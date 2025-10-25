import re
import json
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Iterable

# ------------------ 配置 ------------------
DEFAULT_METADATA_FILE = Path(r"E:\知识图谱构建\文献信息\PHM-217篇摘要.txt")
TARGET_MODELS = ["deepseek", "gemini", "kimi"]  # 需要填充的抽取模型


# ------------------ 元数据解析 ------------------
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


def parse_metadata_file(path: Path) -> List[Dict[str, object]]:
    """解析聚合元数据文件，返回每篇的 dict。
    允许文件中包含 200+ 记录；通过 Title-题名 作为分隔。
    """
    if not path.exists():
        raise FileNotFoundError(f"元数据文件不存在: {path}")
    text = path.read_text(encoding="utf-8", errors="ignore")
    records = []
    for block in RE_RECORD.findall(text):
        title_m = RE_TITLE.search(block)
        if not title_m:
            continue
        title = title_m.group(1).strip()
        authors_m = RE_AUTHOR.search(block)
        orgs_m = RE_ORGAN.search(block)
        pub_m = RE_PUB.search(block)
        authors = _split_items(authors_m.group(1)) if authors_m else []
        orgs = _split_items(orgs_m.group(1)) if orgs_m else []
        pub_time = pub_m.group(1).strip() if pub_m else ""
        if title:
            records.append({
                "title": title,
                "authors": authors,
                "orgs": orgs,
                "pub_time": pub_time,
            })
    return records


def normalize_name(s: str) -> str:
    return re.sub(r"[\s_\-—:：,，；;·•.!！?？'""()（）\[\]【】]", "", s).lower()


def build_meta_index(metas: List[Dict[str, object]]):
    # 返回按 normalized title 长度降序的元组列表 (norm_title, meta)
    pairs = []
    for m in metas:
        t = str(m.get("title", ""))
        if not t:
            continue
        pairs.append((normalize_name(t), m))
    # 更长的标题优先匹配
    pairs.sort(key=lambda x: len(x[0]), reverse=True)
    return pairs


def find_meta_for_stem(stem: str, indexed_metas: List[Tuple[str, Dict[str, object]]]) -> Optional[Dict[str, object]]:
    norm_stem = normalize_name(stem)
    for norm_title, meta in indexed_metas:
        if norm_stem.startswith(norm_title):
            return meta
    return None


def dedup_entities(entities: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen: set[Tuple[str, str]] = set()
    result: List[Dict[str, str]] = []
    for e in entities:
        t = e.get("text", "").strip()
        ty = e.get("type", "").strip()
        key = (t.lower(), ty)
        if key in seen:
            continue
        seen.add(key)
        result.append({"text": t, "type": ty})
    return result


def dedup_relations(relations: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen: set[Tuple[str, str, str]] = set()
    result: List[Dict[str, str]] = []
    for r in relations:
        head = r.get("head", "").strip()
        tail = r.get("tail", "").strip()
        ty = r.get("type", "").strip()
        key = (head, tail, ty)
        if key in seen:
            continue
        seen.add(key)
        result.append({"head": head, "tail": tail, "type": ty})
    return result


def augment_one(json_path: Path, meta: Dict[str, object]) -> bool:
    """将 meta 中元信息追加到指定 JSON。
    支持两种结构：
      1) 顶层 dict: { entities: [...], relations: [...] }
      2) 顶层 list 且第一个元素为 dict（早期格式）
    返回 True 表示内容有新增并写回。
    """
    try:
        raw = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] 读取失败 {json_path.name}: {e}")
        return False

    if isinstance(raw, dict):
        item = raw
        container = raw
    elif isinstance(raw, list) and raw and isinstance(raw[0], dict):
        item = raw[0]
        container = raw
    else:
        print(f"[WARN] 不支持的结构: {json_path}")
        return False

    entities = item.get("entities") or []
    relations = item.get("relations") or []
    if not isinstance(entities, list) or not isinstance(relations, list):
        print(f"[WARN] entities/relations 非列表: {json_path}")
        return False

    title: str = str(meta.get("title", ""))
    authors: List[str] = meta.get("authors", [])  # type: ignore
    orgs: List[str] = meta.get("orgs", [])  # type: ignore
    pub_time: str = str(meta.get("pub_time", ""))

    add_entities: List[Dict[str, str]] = []
    if title:
        add_entities.append({"type": "论文", "text": title})
    for a in authors:
        if a:
            add_entities.append({"type": "作者", "text": a})
    for o in orgs:
        if o:
            add_entities.append({"type": "发表单位", "text": o})
    if pub_time:
        add_entities.append({"type": "发表时间", "text": pub_time})

    add_relations: List[Dict[str, str]] = []
    for a in authors:
        if a and title:
            add_relations.append({"type": "撰写", "head": a, "tail": title})
    if authors and orgs and authors[0] and orgs[0]:
        add_relations.append({"type": "隶属", "head": authors[0], "tail": orgs[0]})
    if title and pub_time:
        add_relations.append({"type": "发表于", "head": title, "tail": pub_time})

    entities_extended = dedup_entities(entities + add_entities)
    relations_extended = dedup_relations(relations + add_relations)
    if len(entities_extended) == len(entities) and len(relations_extended) == len(relations):
        return False
    item["entities"] = entities_extended
    item["relations"] = relations_extended
    json_path.write_text(json.dumps(container, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="将聚合元数据填充到各模型 in_scope JSON")
    parser.add_argument("--metadata-file", default=str(DEFAULT_METADATA_FILE), help="聚合元数据 txt 路径")
    parser.add_argument("--models", default=",".join(TARGET_MODELS), help="需要处理的模型列表，逗号分隔")
    parser.add_argument("--dry-run", action="store_true", help="不写入，仅统计将发生的修改数")
    parser.add_argument("--limit", type=int, default=0, help="每模型最多处理 JSON 数 (0=不限)")
    args = parser.parse_args()

    meta_file = Path(args.metadata_file)
    models = [m.strip() for m in args.models.split(',') if m.strip()]
    if not models:
        print("[ERROR] 未提供模型名称")
        return

    # 计算 抽取 根目录：当前文件位于 抽取/code/填充脚本
    extract_root = Path(__file__).resolve().parents[2]  # 抽取 目录
    data_base = extract_root / "数据结果"

    print(f"[信息] 元数据文件: {meta_file}")
    metas = parse_metadata_file(meta_file)
    print(f"[信息] 解析得到元数据记录: {len(metas)} 条")
    if not metas:
        print("[ERROR] 没有解析到任何记录，退出。")
        return
    indexed = build_meta_index(metas)

    total_updated = 0
    total_skipped_no_meta = 0
    total_unchanged = 0

    for model in models:
        json_dir = data_base / f"提取结果_by_{model}" / "in_scope"
        if not json_dir.exists():
            print(f"[警告] 模型 {model} 目录不存在: {json_dir}")
            continue
        json_files = sorted(json_dir.glob("*.json"))
        if args.limit > 0:
            json_files = json_files[: args.limit]
        print(f"[模型 {model}] 待处理 JSON 数: {len(json_files)} (目录: {json_dir})")

        m_updated = m_no_meta = m_unchanged = 0
        for jp in json_files:
            meta = find_meta_for_stem(jp.stem, indexed)
            if not meta:
                m_no_meta += 1
                continue
            if args.dry_run:
                # 预检：读取并模拟是否会变更
                try:
                    raw = json.loads(jp.read_text(encoding='utf-8'))
                except Exception:
                    m_unchanged += 1
                    continue
                if isinstance(raw, dict):
                    ents = raw.get('entities') or []
                    rels = raw.get('relations') or []
                elif isinstance(raw, list) and raw and isinstance(raw[0], dict):
                    ents = raw[0].get('entities') or []
                    rels = raw[0].get('relations') or []
                else:
                    m_unchanged += 1
                    continue
                before_e, before_r = len(ents), len(rels)
                # 粗略估计新增数
                candidate_e = set((e.get('text','').strip().lower(), e.get('type','')) for e in ents)
                # 论文
                title = str(meta.get('title',''))
                if title:
                    candidate_e.add((title.strip().lower(), '论文'))
                for a in meta.get('authors', []):  # type: ignore
                    if a:
                        candidate_e.add((str(a).strip().lower(), '作者'))
                for o in meta.get('orgs', []):  # type: ignore
                    if o:
                        candidate_e.add((str(o).strip().lower(), '发表单位'))
                pub = str(meta.get('pub_time',''))
                if pub:
                    candidate_e.add((pub.strip().lower(), '发表时间'))
                if len(candidate_e) > before_e:
                    m_updated += 1  # 计作将要更新
                else:
                    m_unchanged += 1
                continue

            changed = augment_one(jp, meta)
            if changed:
                m_updated += 1
            else:
                # 有元数据但没有实际新增（可能之前已加过）
                m_unchanged += 1

        total_updated += m_updated
        total_skipped_no_meta += m_no_meta
        total_unchanged += m_unchanged
        print(f"[模型 {model}] 新增/更新 {m_updated}，缺少元数据 {m_no_meta}，已存在/未变化 {m_unchanged}")

    mode = "DRY-RUN" if args.dry_run else "WRITE"
    print(f"[汇总 {mode}] 更新 {total_updated}，未匹配元数据 {total_skipped_no_meta}，未变化 {total_unchanged}")


if __name__ == "__main__":
    main()
