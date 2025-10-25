# RAG 模型抽取时间统计报告

生成时间: 2025-10-20 17:01:42

## 1. 模型时间对比汇总

| 模型 | 论文数 | 总耗时(分钟) | 平均耗时(秒) | 最短耗时(秒) | 最长耗时(秒) | 总Token数 | 平均Token数 |
|---|---|---|---|---|---|---|---|
| DeepSeek | 10 | 8.21 | 49.27 | 36.29 | 62.44 | 226531 | 22653 |
| Gemini | 10 | 14.12 | 84.75 | 52.45 | 108.32 | 327880 | 32788 |
| Kimi | 10 | 3.5 | 21.0 | 12.38 | 28.22 | 241479 | 24148 |

## 2. 关键发现

- **最快平均速度**: Kimi (21.0 秒/篇)
- **最慢平均速度**: Gemini (84.75 秒/篇)
- **总时间最短**: Kimi (3.5 分钟)
- **最多Token消耗**: Gemini (平均 32788 tokens/篇)

- **速度差异**: Gemini 比 Kimi 慢 4.04 倍

## 3. 各模型详细数据

### DeepSeek

- 论文数: 10
- 总耗时: 8.21 分钟 (492.69 秒)
- 平均耗时: 49.27 秒/篇
- 最短耗时: 36.29 秒
- 最长耗时: 62.44 秒
- 总Token消耗: 226,531
- 平均Token消耗: 22,653 tokens/篇
- 抽取效率: 0.93 个知识元素/秒
- 详细数据: `deepseek/paper_time_stats.csv`

### Gemini

- 论文数: 10
- 总耗时: 14.12 分钟 (847.47 秒)
- 平均耗时: 84.75 秒/篇
- 最短耗时: 52.45 秒
- 最长耗时: 108.32 秒
- 总Token消耗: 327,880
- 平均Token消耗: 32,788 tokens/篇
- 抽取效率: 0.69 个知识元素/秒
- 详细数据: `gemini/paper_time_stats.csv`

### Kimi

- 论文数: 10
- 总耗时: 3.5 分钟 (209.99 秒)
- 平均耗时: 21.0 秒/篇
- 最短耗时: 12.38 秒
- 最长耗时: 28.22 秒
- 总Token消耗: 241,479
- 平均Token消耗: 24,148 tokens/篇
- 抽取效率: 1.76 个知识元素/秒
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

1. **Kimi**: 21.0 秒/篇
2. **DeepSeek**: 49.27 秒/篇
3. **Gemini**: 84.75 秒/篇

### Token消耗排名（从少到多）

1. **DeepSeek**: 22,653 tokens/篇
2. **Kimi**: 24,148 tokens/篇
3. **Gemini**: 32,788 tokens/篇

### 抽取效率排名（知识元素/秒）

1. **Kimi**: 1.76 个/秒
2. **DeepSeek**: 0.93 个/秒
3. **Gemini**: 0.69 个/秒
