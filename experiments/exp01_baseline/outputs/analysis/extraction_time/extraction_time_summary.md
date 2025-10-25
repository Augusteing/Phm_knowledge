# RAG 模型抽取时间统计报告

生成时间: 2025-10-18 15:30:40

## 1. 模型时间对比汇总

| 模型 | 论文数 | 总耗时(分钟) | 平均耗时(秒) | 最短耗时(秒) | 最长耗时(秒) | 总Token数 | 平均Token数 |
|---|---|---|---|---|---|---|---|
| DeepSeek | 10 | 5.09 | 30.54 | 21.82 | 46.24 | 106885 | 10688 |
| Gemini | 10 | 10.18 | 61.09 | 26.46 | 82.6 | 187367 | 18737 |
| Kimi | 10 | 4.41 | 26.45 | 17.95 | 40.52 | 116457 | 11646 |

## 2. 关键发现

- **最快平均速度**: Kimi (26.45 秒/篇)
- **最慢平均速度**: Gemini (61.09 秒/篇)
- **总时间最短**: Kimi (4.41 分钟)
- **最多Token消耗**: Gemini (平均 18737 tokens/篇)

- **速度差异**: Gemini 比 Kimi 慢 2.31 倍

## 3. 各模型详细数据

### DeepSeek

- 论文数: 10
- 总耗时: 5.09 分钟 (305.4 秒)
- 平均耗时: 30.54 秒/篇
- 最短耗时: 21.82 秒
- 最长耗时: 46.24 秒
- 总Token消耗: 106,885
- 平均Token消耗: 10,688 tokens/篇
- 抽取效率: 1.33 个知识元素/秒
- 详细数据: `deepseek/paper_time_stats.csv`

### Gemini

- 论文数: 10
- 总耗时: 10.18 分钟 (610.94 秒)
- 平均耗时: 61.09 秒/篇
- 最短耗时: 26.46 秒
- 最长耗时: 82.6 秒
- 总Token消耗: 187,367
- 平均Token消耗: 18,737 tokens/篇
- 抽取效率: 0.86 个知识元素/秒
- 详细数据: `gemini/paper_time_stats.csv`

### Kimi

- 论文数: 10
- 总耗时: 4.41 分钟 (264.45 秒)
- 平均耗时: 26.45 秒/篇
- 最短耗时: 17.95 秒
- 最长耗时: 40.52 秒
- 总Token消耗: 116,457
- 平均Token消耗: 11,646 tokens/篇
- 抽取效率: 1.34 个知识元素/秒
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

1. **Kimi**: 26.45 秒/篇
2. **DeepSeek**: 30.54 秒/篇
3. **Gemini**: 61.09 秒/篇

### Token消耗排名（从少到多）

1. **DeepSeek**: 10,688 tokens/篇
2. **Kimi**: 11,646 tokens/篇
3. **Gemini**: 18,737 tokens/篇

### 抽取效率排名（知识元素/秒）

1. **Kimi**: 1.34 个/秒
2. **DeepSeek**: 1.33 个/秒
3. **Gemini**: 0.86 个/秒
