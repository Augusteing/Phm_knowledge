# -*- coding: utf-8 -*-
"""验证 元数据(论文/作者/发表单位/发表时间 及 撰写/隶属/发表于) 完全由规则注入

思路:
 1. 使用与填充脚本一致的 Title 匹配策略: 归一化后 文件 stem 以 归一化 title 开头 即视为匹配。
 2. 解析聚合元数据文件, 对匹配到的  in_scope  文件计算 期望新增 的 元数据实体 & 关系 数:
      实体: 论文(1) + 作者(n) + 发表单位(m) + 发表时间(1 可选)
      关系: 每作者 -> 论文 (撰写); 若存在首作者与首单位 => 1 条 隶属; 若有 论文 & 时间 => 1 条 发表于
    (与填充脚本 augment_one() 内逻辑保持一致)
 3. 读取 “增补前” 目录(清理后) 与 当前(已注入) 目录：
      - 统计各文件(匹配到元数据的)中 目标实体/关系 类型计数。
 4. 计算: added = current - pre
 5. 对比: added 与 expected 逐类型、逐模型 完全一致 且 pre 全部为 0 => PASS

输出:
  CSV 目录: 指标统计计算/增添元数据前后存在的差异性/结果/元数据规则注入验证汇总_<model>.csv
  汇总汇报: 元数据规则注入验证最终汇总.csv

用法:
  python 验证_元数据规则注入完整性.py --metadata-file <PHM-217...txt> --models deepseek,gemini,kimi

返回码: 0=全部通过, 1=存在不一致
"""
from __future__ import annotations
import argparse, json, re, sys, csv
from pathlib import Path
from typing import Dict, List, Tuple, Any

ROOT = Path(r"e:\知识图谱构建\9.15之前的实验\EXP-1")
PRE_BASE = ROOT / '抽取' / '数据结果' / '增补前'
CUR_BASE = ROOT / '抽取' / '数据结果'
OUT_DIR = ROOT / '指标统计计算' / '增添元数据前后存在的差异性' / '结果'
OUT_DIR.mkdir(parents=True, exist_ok=True)

META_ENTITY_TYPES = ["论文","作者","发表单位","发表时间"]
META_REL_TYPES = ["撰写","隶属","发表于"]

# ---------------- 元数据解析 (复制/简化自 填充脚本) -----------------
RE_TITLE = re.compile(r"(?m)^Title-题名:\s*(.+)")
RE_AUTHOR = re.compile(r"(?m)^Author-作者:\s*(.+)")
RE_ORGAN = re.compile(r"(?m)^Organ-机构:\s*(.+)")
RE_PUB = re.compile(r"(?m)^PubTime-出版时间:\s*(.+)")
RE_RECORD = re.compile(r"(?m)^Title-题名:.*?(?=^Title-题名:|\Z)", re.DOTALL)

def _split_items(s: str) -> List[str]:
    parts = re.split(r"[;；、，,]+", s)
    items = [p.strip() for p in parts if p and p.strip()]
    items = [re.sub(r"^[\-—·•]\s*", "", it) for it in items]
    return items

def parse_metadata(path: Path):
    txt = path.read_text(encoding='utf-8', errors='ignore')
    records = []
    for block in RE_RECORD.findall(txt):
        m_title = RE_TITLE.search(block)
        if not m_title:
            continue
        title = m_title.group(1).strip()
        authors = _split_items(RE_AUTHOR.search(block).group(1)) if RE_AUTHOR.search(block) else []
        orgs = _split_items(RE_ORGAN.search(block).group(1)) if RE_ORGAN.search(block) else []
        pub_time = RE_PUB.search(block).group(1).strip() if RE_PUB.search(block) else ''
        records.append({"title": title, "authors": authors, "orgs": orgs, "pub_time": pub_time})
    return records

def normalize_name(s: str) -> str:
    # 去除空白及常见标点
    return re.sub(r"[\s_\-—:：,，；;·•.!！?？'\"()（）\[\]【】]", "", s).lower()

def build_index(records):
    pairs = []
    for r in records:
        t = r.get('title','')
        if t:
            pairs.append((normalize_name(str(t)), r))
    pairs.sort(key=lambda x: len(x[0]), reverse=True)
    return pairs

def match_meta(file_stem: str, indexed) -> dict|None:
    ns = normalize_name(file_stem)
    for nt, meta in indexed:
        if ns.startswith(nt):
            return meta
    return None

# --------------- JSON 读取 ---------------

def load_json(path: Path):
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None, None
    if isinstance(raw, dict):
        item = raw
    elif isinstance(raw, list) and raw and isinstance(raw[0], dict):
        item = raw[0]
    else:
        return None, None
    ents = item.get('entities') or []
    rels = item.get('relations') or []
    if not isinstance(ents, list) or not isinstance(rels, list):
        return None, None
    return ents, rels

# --------------- 统计函数 ---------------

def count_meta_in_entities(entities) -> Dict[str,int]:
    c = {t:0 for t in META_ENTITY_TYPES}
    for e in entities:
        ty = e.get('type')
        if ty in c:
            c[ty]+=1
    return c

def count_meta_in_relations(relations) -> Dict[str,int]:
    c = {t:0 for t in META_REL_TYPES}
    for r in relations:
        ty = r.get('type') or r.get('relation')
        if ty in c:
            c[ty]+=1
    return c

# expected counts per file

def expected_counts(meta: dict) -> Tuple[Dict[str,int], Dict[str,int]]:
    e = {t:0 for t in META_ENTITY_TYPES}
    r = {t:0 for t in META_REL_TYPES}
    title = meta.get('title') or ''
    authors = meta.get('authors') or []
    orgs = meta.get('orgs') or []
    pub = meta.get('pub_time') or ''
    if title:
        e['论文'] += 1
    for a in authors:
        if a:
            e['作者'] += 1
    for o in orgs:
        if o:
            e['发表单位'] += 1
    if pub:
        e['发表时间'] += 1
    # relations
    for a in authors:
        if a and title:
            r['撰写'] += 1
    if authors and orgs and authors[0] and orgs[0]:
        r['隶属'] += 1
    if title and pub:
        r['发表于'] += 1
    return e, r

# --------------- 主流程 ---------------

def process_model(model: str, indexed, args):
    pre_dir = PRE_BASE / f'提取结果_by_{model}' / 'in_scope'
    cur_dir = CUR_BASE / f'提取结果_by_{model}' / 'in_scope'
    if not cur_dir.exists():
        print(f"[WARN] 当前目录不存在: {cur_dir}")
        return None
    files = sorted(cur_dir.glob('*.json'))
    rows = []
    agg = {
        'expected_entities': {t:0 for t in META_ENTITY_TYPES},
        'expected_relations': {t:0 for t in META_REL_TYPES},
        'pre_entities': {t:0 for t in META_ENTITY_TYPES},
        'pre_relations': {t:0 for t in META_REL_TYPES},
        'cur_entities': {t:0 for t in META_ENTITY_TYPES},
        'cur_relations': {t:0 for t in META_REL_TYPES},
    }
    matched_files = 0
    for f in files:
        meta = match_meta(f.stem, indexed)
        if not meta:
            continue
        matched_files += 1
        exp_e, exp_r = expected_counts(meta)
        for k,v in exp_e.items(): agg['expected_entities'][k]+=v
        for k,v in exp_r.items(): agg['expected_relations'][k]+=v
        ents_cur, rels_cur = load_json(f)
        if ents_cur is None:
            continue
        cur_e = count_meta_in_entities(ents_cur)
        cur_r = count_meta_in_relations(rels_cur)
        for k,v in cur_e.items(): agg['cur_entities'][k]+=v
        for k,v in cur_r.items(): agg['cur_relations'][k]+=v
        # pre snapshot
        pre_file = pre_dir / f.name
        pre_e_c = pre_r_c = {t:0 for t in META_ENTITY_TYPES}, {t:0 for t in META_REL_TYPES}
        if pre_file.exists():
            ents_pre, rels_pre = load_json(pre_file)
            if ents_pre is not None:
                pre_e_c = count_meta_in_entities(ents_pre), count_meta_in_relations(rels_pre)
        pre_e, pre_r = pre_e_c
        for k,v in pre_e.items(): agg['pre_entities'][k]+=v
        for k,v in pre_r.items(): agg['pre_relations'][k]+=v
        rows.append([
            f.name,
            sum(exp_e.values()), sum(exp_r.values()),
            sum(pre_e.values()), sum(pre_r.values()),
            sum(cur_e.values()), sum(cur_r.values())
        ])
    # 写明细
    detail_csv = OUT_DIR / f'元数据规则注入验证明细_{model}.csv'
    with detail_csv.open('w', newline='', encoding='utf-8-sig') as fw:
        w = csv.writer(fw)
        w.writerow(['文件','期望实体数','期望关系数','增补前实体数','增补前关系数','当前实体数','当前关系数'])
        for r in rows:
            w.writerow(r)
    # 汇总结果
    added_entities_total = {t: agg['cur_entities'][t]-agg['pre_entities'][t] for t in META_ENTITY_TYPES}
    added_relations_total = {t: agg['cur_relations'][t]-agg['pre_relations'][t] for t in META_REL_TYPES}
    status = 'PASS'
    reason = ''
    # 条件1: pre 全 0
    if any(agg['pre_entities'][t] for t in META_ENTITY_TYPES) or any(agg['pre_relations'][t] for t in META_REL_TYPES):
        status = 'FAIL'; reason += '增补前存在残留; '
    # 条件2: expected == cur == added
    for t in META_ENTITY_TYPES:
        if not (agg['expected_entities'][t] == agg['cur_entities'][t] == added_entities_total[t]):
            status='FAIL'; reason+=f'实体类型{t}不一致; '
    for t in META_REL_TYPES:
        if not (agg['expected_relations'][t] == agg['cur_relations'][t] == added_relations_total[t]):
            status='FAIL'; reason+=f'关系类型{t}不一致; '
    summary = {
        'model': model,
        'matched_files': matched_files,
        **{f'exp_ent_{t}': agg['expected_entities'][t] for t in META_ENTITY_TYPES},
        **{f'exp_rel_{t}': agg['expected_relations'][t] for t in META_REL_TYPES},
        'exp_ent_total': sum(agg['expected_entities'].values()),
        'exp_rel_total': sum(agg['expected_relations'].values()),
        'cur_ent_total': sum(agg['cur_entities'].values()),
        'cur_rel_total': sum(agg['cur_relations'].values()),
        'status': status,
        'reason': reason.strip(),
    }
    return summary


def main():
    ap = argparse.ArgumentParser(description='验证元数据规则注入完整性')
    ap.add_argument('--metadata-file', required=True, help='聚合元数据文件路径')
    ap.add_argument('--models', default='deepseek,gemini,kimi', help='模型列表')
    args = ap.parse_args()

    meta_path = Path(args.metadata_file)
    if not meta_path.exists():
        print('[ERROR] metadata file not found')
        sys.exit(2)

    records = parse_metadata(meta_path)
    indexed = build_index(records)
    models = [m.strip() for m in args.models.split(',') if m.strip()]
    summaries = []
    for m in models:
        s = process_model(m, indexed, args)
        if s:
            summaries.append(s)
    # 写汇总
    out_csv = OUT_DIR / '元数据规则注入验证最终汇总.csv'
    with out_csv.open('w', newline='', encoding='utf-8-sig') as fw:
        w = csv.writer(fw)
        header = ['模型','匹配文件数','exp_实体_论文','exp_实体_作者','exp_实体_发表单位','exp_实体_发表时间','exp_实体总','exp_关系_撰写','exp_关系_隶属','exp_关系_发表于','exp_关系总','cur_实体总','cur_关系总','状态','备注']
        w.writerow(header)
        for s in summaries:
            w.writerow([
                s['model'], s['matched_files'], s['exp_ent_论文'], s['exp_ent_作者'], s['exp_ent_发表单位'], s['exp_ent_发表时间'], s['exp_ent_total'],
                s['exp_rel_撰写'], s['exp_rel_隶属'], s['exp_rel_发表于'], s['exp_rel_total'], s['cur_ent_total'], s['cur_rel_total'], s['status'], s['reason']
            ])
    print('[INFO] 汇总写出:', out_csv)
    failed = [s for s in summaries if s['status']!='PASS']
    if failed:
        print('[RESULT] 验证未通过:')
        for f in failed:
            print('  -', f['model'], f['reason'])
        sys.exit(1)
    else:
        print('[RESULT] 所有模型 PASS: 元数据实体与关系完全由规则注入且数量匹配 (期望==当前==新增)')
        sys.exit(0)

if __name__ == '__main__':
    main()
