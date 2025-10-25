# -*- coding: utf-8 -*-
"""审计脚本：分析元数据补充对各模型 in_scope JSON 的影响。

输出：
  抽取/数据结果/元数据补充审计/metadata_audit_summary.csv  (总体汇总)
  抽取/数据结果/元数据补充审计/<model>_details.csv        (逐文件详情)

统计内容：
  - 每文件：是否匹配到元数据；候选论文题名；作者数/机构数/是否有出版时间
  - 期望新增实体数 (1 + 作者数 + 机构数 + (1 if pub_time else 0))
  - 其中已有实体数 / 缺失实体数（依据 text+type 匹配）
  - 同理关系：撰写关系数 (作者数), 隶属(0/1), 发表(0/1) -> 期待总关系数；现有关系中已存在与缺失
  - 记录文件中当前实体类型总数（unique types）
  - 标记四种元数据类型是否存在：论文/作者/发表单位/发表时间

使用：
  python 抽取\code\填充脚本\审计_元数据补充影响.py --metadata-file "E:/知识图谱构建/文献信息/PHM-217篇摘要.txt"

备注：无需元数据补充前的快照，通过再次匹配候选实体/关系判断哪些当初是"新加"或原本就存在；这可解释不同模型新增数量不一致的原因（部分已被抽取模型自身识别）。
"""
from __future__ import annotations
import csv
import json
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

# 与填充脚本保持一致的解析逻辑 -----------------
RE_TITLE = re.compile(r"(?m)^Title-题名:\s*(.+)")
RE_AUTHOR = re.compile(r"(?m)^Author-作者:\s*(.+)")
RE_ORGAN = re.compile(r"(?m)^Organ-机构:\s*(.+)")
RE_PUB = re.compile(r"(?m)^PubTime-出版时间:\s*(.+)")
RE_RECORD = re.compile(r"(?m)^Title-题名:.*?(?=^Title-题名:|\Z)", re.DOTALL)

META_TYPES = ["论文", "作者", "发表单位", "发表时间"]


def parse_metadata_file(path: Path) -> List[Dict[str, object]]:
    text = path.read_text(encoding='utf-8', errors='ignore')
    out = []
    for block in RE_RECORD.findall(text):
        t_m = RE_TITLE.search(block)
        if not t_m:
            continue
        title = t_m.group(1).strip()
        authors = RE_AUTHOR.search(block)
        orgs = RE_ORGAN.search(block)
        pub = RE_PUB.search(block)
        def split(s: str|None):
            if not s: return []
            parts = re.split(r"[;；、，,]+", s)
            items = [p.strip() for p in parts if p.strip()]
            items = [re.sub(r"^[\-—·•]\s*", "", it) for it in items]
            return items
        out.append({
            'title': title,
            'authors': split(authors.group(1) if authors else None),
            'orgs': split(orgs.group(1) if orgs else None),
            'pub_time': pub.group(1).strip() if pub else ''
        })
    return out


def normalize_name(s: str) -> str:
    return re.sub(r"[\s_\-—:：,，；;·•.!！?？'""()（）\[\]【】]", "", s).lower()


def build_meta_index(metas: List[Dict[str, object]]):
    pairs = []
    for m in metas:
        t = str(m.get('title',''))
        if t:
            pairs.append((normalize_name(t), m))
    pairs.sort(key=lambda x: len(x[0]), reverse=True)
    return pairs


def find_meta_for_stem(stem: str, indexed) -> Dict[str,object] | None:
    ns = normalize_name(stem)
    for nt, meta in indexed:
        if ns.startswith(nt):
            return meta
    return None


def load_json_any(path: Path):
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


def audit_model(model: str, json_dir: Path, indexed, details_dir: Path) -> Dict[str, object]:
    json_files = sorted(json_dir.glob('*.json'))
    rows = []
    total_expected_entities = total_present_entities = 0
    total_expected_relations = total_present_relations = 0
    matched_files = 0
    type_set = set()
    missing_meta_files = 0

    for jp in json_files:
        ents, rels = load_json_any(jp)
        if ents is None:
            continue
        for e in ents:
            ty = e.get('type')
            if isinstance(ty, str):
                type_set.add(ty)
        meta = find_meta_for_stem(jp.stem, indexed)
        if not meta:
            missing_meta_files += 1
            rows.append([
                jp.name, 0, '', 0,0,0,0,0,0,0,0,0,0, len(set(e.get('type') for e in ents if isinstance(e, dict))), '', '', '', '',
            ])
            continue
        matched_files += 1
        title = str(meta.get('title',''))
        authors = list(meta.get('authors', []))
        orgs = list(meta.get('orgs', []))
        pub_time = str(meta.get('pub_time',''))

        # Expected entities
        expected_entities = 1 + len(authors) + len(orgs) + (1 if pub_time else 0)
        # Build sets
        ent_set = {( (e.get('text','') or '').strip().lower(), e.get('type','') ) for e in ents if isinstance(e, dict)}
        present_entities = 0
        # Title
        if (title.strip().lower(), '论文') in ent_set: present_entities += 1
        for a in authors:
            if (a.strip().lower(), '作者') in ent_set: present_entities += 1
        for o in orgs:
            if (o.strip().lower(), '发表单位') in ent_set: present_entities += 1
        if pub_time and (pub_time.strip().lower(), '发表时间') in ent_set: present_entities += 1

        # Expected relations
        expected_relations = len(authors)  # 撰写
        if authors and orgs and authors[0] and orgs[0]: expected_relations += 1  # 隶属
        if title and pub_time: expected_relations += 1  # 发表于

        rel_key_set = {(r.get('head','').strip(), r.get('tail','').strip(), r.get('type','')) for r in rels if isinstance(r, dict)}
        present_relations = 0
        for a in authors:
            if (a, title, '撰写') in rel_key_set: present_relations += 1
        if authors and orgs and authors[0] and orgs[0] and (authors[0], orgs[0], '隶属') in rel_key_set:
            present_relations += 1
        if title and pub_time and (title, pub_time, '发表于') in rel_key_set:
            present_relations += 1

        rows.append([
            jp.name, 1, title, len(authors), len(orgs), 1 if pub_time else 0,
            expected_entities, present_entities, expected_entities - present_entities,
            expected_relations, present_relations, expected_relations - present_relations,
            len(type_set),
            int('论文' in type_set), int('作者' in type_set), int('发表单位' in type_set), int('发表时间' in type_set),
        ])

        total_expected_entities += expected_entities
        total_present_entities += present_entities
        total_expected_relations += expected_relations
        total_present_relations += present_relations

    # 写详情
    details_dir.mkdir(parents=True, exist_ok=True)
    detail_path = details_dir / f"{model}_details.csv"
    with detail_path.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow([
            '文件','是否匹配元数据','题名','作者数','机构数','有发表时间','期望元数据实体数','已存在元数据实体数','缺失元数据实体数',
            '期望元数据关系数','已存在元数据关系数','缺失元数据关系数','当前实体type总数',
            '含type_论文','含type_作者','含type_发表单位','含type_发表时间'
        ])
        w.writerows(rows)

    return {
        'model': model,
        'files_total': len(json_files),
        'files_with_meta': matched_files,
        'files_without_meta': missing_meta_files,
        'type_count': len(type_set),
        'has_论文': int('论文' in type_set),
        'has_作者': int('作者' in type_set),
        'has_发表单位': int('发表单位' in type_set),
        'has_发表时间': int('发表时间' in type_set),
        'expected_entities_total': total_expected_entities,
        'present_entities_total': total_present_entities,
        'missing_entities_total': total_expected_entities - total_present_entities,
        'expected_relations_total': total_expected_relations,
        'present_relations_total': total_present_relations,
        'missing_relations_total': total_expected_relations - total_present_relations,
    }


def main():
    parser = argparse.ArgumentParser(description='审计元数据补充影响')
    parser.add_argument('--metadata-file', required=True, help='聚合元数据 txt 文件路径')
    parser.add_argument('--models', default='deepseek,gemini,kimi', help='模型列表')
    args = parser.parse_args()

    meta_path = Path(args.metadata_file)
    metas = parse_metadata_file(meta_path)
    indexed = build_meta_index(metas)

    extract_root = Path(__file__).resolve().parents[2]  # 抽取 目录
    data_base = extract_root / '数据结果'
    out_dir = data_base / '元数据补充审计'
    out_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    for model in [m.strip() for m in args.models.split(',') if m.strip()]:
        json_dir = data_base / f'提取结果_by_{model}' / 'in_scope'
        if not json_dir.exists():
            print(f'[WARN] 模型目录不存在: {json_dir}')
            continue
        print(f'[审计] 模型 {model} ...')
        summary = audit_model(model, json_dir, indexed, out_dir)
        summaries.append(summary)

    # 汇总表
    sum_path = out_dir / 'metadata_audit_summary.csv'
    with sum_path.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow([
            '模型','JSON文件数','匹配元数据文件数','未匹配文件数','实体type数量','含论文','含作者','含发表单位','含发表时间',
            '期望元数据实体总数','已存在元数据实体总数','缺失元数据实体总数',
            '期望元数据关系总数','已存在元数据关系总数','缺失元数据关系总数'
        ])
        for s in summaries:
            w.writerow([
                s['model'], s['files_total'], s['files_with_meta'], s['files_without_meta'], s['type_count'],
                s['has_论文'], s['has_作者'], s['has_发表单位'], s['has_发表时间'],
                s['expected_entities_total'], s['present_entities_total'], s['missing_entities_total'],
                s['expected_relations_total'], s['present_relations_total'], s['missing_relations_total']
            ])
    print('[完成] 写出审计汇总:', sum_path)

if __name__ == '__main__':
    main()
