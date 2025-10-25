# 抽取结果一致性分析报告

运行目录: `E:\entities\experiments\exp02_improved\outputs\extractions\consistency`

共发现 3 次运行: 1, 2, 3

## 模型级汇总

| 模型 | 论文数 | 平均实体Jaccard | 平均关系Jaccard | 实体数CV(均值) | 关系数CV(均值) |
|---|---|---|---|---|---|
| deepseek | 10 | 0.4744 | 0.5733 | 0.1823 | 0.1912 |
| gemini | 10 | 0.391 | 0.4422 | 0.1339 | 0.1289 |
| kimi | 10 | 0.5082 | 0.4861 | 0.1228 | 0.1666 |

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
