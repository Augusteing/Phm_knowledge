# -*- coding: utf-8 -*-
"""
RAG 模型结果对比分析脚本
统计 DeepSeek、Gemini、Kimi 三个模型的抽取结果
生成对比表格和可视化图表
"""
import os
import json
import argparse
from pathlib import Path
from collections import defaultdict
import pandas as pd
from datetime import datetime

# ------------------------------
# 路径配置
# ------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # .../exp01_baseline

def resolve_outputs_root(cli_outputs_dir: str | None) -> Path:
    if cli_outputs_dir:
        return Path(cli_outputs_dir).resolve()
    return PROJECT_ROOT / "outputs"

def ensure_output_dir(outputs_root: Path) -> Path:
    out = outputs_root / "analysis" / "statistics"
    os.makedirs(out, exist_ok=True)
    return out

# ------------------------------
# 数据统计函数
# ------------------------------
def count_json_files(directory: Path) -> dict:
    """统计目录下的JSON文件数量和基本信息"""
    if not directory.exists():
        return {
            "total": 0,
            "success": 0,
            "failed": 0,
            "files": []
        }
    # 递归读取所有子目录
    json_files = list(directory.rglob("*.json"))
    # 失败标记兼容两种：.error.txt 或 .failed.txt
    error_files = list(directory.rglob("*.error.txt")) + list(directory.rglob("*.failed.txt"))
    
    return {
        "total": len(json_files) + len(error_files),
        "success": len(json_files),
        "failed": len(error_files),
        "files": [f.name for f in json_files]
    }

def analyze_json_content(file_path: Path) -> dict:
    """分析单个JSON文件的内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entities = data.get("entities", [])
        relations = data.get("relations", [])
        
        # 统计实体类型分布
        entity_types = defaultdict(int)
        for entity in entities:
            entity_type = entity.get("type", "unknown")
            entity_types[entity_type] += 1
        
        # 统计关系类型分布
        relation_types = defaultdict(int)
        for relation in relations:
            relation_type = relation.get("relation", "unknown")
            relation_types[relation_type] += 1
        
        return {
            "entity_count": len(entities),
            "relation_count": len(relations),
            "entity_type_count": len(entity_types),  # 实体类型数量
            "relation_type_count": len(relation_types),  # 关系类型数量
            "entity_types": dict(entity_types),
            "relation_types": dict(relation_types)
        }
    except Exception as e:
        print(f"⚠️ 分析文件失败 {file_path.name}: {e}")
        return {
            "entity_count": 0,
            "relation_count": 0,
            "entity_type_count": 0,
            "relation_type_count": 0,
            "entity_types": {},
            "relation_types": {}
        }

def analyze_model_results(model_name: str, json_dir: Path, log_dir: Path) -> dict:
    """分析单个模型的所有结果"""
    print(f"\n📊 分析 {model_name} 模型结果...")
    
    # 基本统计
    file_stats = count_json_files(json_dir)
    print(f"   - 成功: {file_stats['success']} 篇")
    print(f"   - 失败: {file_stats['failed']} 篇")
    
    # 详细分析每个JSON文件
    detailed_results = []
    total_entities = 0
    total_relations = 0
    total_entity_types = 0
    total_relation_types = 0
    
    # 用于统计所有论文中的类型（去重）
    all_entity_types = set()
    all_relation_types = set()
    
    for json_file in json_dir.rglob("*.json"):
        paper_name = json_file.stem
        analysis = analyze_json_content(json_file)
        
        detailed_results.append({
            "paper": paper_name,
            "entities": analysis["entity_count"],
            "relations": analysis["relation_count"],
            "entity_types": analysis["entity_type_count"],
            "relation_types": analysis["relation_type_count"]
        })
        
        total_entities += analysis["entity_count"]
        total_relations += analysis["relation_count"]
        total_entity_types += analysis["entity_type_count"]
        total_relation_types += analysis["relation_type_count"]
        
        # 收集所有类型
        all_entity_types.update(analysis["entity_types"].keys())
        all_relation_types.update(analysis["relation_types"].keys())
    
    # 计算平均值
    success_count = file_stats['success']
    avg_entities = total_entities / success_count if success_count > 0 else 0
    avg_relations = total_relations / success_count if success_count > 0 else 0
    avg_entity_types = total_entity_types / success_count if success_count > 0 else 0
    avg_relation_types = total_relation_types / success_count if success_count > 0 else 0
    
    return {
        "model": model_name,
        "total_papers": file_stats['total'],
        "success": file_stats['success'],
        "failed": file_stats['failed'],
        "total_entities": total_entities,
        "total_relations": total_relations,
        "avg_entities": round(avg_entities, 2),
        "avg_relations": round(avg_relations, 2),
        "total_entity_types": total_entity_types,
        "total_relation_types": total_relation_types,
        "avg_entity_types": round(avg_entity_types, 2),
        "avg_relation_types": round(avg_relation_types, 2),
        "unique_entity_types": len(all_entity_types),
        "unique_relation_types": len(all_relation_types),
        "detailed_results": detailed_results
    }

# ------------------------------
# 主程序
# ------------------------------
def main():
    parser = argparse.ArgumentParser(description="RAG 结果对比分析")
    parser.add_argument(
        "--outputs-dir",
        help="覆盖 outputs 根目录，默认使用当前实验目录下的 outputs",
        default=None,
    )
    args = parser.parse_args()

    outputs_root = resolve_outputs_root(args.outputs_dir)
    # 三个模型的输出目录（基于 outputs）
    deepseek_dir = outputs_root / "extractions" / "deepseek"
    gemini_dir = outputs_root / "extractions" / "gemini"
    kimi_dir = outputs_root / "extractions" / "kimi"

    # 日志目录
    deepseek_log = outputs_root / "logs" / "deepseek"
    gemini_log = outputs_root / "logs" / "gemini"
    kimi_log = outputs_root / "logs" / "kimi"

    output_dir = ensure_output_dir(outputs_root)
    print("=" * 80)
    print("🔬 RAG 模型抽取结果统计分析")
    print("=" * 80)
    
    # 分析三个模型
    models_config = [
        ("DeepSeek", deepseek_dir, deepseek_log),
        ("Gemini", gemini_dir, gemini_log),
        ("Kimi", kimi_dir, kimi_log),
    ]
    
    all_results = []
    
    for model_name, json_dir, log_dir in models_config:
        result = analyze_model_results(model_name, json_dir, log_dir)
        all_results.append(result)
        
        # 为每个模型创建子目录并保存论文统计
        model_output_dir = output_dir / model_name.lower()
        os.makedirs(model_output_dir, exist_ok=True)
        
        paper_stats_df = pd.DataFrame(result["detailed_results"])
        paper_stats_file = model_output_dir / "paper_statistics.csv"
        paper_stats_df.to_csv(paper_stats_file, index=False, encoding='utf-8-sig')
        print(f"   ✅ 已保存: {paper_stats_file}")
    
    # ------------------------------
    # 生成汇总表格
    # ------------------------------
    print("\n" + "=" * 80)
    print("📋 模型对比汇总")
    print("=" * 80)
    
    summary_df = pd.DataFrame([
        {
            "模型": r["model"],
            "成功论文数": r["success"],
            "失败论文数": r["failed"],
            "总实体数": r["total_entities"],
            "总关系数": r["total_relations"],
            "平均实体数": r["avg_entities"],
            "平均关系数": r["avg_relations"],
            "平均实体类型数": r["avg_entity_types"],
            "平均关系类型数": r["avg_relation_types"],
            "总实体类型数": r["unique_entity_types"],
            "总关系类型数": r["unique_relation_types"]
        }
        for r in all_results
    ])
    
    print(summary_df.to_string(index=False))
    
    # ------------------------------
    # 生成汇总 Markdown 报告（放在外层）
    # ------------------------------
    report_file = output_dir / "extraction_summary.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# RAG 模型抽取结果统计报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. 模型对比汇总\n\n")
        # 手动生成 Markdown 表格
        headers = summary_df.columns.tolist()
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "|".join(["---"] * len(headers)) + "|\n")
        for _, row in summary_df.iterrows():
            f.write("| " + " | ".join(str(v) for v in row.values) + " |\n")
        f.write("\n")
        
        f.write("## 2. 关键发现\n\n")
        
        best_entities = max(all_results, key=lambda x: x["avg_entities"])
        best_relations = max(all_results, key=lambda x: x["avg_relations"])
        best_entity_types = max(all_results, key=lambda x: x["avg_entity_types"])
        best_relation_types = max(all_results, key=lambda x: x["avg_relation_types"])
        most_diverse_entity = max(all_results, key=lambda x: x["unique_entity_types"])
        most_diverse_relation = max(all_results, key=lambda x: x["unique_relation_types"])
        
        f.write(f"- **最多平均实体数**: {best_entities['model']} ({best_entities['avg_entities']} 个)\n")
        f.write(f"- **最多平均关系数**: {best_relations['model']} ({best_relations['avg_relations']} 个)\n")
        f.write(f"- **最多平均实体类型数**: {best_entity_types['model']} ({best_entity_types['avg_entity_types']} 种)\n")
        f.write(f"- **最多平均关系类型数**: {best_relation_types['model']} ({best_relation_types['avg_relation_types']} 种)\n")
        f.write(f"- **最丰富实体类型**: {most_diverse_entity['model']} (共 {most_diverse_entity['unique_entity_types']} 种不同类型)\n")
        f.write(f"- **最丰富关系类型**: {most_diverse_relation['model']} (共 {most_diverse_relation['unique_relation_types']} 种不同类型)\n\n")
        
        f.write("## 3. 各模型详细数据\n\n")
        
        for r in all_results:
            model_name = r['model']
            f.write(f"### {model_name}\n\n")
            f.write(f"- 成功论文数: {r['success']}\n")
            f.write(f"- 总实体数: {r['total_entities']}\n")
            f.write(f"- 总关系数: {r['total_relations']}\n")
            f.write(f"- 平均实体数: {r['avg_entities']}\n")
            f.write(f"- 平均关系数: {r['avg_relations']}\n")
            f.write(f"- 平均实体类型数: {r['avg_entity_types']}\n")
            f.write(f"- 平均关系类型数: {r['avg_relation_types']}\n")
            f.write(f"- 总实体类型数（去重）: {r['unique_entity_types']}\n")
            f.write(f"- 总关系类型数（去重）: {r['unique_relation_types']}\n")
            f.write(f"- 详细数据: `{model_name.lower()}/paper_statistics.csv`\n\n")
        
        f.write("## 4. 文件说明\n\n")
        f.write("```\n")
        f.write("statistics/\n")
        f.write("├── extraction_summary.md         # 本文件（汇总报告）\n")
        f.write("├── deepseek/\n")
        f.write("│   └── paper_statistics.csv     # DeepSeek 每篇论文的统计数据\n")
        f.write("├── gemini/\n")
        f.write("│   └── paper_statistics.csv     # Gemini 每篇论文的统计数据\n")
        f.write("└── kimi/\n")
        f.write("    └── paper_statistics.csv     # Kimi 每篇论文的统计数据\n")
        f.write("```\n\n")
        
        f.write("## 5. CSV 文件列说明\n\n")
        f.write("- **paper**: 论文名称\n")
        f.write("- **entities**: 实体数量\n")
        f.write("- **relations**: 关系数量\n")
        f.write("- **entity_types**: 实体类型数量（去重）\n")
        f.write("- **relation_types**: 关系类型数量（去重）\n")
    
    print(f"\n✅ 汇总报告已保存: {report_file}")
    
    # 打印统计亮点
    print("\n" + "=" * 80)
    print("🎯 统计亮点")
    print("=" * 80)
    
    entity_ranking = sorted(all_results, key=lambda x: x["avg_entities"], reverse=True)
    relation_ranking = sorted(all_results, key=lambda x: x["avg_relations"], reverse=True)
    entity_type_ranking = sorted(all_results, key=lambda x: x["avg_entity_types"], reverse=True)
    relation_type_ranking = sorted(all_results, key=lambda x: x["avg_relation_types"], reverse=True)
    
    print("\n平均实体数排名:")
    for rank, r in enumerate(entity_ranking, 1):
        print(f"  {rank}. {r['model']}: {r['avg_entities']} 个")
    
    print("\n平均关系数排名:")
    for rank, r in enumerate(relation_ranking, 1):
        print(f"  {rank}. {r['model']}: {r['avg_relations']} 个")
    
    print("\n平均实体类型数排名:")
    for rank, r in enumerate(entity_type_ranking, 1):
        print(f"  {rank}. {r['model']}: {r['avg_entity_types']} 种 (总共 {r['unique_entity_types']} 种不同类型)")
    
    print("\n平均关系类型数排名:")
    for rank, r in enumerate(relation_type_ranking, 1):
        print(f"  {rank}. {r['model']}: {r['avg_relation_types']} 种 (总共 {r['unique_relation_types']} 种不同类型)")
    
    print("\n" + "=" * 80)
    print("✅ 分析完成!")
    print("=" * 80)
    print(f"\n📁 输出目录: {output_dir}")
    print(f"   - 汇总报告: extraction_summary.md")
    print(f"   - DeepSeek统计: deepseek/paper_statistics.csv")
    print(f"   - Gemini统计: gemini/paper_statistics.csv")
    print(f"   - Kimi统计: kimi/paper_statistics.csv")

if __name__ == "__main__":
    main()
