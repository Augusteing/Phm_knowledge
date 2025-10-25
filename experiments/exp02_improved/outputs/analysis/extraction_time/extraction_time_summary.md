# RAG 模型抽取时间统计报告

生成时间: 2025-10-18 20:05:31

## 1. 模型时间对比汇总

| 模型 | 论文数 | 总耗时(分钟) | 平均耗时(秒) | 最短耗时(秒) | 最长耗时(秒) | 总Token数 | 平均Token数 |
|---|---|---|---|---|---|---|---|
| DeepSeek | 10 | 6.64 | 39.81 | 26.54 | 62.09 | 140794 | 14079 |
| Gemini | 10 | 15.04 | 90.23 | 41.57 | 130.59 | 231340 | 23134 |
| Kimi | 10 | 3.07 | 18.43 | 13.58 | 23.5 | 148526 | 14853 |

## 2. 关键发现

- **最快平均速度**: Kimi (18.43 秒/篇)
- **最慢平均速度**: Gemini (90.23 秒/篇)
- **总时间最短**: Kimi (3.07 分钟)
- **最多Token消耗**: Gemini (平均 23134 tokens/篇)

- **速度差异**: Gemini 比 Kimi 慢 4.90 倍

## 3. 各模型详细数据

### DeepSeek

- 论文数: 10
- 总耗时: 6.64 分钟 (398.14 秒)
- 平均耗时: 39.81 秒/篇
- 最短耗时: 26.54 秒
- 最长耗时: 62.09 秒
- 总Token消耗: 140,794
- 平均Token消耗: 14,079 tokens/篇
- 抽取效率: 1.36 个知识元素/秒
- 详细数据: `deepseek/paper_time_stats.csv`

### Gemini

- 论文数: 10
- 总耗时: 15.04 分钟 (902.27 秒)
- 平均耗时: 90.23 秒/篇
- 最短耗时: 41.57 秒
- 最长耗时: 130.59 秒
- 总Token消耗: 231,340
- 平均Token消耗: 23,134 tokens/篇
- 抽取效率: 0.75 个知识元素/秒
- 详细数据: `gemini/paper_time_stats.csv`

### Kimi

- 论文数: 10
- 总耗时: 3.07 分钟 (184.25 秒)
- 平均耗时: 18.43 秒/篇
- 最短耗时: 13.58 秒
- 最长耗时: 23.5 秒
- 总Token消耗: 148,526
- 平均Token消耗: 14,853 tokens/篇
- 抽取效率: 1.56 个知识元素/秒
- 详细数据: `kimi/paper_time_stats.csv`

## 4. 文件说明

```
extraction_time/
├── extraction_time_summary.md    # 本文件（汇总报告）
├── deepseek/
│   └── paper_time_stats.csv     # DeepSeek 每篇论文的时间统计
├── gemini/
│   └── paper_time_stats.csv     # Gemini 每篇论文的时间统计
└── kimi/
    └── paper_time_stats.csv     # Kimi 每篇论文的时间统计
```

## 5. CSV 文件列说明

- **paper**: 论文名称
- **duration_seconds**: 抽取耗时（秒）
- **duration_minutes**: 抽取耗时（分钟）
- **entity_count**: 实体数量
- **relation_count**: 关系数量
- **prompt_tokens**: Prompt Token数
- **completion_tokens**: 生成Token数
- **total_tokens**: 总Token数

## 6. 性能分析

### 平均速度排名（从快到慢）

1. **Kimi**: 18.43 秒/篇
2. **DeepSeek**: 39.81 秒/篇
3. **Gemini**: 90.23 秒/篇

### Token消耗排名（从少到多）

1. **DeepSeek**: 14,079 tokens/篇
2. **Kimi**: 14,853 tokens/篇
3. **Gemini**: 23,134 tokens/篇

### 抽取效率排名（知识元素/秒）

1. **Kimi**: 1.56 个/秒
2. **DeepSeek**: 1.36 个/秒
3. **Gemini**: 0.75 个/秒
