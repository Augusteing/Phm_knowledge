"""
分析不同模型的知识抽取时间统计

功能：
1. 读取各模型的extraction_log日志文件
2. 统计每篇论文的抽取时间
3. 生成每个模型的论文级时间统计CSV
4. 生成汇总Markdown报告

输出结构：
outputs/analysis/extraction_time/
├── extraction_time_summary.md    # 汇总报告
├── deepseek/
│   └── paper_time_stats.csv      # DeepSeek每篇论文的时间统计
├── gemini/
│   └── paper_time_stats.csv
└── kimi/
    └── paper_time_stats.csv
"""

import json
import os
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List

# ------------------------------
# 配置路径
# ------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # .../exp01_baseline

def resolve_outputs_root(cli_outputs_dir: str | None) -> Path:
    if cli_outputs_dir:
        return Path(cli_outputs_dir).resolve()
    return PROJECT_ROOT / "outputs"

# 模型日志目录
def ensure_output_dir(outputs_root: Path) -> Path:
    out = outputs_root / "analysis" / "extraction_time"
    os.makedirs(out, exist_ok=True)
    return out

# ------------------------------
# 核心函数
# ------------------------------

def find_latest_log(log_dir: Path) -> Path:
    """找到指定目录下最新的extraction_log文件"""
    # 支持日志命名变体：extraction_log_*.json 或 extraction_log.json
    log_files = list(log_dir.glob("extraction_log_*.json"))
    if not log_files:
        log_files = list(log_dir.glob("extraction_log.json"))
    if not log_files:
        raise FileNotFoundError(f"未找到日志文件: {log_dir}")
    
    # 按文件名排序，取最新的
    latest_log = sorted(log_files, reverse=True)[0]
    return latest_log

def extract_paper_name(paper_path: str) -> str:
    """从完整路径中提取论文名称"""
    # 例如: "priority/基于XXX.md" -> "基于XXX"
    filename = Path(paper_path).stem
    return filename

def analyze_log_file(log_file: Path, model_name: str) -> Dict:
    """分析单个日志文件，提取时间信息"""
    print(f"\n📊 分析 {model_name} 日志文件: {log_file.name}")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
    
    # 提取论文级别的时间统计
    paper_stats = []
    for entry in log_data.get("logs", []):
        if entry.get("success", False):
            paper_stats.append({
                "paper": extract_paper_name(entry["paper"]),
                "duration_seconds": round(entry["duration_seconds"], 2),
                "duration_minutes": round(entry["duration_seconds"] / 60, 2),
                "entity_count": entry.get("entity_count", 0),
                "relation_count": entry.get("relation_count", 0),
                "prompt_tokens": entry.get("prompt_tokens", 0),
                "completion_tokens": entry.get("completion_tokens", 0),
                "total_tokens": entry.get("total_tokens", 0)
            })
    
    # 计算汇总统计
    total_papers = len(paper_stats)
    total_time = sum(p["duration_seconds"] for p in paper_stats)
    avg_time = total_time / total_papers if total_papers > 0 else 0
    min_time = min((p["duration_seconds"] for p in paper_stats), default=0)
    max_time = max((p["duration_seconds"] for p in paper_stats), default=0)
    
    total_entities = sum(p["entity_count"] for p in paper_stats)
    total_relations = sum(p["relation_count"] for p in paper_stats)
    total_tokens_used = sum(p["total_tokens"] for p in paper_stats)
    
    print(f"   - 成功论文数: {total_papers}")
    print(f"   - 总耗时: {round(total_time / 60, 2)} 分钟")
    print(f"   - 平均耗时: {round(avg_time, 2)} 秒/篇")
    
    return {
        "model": model_name,
        "total_papers": total_papers,
        "total_time_seconds": round(total_time, 2),
        "total_time_minutes": round(total_time / 60, 2),
        "avg_time_seconds": round(avg_time, 2),
        "min_time_seconds": round(min_time, 2),
        "max_time_seconds": round(max_time, 2),
        "total_entities": total_entities,
        "total_relations": total_relations,
        "total_tokens": total_tokens_used,
        "avg_tokens_per_paper": round(total_tokens_used / total_papers, 0) if total_papers > 0 else 0,
        "paper_stats": paper_stats
    }

# ------------------------------
# 主程序
# ------------------------------
def main():
    parser = argparse.ArgumentParser(description="抽取时间统计分析")
    parser.add_argument(
        "--outputs-dir",
        help="覆盖 outputs 根目录，默认使用当前实验目录下的 outputs",
        default=None,
    )
    args = parser.parse_args()

    outputs_root = resolve_outputs_root(args.outputs_dir)
    logs_dir = outputs_root / "logs"
    output_dir = ensure_output_dir(outputs_root)

    # 模型日志目录
    deepseek_log = logs_dir / "deepseek"
    gemini_log = logs_dir / "gemini"
    kimi_log = logs_dir / "kimi"
    print("=" * 80)
    print("⏱️ RAG 模型抽取时间统计分析")
    print("=" * 80)
    
    # 分析三个模型
    models_config = [
        ("DeepSeek", deepseek_log),
        ("Gemini", gemini_log),
        ("Kimi", kimi_log),
    ]
    
    all_results = []
    
    for model_name, log_dir in models_config:
        try:
            # 找到最新的日志文件
            latest_log = find_latest_log(log_dir)
            result = analyze_log_file(latest_log, model_name)
            all_results.append(result)
            
            # 为每个模型创建子目录并保存论文时间统计
            model_output_dir = output_dir / model_name.lower()
            os.makedirs(model_output_dir, exist_ok=True)
            
            paper_stats_df = pd.DataFrame(result["paper_stats"])
            paper_stats_file = model_output_dir / "paper_time_stats.csv"
            paper_stats_df.to_csv(paper_stats_file, index=False, encoding='utf-8-sig')
            print(f"   ✅ 已保存: {paper_stats_file}")
            
        except FileNotFoundError as e:
            print(f"   ⚠️ {e}")
            continue
    
    if not all_results:
        print("\n❌ 未找到任何日志文件，退出分析")
        return
    
    # ------------------------------
    # 生成汇总表格
    # ------------------------------
    print("\n" + "=" * 80)
    print("📋 模型对比汇总")
    print("=" * 80)
    
    summary_df = pd.DataFrame([
        {
            "模型": r["model"],
            "论文数": r["total_papers"],
            "总耗时(分钟)": r["total_time_minutes"],
            "平均耗时(秒)": r["avg_time_seconds"],
            "最短耗时(秒)": r["min_time_seconds"],
            "最长耗时(秒)": r["max_time_seconds"],
            "总Token数": r["total_tokens"],
            "平均Token数": int(r["avg_tokens_per_paper"])
        }
        for r in all_results
    ])
    
    print(summary_df.to_string(index=False))
    
    # ------------------------------
    # 生成汇总 Markdown 报告
    # ------------------------------
    report_file = output_dir / "extraction_time_summary.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# RAG 模型抽取时间统计报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. 模型时间对比汇总\n\n")
        # 生成 Markdown 表格
        headers = summary_df.columns.tolist()
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "|".join(["---"] * len(headers)) + "|\n")
        for _, row in summary_df.iterrows():
            f.write("| " + " | ".join(str(v) for v in row.values) + " |\n")
        f.write("\n")
        
        f.write("## 2. 关键发现\n\n")
        
        fastest_avg = min(all_results, key=lambda x: x["avg_time_seconds"])
        slowest_avg = max(all_results, key=lambda x: x["avg_time_seconds"])
        most_efficient = min(all_results, key=lambda x: x["total_time_minutes"])
        most_tokens = max(all_results, key=lambda x: x["avg_tokens_per_paper"])
        
        f.write(f"- **最快平均速度**: {fastest_avg['model']} ({fastest_avg['avg_time_seconds']} 秒/篇)\n")
        f.write(f"- **最慢平均速度**: {slowest_avg['model']} ({slowest_avg['avg_time_seconds']} 秒/篇)\n")
        f.write(f"- **总时间最短**: {most_efficient['model']} ({most_efficient['total_time_minutes']} 分钟)\n")
        f.write(f"- **最多Token消耗**: {most_tokens['model']} (平均 {int(most_tokens['avg_tokens_per_paper'])} tokens/篇)\n\n")
        
        # 计算速度对比
        speed_ratio = slowest_avg['avg_time_seconds'] / fastest_avg['avg_time_seconds']
        f.write(f"- **速度差异**: {slowest_avg['model']} 比 {fastest_avg['model']} 慢 {speed_ratio:.2f} 倍\n\n")
        
        f.write("## 3. 各模型详细数据\n\n")
        
        for r in all_results:
            model_name = r['model']
            f.write(f"### {model_name}\n\n")
            f.write(f"- 论文数: {r['total_papers']}\n")
            f.write(f"- 总耗时: {r['total_time_minutes']} 分钟 ({r['total_time_seconds']} 秒)\n")
            f.write(f"- 平均耗时: {r['avg_time_seconds']} 秒/篇\n")
            f.write(f"- 最短耗时: {r['min_time_seconds']} 秒\n")
            f.write(f"- 最长耗时: {r['max_time_seconds']} 秒\n")
            f.write(f"- 总Token消耗: {r['total_tokens']:,}\n")
            f.write(f"- 平均Token消耗: {int(r['avg_tokens_per_paper']):,} tokens/篇\n")
            f.write(f"- 抽取效率: {round(r['total_entities'] + r['total_relations'], 0) / r['total_time_seconds']:.2f} 个知识元素/秒\n")
            f.write(f"- 详细数据: `{model_name.lower()}/paper_time_stats.csv`\n\n")
        
        f.write("## 4. 文件说明\n\n")
        f.write("```\n")
        f.write("extraction_time/\n")
        f.write("├── extraction_time_summary.md    # 本文件（汇总报告）\n")
        f.write("├── deepseek/\n")
        f.write("│   └── paper_time_stats.csv     # DeepSeek 每篇论文的时间统计\n")
        f.write("├── gemini/\n")
        f.write("│   └── paper_time_stats.csv     # Gemini 每篇论文的时间统计\n")
        f.write("└── kimi/\n")
        f.write("    └── paper_time_stats.csv     # Kimi 每篇论文的时间统计\n")
        f.write("```\n\n")
        
        f.write("## 5. CSV 文件列说明\n\n")
        f.write("- **paper**: 论文名称\n")
        f.write("- **duration_seconds**: 抽取耗时（秒）\n")
        f.write("- **duration_minutes**: 抽取耗时（分钟）\n")
        f.write("- **entity_count**: 实体数量\n")
        f.write("- **relation_count**: 关系数量\n")
        f.write("- **prompt_tokens**: Prompt Token数\n")
        f.write("- **completion_tokens**: 生成Token数\n")
        f.write("- **total_tokens**: 总Token数\n\n")
        
        f.write("## 6. 性能分析\n\n")
        
        # 时间效率排名
        time_ranking = sorted(all_results, key=lambda x: x["avg_time_seconds"])
        f.write("### 平均速度排名（从快到慢）\n\n")
        for rank, r in enumerate(time_ranking, 1):
            f.write(f"{rank}. **{r['model']}**: {r['avg_time_seconds']} 秒/篇\n")
        f.write("\n")
        
        # Token效率排名
        token_ranking = sorted(all_results, key=lambda x: x["avg_tokens_per_paper"])
        f.write("### Token消耗排名（从少到多）\n\n")
        for rank, r in enumerate(token_ranking, 1):
            f.write(f"{rank}. **{r['model']}**: {int(r['avg_tokens_per_paper']):,} tokens/篇\n")
        f.write("\n")
        
        # 抽取效率（知识元素/秒）
        efficiency_ranking = sorted(all_results, 
                                   key=lambda x: (x['total_entities'] + x['total_relations']) / x['total_time_seconds'],
                                   reverse=True)
        f.write("### 抽取效率排名（知识元素/秒）\n\n")
        for rank, r in enumerate(efficiency_ranking, 1):
            efficiency = (r['total_entities'] + r['total_relations']) / r['total_time_seconds']
            f.write(f"{rank}. **{r['model']}**: {efficiency:.2f} 个/秒\n")
    
    print(f"\n✅ 汇总报告已保存: {report_file}")
    
    # 打印统计亮点
    print("\n" + "=" * 80)
    print("🎯 统计亮点")
    print("=" * 80)
    
    time_ranking = sorted(all_results, key=lambda x: x["avg_time_seconds"])
    
    print("\n平均速度排名（快→慢）:")
    for rank, r in enumerate(time_ranking, 1):
        print(f"  {rank}. {r['model']}: {r['avg_time_seconds']} 秒/篇")
    
    print("\nToken消耗排名（少→多）:")
    token_ranking = sorted(all_results, key=lambda x: x["avg_tokens_per_paper"])
    for rank, r in enumerate(token_ranking, 1):
        print(f"  {rank}. {r['model']}: {int(r['avg_tokens_per_paper']):,} tokens/篇")
    
    print("\n" + "=" * 80)
    print("✅ 分析完成!")
    print("=" * 80)
    print(f"\n📁 输出目录: {output_dir}")
    print(f"   - 汇总报告: extraction_time_summary.md")
    print(f"   - DeepSeek统计: deepseek/paper_time_stats.csv")
    print(f"   - Gemini统计: gemini/paper_time_stats.csv")
    print(f"   - Kimi统计: kimi/paper_time_stats.csv")

if __name__ == "__main__":
    main()
