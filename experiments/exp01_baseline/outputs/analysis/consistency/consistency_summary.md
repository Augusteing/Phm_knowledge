# 抽取结果一致性分析报告

运行目录: `E:\entities\experiments\exp01_baseline\outputs\extractions\consistency`

共发现 3 次运行: 1, 2, 3

## 模型级汇总

| 模型 | 论文数 | 平均实体Jaccard | 平均关系Jaccard | 实体数CV(均值) | 关系数CV(均值) |
|---|---|---|---|---|---|
| deepseek | 10 | 0.7771 | 0.6298 | 0.0521 | 0.066 |
| gemini | 10 | 0.472 | 0.4746 | 0.1032 | 0.089 |
| kimi | 10 | 0.5709 | 0.4851 | 0.1221 | 0.1475 |

## 文件结构

```
outputs/analysis/consistency/
├── consistency_summary.md
├── deepseek/paper_consistency.csv
├── gemini/paper_consistency.csv
└── kimi/paper_consistency.csv
```

## 指标说明

- 实体/关系 Jaccard: 跨运行的集合相似度（成对平均），越高越稳定
- 实体数/关系数 CV: 规模波动（std/mean），越低越稳定
- runs 列示该论文实际参与统计的运行次数（缺失会自动跳过）
