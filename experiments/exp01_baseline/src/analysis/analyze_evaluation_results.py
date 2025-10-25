# -*- coding: utf-8 -*-
"""
评估结果统计分析脚本
分析 Gemini 对三个模型抽取结果的评估数据
生成详细的准确率、错误分析和对比报告
"""
import os
import json
import argparse
from pathlib import Path
from collections import defaultdict, Counter
import pandas as pd
from datetime import datetime

# ------------------------------
# 路径配置
# ------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # .../exp01_baseline

def resolve_outputs_root(cli_outputs_dir: str | None) -> Path:
    """确定 outputs 根目录：优先使用命令行传入，否则使用当前实验目录下的 outputs。"""
    if cli_outputs_dir:
        return Path(cli_outputs_dir).resolve()
    return PROJECT_ROOT / "outputs"

# ------------------------------
# 分析函数
# ------------------------------
def analyze_single_file(eval_file: Path) -> dict:
    """分析单个评估文件"""
    with open(eval_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entities = data.get('entities', [])
    relations = data.get('relations', [])
    
    # 统计实体评估结果
    entity_stats = {
        'total': len(entities),
        'correct': sum(1 for e in entities if e.get('evaluation') == '正确'),
        'incorrect': sum(1 for e in entities if e.get('evaluation') == '错误'),
        'uncertain': sum(1 for e in entities if e.get('evaluation') == '不确定'),
        'missing_eval': sum(1 for e in entities if 'evaluation' not in e)
    }
    
    # 统计关系评估结果
    relation_stats = {
        'total': len(relations),
        'correct': sum(1 for r in relations if r.get('evaluation') == '正确'),
        'incorrect': sum(1 for r in relations if r.get('evaluation') == '错误'),
        'uncertain': sum(1 for r in relations if r.get('evaluation') == '不确定'),
        'missing_eval': sum(1 for r in relations if 'evaluation' not in r)
    }
    
    # 统计实体类型分布（正确vs错误）
    entity_type_correct = defaultdict(int)
    entity_type_incorrect = defaultdict(int)
    entity_type_total = defaultdict(int)
    
    for entity in entities:
        etype = entity.get('type', 'unknown')
        evaluation = entity.get('evaluation', 'unknown')
        entity_type_total[etype] += 1
        if evaluation == '正确':
            entity_type_correct[etype] += 1
        elif evaluation == '错误':
            entity_type_incorrect[etype] += 1
    
    # 统计关系类型分布（正确vs错误）
    relation_type_correct = defaultdict(int)
    relation_type_incorrect = defaultdict(int)
    relation_type_total = defaultdict(int)
    
    for relation in relations:
        rtype = relation.get('relation', 'unknown')
        evaluation = relation.get('evaluation', 'unknown')
        relation_type_total[rtype] += 1
        if evaluation == '正确':
            relation_type_correct[rtype] += 1
        elif evaluation == '错误':
            relation_type_incorrect[rtype] += 1
    
    return {
        'entity_stats': entity_stats,
        'relation_stats': relation_stats,
        'entity_type_correct': dict(entity_type_correct),
        'entity_type_incorrect': dict(entity_type_incorrect),
        'entity_type_total': dict(entity_type_total),
        'relation_type_correct': dict(relation_type_correct),
        'relation_type_incorrect': dict(relation_type_incorrect),
        'relation_type_total': dict(relation_type_total)
    }

def analyze_model_results(model_name: str, eval_dir: Path) -> dict:
    """分析单个模型的所有评估结果"""
    print(f"\n{'='*80}")
    print(f"📊 分析 {model_name} 模型的评估结果")
    print(f"{'='*80}")
    
    if not eval_dir.exists():
        print(f"⚠️ 目录不存在: {eval_dir}")
        return None
    
    # 递归查找 *_evaluated.json，兼容子目录结构（如 priority/general）
    eval_files = sorted(eval_dir.rglob("*_evaluated.json"))
    
    if not eval_files:
        print(f"⚠️ 未找到评估文件")
        return None
    
    print(f"📁 找到 {len(eval_files)} 个评估文件")
    
    # 汇总统计
    total_entity_stats = {
        'total': 0,
        'correct': 0,
        'incorrect': 0,
        'uncertain': 0,
        'missing_eval': 0
    }
    
    total_relation_stats = {
        'total': 0,
        'correct': 0,
        'incorrect': 0,
        'uncertain': 0,
        'missing_eval': 0
    }
    
    # 所有实体类型统计
    all_entity_type_correct = defaultdict(int)
    all_entity_type_incorrect = defaultdict(int)
    all_entity_type_total = defaultdict(int)
    
    # 所有关系类型统计
    all_relation_type_correct = defaultdict(int)
    all_relation_type_incorrect = defaultdict(int)
    all_relation_type_total = defaultdict(int)
    
    # 逐文件详细结果
    paper_details = []
    
    for eval_file in eval_files:
        paper_name = eval_file.stem.replace('_evaluated', '')
        
        try:
            file_analysis = analyze_single_file(eval_file)
            
            # 汇总实体统计
            for key in total_entity_stats:
                total_entity_stats[key] += file_analysis['entity_stats'][key]
            
            # 汇总关系统计
            for key in total_relation_stats:
                total_relation_stats[key] += file_analysis['relation_stats'][key]
            
            # 汇总类型统计
            for etype, count in file_analysis['entity_type_correct'].items():
                all_entity_type_correct[etype] += count
            for etype, count in file_analysis['entity_type_incorrect'].items():
                all_entity_type_incorrect[etype] += count
            for etype, count in file_analysis['entity_type_total'].items():
                all_entity_type_total[etype] += count
            
            for rtype, count in file_analysis['relation_type_correct'].items():
                all_relation_type_correct[rtype] += count
            for rtype, count in file_analysis['relation_type_incorrect'].items():
                all_relation_type_incorrect[rtype] += count
            for rtype, count in file_analysis['relation_type_total'].items():
                all_relation_type_total[rtype] += count
            
            # 记录论文详细结果
            entity_accuracy = (file_analysis['entity_stats']['correct'] / 
                             file_analysis['entity_stats']['total'] * 100) if file_analysis['entity_stats']['total'] > 0 else 0
            relation_accuracy = (file_analysis['relation_stats']['correct'] / 
                               file_analysis['relation_stats']['total'] * 100) if file_analysis['relation_stats']['total'] > 0 else 0
            
            paper_details.append({
                'paper': paper_name,
                'entity_total': file_analysis['entity_stats']['total'],
                'entity_correct': file_analysis['entity_stats']['correct'],
                'entity_incorrect': file_analysis['entity_stats']['incorrect'],
                'entity_accuracy': round(entity_accuracy, 2),
                'relation_total': file_analysis['relation_stats']['total'],
                'relation_correct': file_analysis['relation_stats']['correct'],
                'relation_incorrect': file_analysis['relation_stats']['incorrect'],
                'relation_accuracy': round(relation_accuracy, 2)
            })
            
        except Exception as e:
            print(f"⚠️ 分析文件失败 {eval_file.name}: {e}")
            continue
    
    # 计算总体准确率
    entity_accuracy = (total_entity_stats['correct'] / 
                      total_entity_stats['total'] * 100) if total_entity_stats['total'] > 0 else 0
    relation_accuracy = (total_relation_stats['correct'] / 
                        total_relation_stats['total'] * 100) if total_relation_stats['total'] > 0 else 0
    
    print(f"\n实体统计:")
    print(f"  - 总数: {total_entity_stats['total']}")
    print(f"  - 正确: {total_entity_stats['correct']} ({entity_accuracy:.2f}%)")
    print(f"  - 错误: {total_entity_stats['incorrect']}")
    print(f"  - 不确定: {total_entity_stats['uncertain']}")
    
    print(f"\n关系统计:")
    print(f"  - 总数: {total_relation_stats['total']}")
    print(f"  - 正确: {total_relation_stats['correct']} ({relation_accuracy:.2f}%)")
    print(f"  - 错误: {total_relation_stats['incorrect']}")
    print(f"  - 不确定: {total_relation_stats['uncertain']}")
    
    return {
        'model': model_name,
        'files_analyzed': len(eval_files),
        'entity_stats': total_entity_stats,
        'relation_stats': total_relation_stats,
        'entity_accuracy': round(entity_accuracy, 2),
        'relation_accuracy': round(relation_accuracy, 2),
        'entity_type_correct': dict(all_entity_type_correct),
        'entity_type_incorrect': dict(all_entity_type_incorrect),
        'entity_type_total': dict(all_entity_type_total),
        'relation_type_correct': dict(all_relation_type_correct),
        'relation_type_incorrect': dict(all_relation_type_incorrect),
        'relation_type_total': dict(all_relation_type_total),
        'paper_details': paper_details
    }

def generate_entity_type_accuracy_table(model_results: dict) -> pd.DataFrame:
    """生成实体类型准确率表格"""
    rows = []
    
    for etype in sorted(model_results['entity_type_total'].keys()):
        total = model_results['entity_type_total'][etype]
        correct = model_results['entity_type_correct'].get(etype, 0)
        incorrect = model_results['entity_type_incorrect'].get(etype, 0)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        rows.append({
            '实体类型': etype,
            '总数': total,
            '正确': correct,
            '错误': incorrect,
            '准确率(%)': round(accuracy, 2)
        })
    
    return pd.DataFrame(rows)

def generate_relation_type_accuracy_table(model_results: dict) -> pd.DataFrame:
    """生成关系类型准确率表格"""
    rows = []
    
    for rtype in sorted(model_results['relation_type_total'].keys()):
        total = model_results['relation_type_total'][rtype]
        correct = model_results['relation_type_correct'].get(rtype, 0)
        incorrect = model_results['relation_type_incorrect'].get(rtype, 0)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        rows.append({
            '关系类型': rtype,
            '总数': total,
            '正确': correct,
            '错误': incorrect,
            '准确率(%)': round(accuracy, 2)
        })
    
    return pd.DataFrame(rows)

# ------------------------------
# 主程序
# ------------------------------
def main():
    parser = argparse.ArgumentParser(description="评估结果统计分析")
    parser.add_argument(
        "--outputs-dir",
        help="覆盖 outputs 根目录，默认使用当前实验目录下的 outputs",
        default=None,
    )
    args = parser.parse_args()

    outputs_root = resolve_outputs_root(args.outputs_dir)
    # 评估结果目录（基于 outputs）
    eval_root = outputs_root / "evaluations"
    deepseek_eval_dir = eval_root / "deepseek"
    gemini_eval_dir = eval_root / "gemini"
    kimi_eval_dir = eval_root / "kimi"

    # 输出目录（统一使用 outputs/analysis/...）
    analysis_output_dir = outputs_root / "analysis" / "evaluation_results"
    os.makedirs(analysis_output_dir, exist_ok=True)

    print("=" * 80)
    print("📈 评估结果统计分析")
    print("=" * 80)
    
    # 分析三个模型
    models_config = [
        ("DeepSeek", deepseek_eval_dir),
        ("Gemini", gemini_eval_dir),
        ("Kimi", kimi_eval_dir),
    ]
    
    all_model_results = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for model_name, eval_dir in models_config:
        result = analyze_model_results(model_name, eval_dir)
        if result:
            all_model_results.append(result)
            
            # 为每个模型创建子目录
            model_output_dir = analysis_output_dir / model_name.lower()
            os.makedirs(model_output_dir, exist_ok=True)
            
            # 只保存论文级别详细结果到模型子目录
            paper_details_df = pd.DataFrame(result['paper_details'])
            paper_details_file = model_output_dir / f"paper_details.csv"
            paper_details_df.to_csv(paper_details_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ {model_name} 论文详情已保存: {paper_details_file}")
    
    if not all_model_results:
        print("\n❌ 没有找到任何评估结果")
        return
    
    # ------------------------------
    # 生成汇总 Markdown 报告（放在外层目录）
    # ------------------------------
    print("\n" + "=" * 80)
    print("📋 生成汇总报告")
    print("=" * 80)
    
    # 汇总表格
    summary_df = pd.DataFrame([
        {
            '模型': r['model'],
            '评估文件数': r['files_analyzed'],
            '实体总数': r['entity_stats']['total'],
            '实体正确': r['entity_stats']['correct'],
            '实体错误': r['entity_stats']['incorrect'],
            '实体准确率(%)': r['entity_accuracy'],
            '关系总数': r['relation_stats']['total'],
            '关系正确': r['relation_stats']['correct'],
            '关系错误': r['relation_stats']['incorrect'],
            '关系准确率(%)': r['relation_accuracy']
        }
        for r in all_model_results
    ])
    
    # 打印汇总
    print(summary_df.to_string(index=False))
    
    # 生成 Markdown 报告（放在外层）
    report_file = analysis_output_dir / "evaluation_summary.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# RAG 模型抽取结果评估分析报告\n\n")
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
        
        # 找出最佳模型
        best_entity = max(all_model_results, key=lambda x: x['entity_accuracy'])
        best_relation = max(all_model_results, key=lambda x: x['relation_accuracy'])
        
        f.write(f"- **实体抽取最优**: {best_entity['model']} ({best_entity['entity_accuracy']}%)\n")
        f.write(f"- **关系抽取最优**: {best_relation['model']} ({best_relation['relation_accuracy']}%)\n\n")
        
        f.write("## 3. 各模型详细分析\n\n")
        
        for model_result in all_model_results:
            model_name = model_result['model']
            f.write(f"### {model_name}\n\n")
            f.write(f"- 实体准确率: {model_result['entity_accuracy']}%\n")
            f.write(f"- 关系准确率: {model_result['relation_accuracy']}%\n")
            f.write(f"- 实体总数: {model_result['entity_stats']['total']}\n")
            f.write(f"- 关系总数: {model_result['relation_stats']['total']}\n")
            f.write(f"- 详细数据: `{model_name.lower()}/paper_details.csv`\n\n")
        
        f.write("## 4. 文件说明\n\n")
        f.write("```\n")
        f.write("evaluation_results/\n")
        f.write("├── evaluation_summary.md     # 本文件（汇总报告）\n")
        f.write("├── deepseek/\n")
        f.write("│   └── paper_details.csv     # DeepSeek 每篇论文的详细结果\n")
        f.write("├── gemini/\n")
        f.write("│   └── paper_details.csv     # Gemini 每篇论文的详细结果\n")
        f.write("└── kimi/\n")
        f.write("    └── paper_details.csv     # Kimi 每篇论文的详细结果\n")
        f.write("```\n\n")
        
        f.write("## 5. 改进建议\n\n")
        f.write("1. 分析错误实体和关系的具体类型，针对性优化 Prompt\n")
        f.write("2. 对准确率较低的实体/关系类型增加更多 few-shot 示例\n")
        f.write("3. 人工复核错误案例，调整 schema 定义\n")
        f.write("4. 考虑使用集成方法结合多个模型的优势\n")
    
    print(f"\n✅ 汇总报告已保存: {report_file}")
    
    # 打印统计亮点
    print("\n" + "=" * 80)
    print("🎯 统计亮点")
    print("=" * 80)
    
    # 实体准确率对比
    entity_accuracies = [(r['model'], r['entity_accuracy']) for r in all_model_results]
    entity_accuracies.sort(key=lambda x: x[1], reverse=True)
    
    print("\n实体准确率排名:")
    for rank, (model, acc) in enumerate(entity_accuracies, 1):
        print(f"  {rank}. {model}: {acc}%")
    
    # 关系准确率对比
    relation_accuracies = [(r['model'], r['relation_accuracy']) for r in all_model_results]
    relation_accuracies.sort(key=lambda x: x[1], reverse=True)
    
    print("\n关系准确率排名:")
    for rank, (model, acc) in enumerate(relation_accuracies, 1):
        print(f"  {rank}. {model}: {acc}%")
    
    print("\n" + "=" * 80)
    print("✅ 分析完成!")
    print("=" * 80)
    print(f"\n📁 输出目录: {analysis_output_dir}")
    print(f"   - 汇总报告: evaluation_summary.md")
    print(f"   - DeepSeek详情: deepseek/paper_details.csv")
    print(f"   - Gemini详情: gemini/paper_details.csv")
    print(f"   - Kimi详情: kimi/paper_details.csv")

if __name__ == "__main__":
    main()
