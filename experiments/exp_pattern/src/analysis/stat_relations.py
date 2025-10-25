#!/usr/bin/env python3
"""
统计 result 目录中每个 JSON 文件的 subject/object 出现次数以及 relation 的种类数量。

输出到 experiments/exp_pattern/output/analysis/statistics，包含：
- summary.json: 汇总数字
- summary.md: 可读的简要报告
- relation_counts.csv: 每种 relation 的出现次数明细

用法:
    python stat_relations.py --results-dir ../result --output-dir ../../output/analysis/statistics

"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable


def iter_json_files(results_dir: Path) -> Iterable[Path]:
    for p in sorted(results_dir.glob('*.json')):
        yield p


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"跳过文件 {path}，解析失败: {e}")
        return None


def normalize_items(data: Any) -> Iterable[Dict[str, Any]]:
    """把各种可能的顶层 JSON 结构归一化为可迭代的项(dict)序列。

    常见情况：
    - 顶层就是 list -> 每个元素为一条三元组/实体字典
    - 顶层为 dict 且包含键 'entities' 或 'relations' -> 返回该值中的元素
    - 顶层为单个 dict 且直接为一条记录 -> 返回 [dict]
    """
    if data is None:
        return []
    if isinstance(data, list):
        # 平坦的列表：可能是若干三元组
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        # 如果包含 'entities' 或 'relations'，优先返回其内容
        if 'entities' in data and isinstance(data['entities'], list):
            return [item for item in data['entities'] if isinstance(item, dict)]
        if 'relations' in data and isinstance(data['relations'], list):
            return [item for item in data['relations'] if isinstance(item, dict)]
        # 否则把 dict 作为单条记录返回
        return [data]
    # 其他类型，忽略
    return []


def analyze(results_dir: Path) -> Dict[str, Any]:
    total_subjects = 0
    total_objects = 0
    unique_subjects = set()
    unique_objects = set()
    relation_counter: Counter = Counter()
    files_processed = 0
    files_skipped = 0

    for path in iter_json_files(results_dir):
        data = load_json(path)
        if data is None:
            files_skipped += 1
            continue
        items = list(normalize_items(data))
        if not items:
            # nothing to count
            files_skipped += 1
            continue
        files_processed += 1
        for item in items:
            # item is expected to be a dict with keys like 'subject','object','relation'
            subj = item.get('subject') or item.get('subject_name')
            obj = item.get('object') or item.get('object_name')
            rel = item.get('relation') or item.get('predicate')

            if subj:
                total_subjects += 1
                unique_subjects.add(str(subj))
            if obj:
                total_objects += 1
                unique_objects.add(str(obj))
            if rel:
                relation_counter[str(rel)] += 1

    summary = {
        'files_processed': files_processed,
        'files_skipped_or_empty': files_skipped,
        'total_subject_occurrences': total_subjects,
        'total_object_occurrences': total_objects,
        'unique_subject_count': len(unique_subjects),
        'unique_object_count': len(unique_objects),
        'relation_types_count': len(relation_counter),
        'top_relations': relation_counter.most_common(30),
    }

    return {'summary': summary, 'relation_counts': dict(relation_counter)}


def write_outputs(report: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_path = out_dir / f'summary_{ts}.json'
    md_path = out_dir / f'summary_{ts}.md'
    csv_path = out_dir / f'relation_counts_{ts}.csv'

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    # Markdown 简要报告
    s = report['summary']
    md_lines = [
        f"# Extraction Statistics ({ts})",
        "",
        f"- 处理文件数: {s['files_processed']}",
        f"- 跳过或空文件数: {s['files_skipped_or_empty']}",
        f"- subject 总出现次数: {s['total_subject_occurrences']}",
        f"- object 总出现次数: {s['total_object_occurrences']}",
        f"- 不重复 subject 数量: {s['unique_subject_count']}",
        f"- 不重复 object 数量: {s['unique_object_count']}",
        f"- relation 种类数量: {s['relation_types_count']}",
        "",
        "## Top relations",
        "",
    ]
    for rel, cnt in s['top_relations']:
        md_lines.append(f"- {rel}: {cnt}")

    md_path.write_text('\n'.join(md_lines), encoding='utf-8')

    # CSV of all relation counts
    lines = ["relation,count"]
    for rel, cnt in sorted(report['relation_counts'].items(), key=lambda x: -x[1]):
        # escape quotes
        rel_escaped = str(rel).replace('"', '""')
        lines.append(f'"{rel_escaped}",{cnt}')
    csv_path.write_text('\n'.join(lines), encoding='utf-8')

    print(f"写出: {json_path}\n写出: {md_path}\n写出: {csv_path}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='统计 result 目录中 subject/object/relation')
    p.add_argument('--results-dir', type=Path, default=Path(__file__).resolve().parents[2] / 'result',
                   help='存放 JSON 结果的目录')
    p.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[2] / 'output' / 'analysis' / 'statistics',
                   help='输出统计结果目录')
    return p.parse_args()


def main() -> None:
    args = parse_args()
    results_dir: Path = args.results_dir
    out_dir: Path = args.output_dir

    if not results_dir.exists():
        print(f"结果目录不存在: {results_dir}")
        return

    report = analyze(results_dir)
    write_outputs(report, out_dir)


if __name__ == '__main__':
    main()
