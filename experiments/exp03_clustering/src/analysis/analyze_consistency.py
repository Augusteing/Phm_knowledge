# -*- coding: utf-8 -*-
"""
一致性分析脚本（适配 EXP 输出结构，支持实验一/二/三复用）

输入目录（相对 outputs 根目录）：
    outputs/extractions/consistency/
    ├── 1/
    │   ├── deepseek/ 或 deepseek_rag/
    │   ├── gemini/   或 gemini_rag/
    │   └── kimi/     或 kimi_rag/
    ├── 2/
    └── 3/

输出目录（与其它分析脚本一致）：
    outputs/analysis/consistency/
    ├── consistency_summary.md
    ├── deepseek/paper_consistency.csv
    ├── gemini/paper_consistency.csv
    └── kimi/paper_consistency.csv

指标定义（基础版）：
    - 实体集合一致性（Jaccard 平均）：同一论文跨多次运行的实体集合成对 Jaccard 相似度的平均值
    - 关系集合一致性（Jaccard 平均）：同上
    - 规模稳定性（CV）：实体数、关系数在多次运行间的变异系数（std/mean）

健壮性：
    - JSON 键名做兼容提取；少于 2 次运行的论文，Jaccard/CV 记为 NA。
    - 自动识别 deepseek/deepseek_rag 等子目录命名；递归扫描，并排除日志与 *_evaluated.json。
"""

from __future__ import annotations

import os
import json
import math
import argparse
from pathlib import Path
from itertools import combinations
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any

import pandas as pd

# 实验根目录（当前脚本所在实验目录）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def resolve_outputs_root(cli_outputs_dir: str | None) -> Path:
    if cli_outputs_dir:
        return Path(cli_outputs_dir).resolve()
    return PROJECT_ROOT / "outputs"

# 可接受的模型子目录命名（将按前缀匹配）
MODEL_DIR_HINTS = {
    "deepseek": ["deepseek", "deepseek_rag"],
    "gemini": ["gemini", "gemini_rag"],
    "kimi": ["kimi", "kimi_rag"],
}


def norm_text(x: Any) -> str:
    if x is None:
        return ""
    s = str(x).strip().lower()
    # 可拓展：全角半角、特殊空格
    return " ".join(s.split())


def entity_key(ent: dict) -> str:
    name = ent.get("name") or ent.get("entity") or ent.get("text")
    etype = ent.get("type") or ent.get("entity_type") or ent.get("category")
    return f"{norm_text(name)}::{norm_text(etype)}"


def relation_key(rel: dict) -> str:
    # 兼容不同字段命名
    src_name = rel.get("source_name") or rel.get("source") or rel.get("from")
    src_type = rel.get("source_type") or rel.get("from_type") or rel.get("sourceEntityType")
    tgt_name = rel.get("target_name") or rel.get("target") or rel.get("to")
    tgt_type = rel.get("target_type") or rel.get("to_type") or rel.get("targetEntityType")
    rtype = rel.get("type") or rel.get("relation") or rel.get("relation_type")
    return f"{norm_text(src_name)}::{norm_text(src_type)}->{norm_text(rtype)}->{norm_text(tgt_name)}::{norm_text(tgt_type)}"


def load_json_safely(p: Path) -> dict | None:
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def extract_sets_from_file(p: Path) -> Tuple[Set[str], Set[str], int, int]:
    data = load_json_safely(p)
    if not isinstance(data, dict):
        return set(), set(), 0, 0
    ents = data.get("entities") or []
    rels = data.get("relations") or []
    ent_set = set()
    for e in ents:
        try:
            ent_set.add(entity_key(e))
        except Exception:
            continue
    rel_set = set()
    for r in rels:
        try:
            rel_set.add(relation_key(r))
        except Exception:
            continue
    return ent_set, rel_set, len(ents) if isinstance(ents, list) else 0, len(rels) if isinstance(rels, list) else 0


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    if union == 0:
        return 1.0
    return inter / union


def coeff_variation(values: List[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    if mean == 0:
        return None
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    std = math.sqrt(var)
    return std / mean


def _find_model_dirs(run_dir: Path, model_key: str) -> List[Path]:
    """在 run_dir 下查找与 model_key 匹配的子目录，支持 deepseek/deepseek_rag 等变体。"""
    results: List[Path] = []
    if not run_dir.exists():
        return results
    hints = MODEL_DIR_HINTS.get(model_key, [model_key])
    for child in run_dir.iterdir():
        if not child.is_dir():
            continue
        name = child.name.lower()
        if any(name.startswith(h) for h in hints):
            results.append(child)
    return results

def scan_run_files(run_dir: Path, model_key: str) -> Dict[str, Path]:
    """扫描单次运行中某模型的所有论文结果文件，返回 {paper_id: path}。
    - 自动识别模型子目录（deepseek 与 deepseek_rag 等）
    - 递归 rglob，过滤日志与 *_evaluated.json
    """
    results: Dict[str, Path] = {}
    model_dirs = _find_model_dirs(run_dir, model_key)
    for base in model_dirs:
        for p in base.rglob("*.json"):
            name_lower = p.name.lower()
            if "log" in name_lower:
                continue
            if name_lower.endswith("_evaluated.json"):
                continue
            paper = p.stem
            # 若同名出现多次，后出现的覆盖前一个（一般不冲突）
            results[paper] = p
    return results


def analyze_model(model_key: str, runs: List[Path]) -> pd.DataFrame:
    # 收集每次运行的文件映射
    run_maps: List[Dict[str, Path]] = [scan_run_files(r, model_key) for r in runs]

    # 汇总所有论文ID
    all_papers: Set[str] = set()
    for m in run_maps:
        all_papers.update(m.keys())

    rows = []
    for paper in sorted(all_papers):
        ent_sets: List[Set[str]] = []
        rel_sets: List[Set[str]] = []
        ent_counts: List[int] = []
        rel_counts: List[int] = []
        used_runs = 0

        for m in run_maps:
            path = m.get(paper)
            if not path:
                continue
            ent_set, rel_set, ec, rc = extract_sets_from_file(path)
            ent_sets.append(ent_set)
            rel_sets.append(rel_set)
            ent_counts.append(ec)
            rel_counts.append(rc)
            used_runs += 1

        # 计算平均 pairwise Jaccard
        def avg_pairwise_jacc(sets: List[Set[str]]) -> float | None:
            if len(sets) < 2:
                return None
            vals = []
            for a, b in combinations(sets, 2):
                vals.append(jaccard(a, b))
            return sum(vals) / len(vals) if vals else None

        ent_j = avg_pairwise_jacc(ent_sets)
        rel_j = avg_pairwise_jacc(rel_sets)
        ecv = coeff_variation(ent_counts)
        rcv = coeff_variation(rel_counts)

        rows.append({
            "paper": paper,
            "runs": used_runs,
            "entity_jaccard": None if ent_j is None else round(ent_j, 4),
            "relation_jaccard": None if rel_j is None else round(rel_j, 4),
            "entities_cv": None if ecv is None else round(ecv, 4),
            "relations_cv": None if rcv is None else round(rcv, 4),
            "avg_entities": round(sum(ent_counts) / used_runs, 2) if used_runs else None,
            "avg_relations": round(sum(rel_counts) / used_runs, 2) if used_runs else None,
        })

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="抽取结果一致性分析")
    parser.add_argument(
        "--outputs-dir",
        help="覆盖 outputs 根目录（默认使用当前实验目录下的 outputs）",
        default=None,
    )
    args = parser.parse_args()

    outputs_root = resolve_outputs_root(args.outputs_dir)
    consistency_base = outputs_root / "extractions" / "consistency"
    print("=" * 80)
    print("🔁 抽取结果一致性分析")
    print("=" * 80)

    # 收集有效的运行目录（数字命名）
    if not consistency_base.exists():
        print(f"❌ 未找到目录: {consistency_base}")
        return

    runs = [d for d in consistency_base.iterdir() if d.is_dir() and d.name.isdigit()]
    runs.sort(key=lambda p: int(p.name))
    print(f"发现运行次数: {len(runs)} -> {[p.name for p in runs]}")

    output_dir = outputs_root / "analysis" / "consistency"
    output_dir.mkdir(parents=True, exist_ok=True)

    model_summaries = []
    for model_key in ["deepseek", "gemini", "kimi"]:
        df = analyze_model(model_key, runs)
        model_dir = output_dir / model_key
        model_dir.mkdir(parents=True, exist_ok=True)
        out_csv = model_dir / "paper_consistency.csv"
        df.to_csv(out_csv, index=False, encoding="utf-8-sig")
        print(f"   ✅ {model_key} 结果已保存: {out_csv}")

        # 统计汇总（忽略 NA）
        def safe_mean(series: pd.Series) -> float | None:
            s = series.dropna()
            return round(s.mean(), 4) if len(s) else None

        summary = {
            "模型": model_key,
            "论文数": len(df),
            "平均实体Jaccard": safe_mean(df["entity_jaccard"]) if not df.empty else None,
            "平均关系Jaccard": safe_mean(df["relation_jaccard"]) if not df.empty else None,
            "实体数CV(均值)": safe_mean(df["entities_cv"]) if not df.empty else None,
            "关系数CV(均值)": safe_mean(df["relations_cv"]) if not df.empty else None,
        }
        model_summaries.append(summary)

    # 生成汇总 Markdown
    md_file = output_dir / "consistency_summary.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# 抽取结果一致性分析报告\n\n")
        f.write(f"运行目录: `{consistency_base}`\n\n")
        f.write(f"共发现 {len(runs)} 次运行: {', '.join(p.name for p in runs)}\n\n")

        if model_summaries:
            f.write("## 模型级汇总\n\n")
            headers = ["模型", "论文数", "平均实体Jaccard", "平均关系Jaccard", "实体数CV(均值)", "关系数CV(均值)"]
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("|" + "|".join(["---"] * len(headers)) + "|\n")
            for s in model_summaries:
                row = [
                    s["模型"],
                    s["论文数"],
                    s["平均实体Jaccard"],
                    s["平均关系Jaccard"],
                    s["实体数CV(均值)"],
                    s["关系数CV(均值)"],
                ]
                f.write("| " + " | ".join("" if v is None else str(v) for v in row) + " |\n")
            f.write("\n")

        f.write("## 文件结构\n\n")
        f.write("```\n")
        f.write("outputs/analysis/consistency/\n")
        f.write("├── consistency_summary.md\n")
        f.write("├── deepseek/paper_consistency.csv\n")
        f.write("├── gemini/paper_consistency.csv\n")
        f.write("└── kimi/paper_consistency.csv\n")
        f.write("```\n\n")

        f.write("## 指标说明\n\n")
        f.write("- 实体/关系 Jaccard: 跨运行的集合相似度（成对平均），越高越稳定\n")
        f.write("- 实体数/关系数 CV: 规模波动（std/mean），越低越稳定\n")
        f.write("- runs 列示该论文实际参与统计的运行次数（缺失会自动跳过）\n")

    print(f"\n✅ 汇总报告已保存: {md_file}")


if __name__ == "__main__":
    main()
