# 统计分析模块

## 📊 功能说明

该模块用于统计和分析实体关系抽取结果。

## 📁 文件说明

- `stats_extraction.py` - 抽取结果统计脚本

## 🚀 使用方法

### 1. 安装依赖

```powershell
pip install pandas openpyxl
```

### 2. 运行统计脚本

```powershell
# 确保在项目根目录
cd E:\entities\experiments\exp01_baseline

# 运行统计
python src/evaluation/stats_extraction.py
```

### 3. 查看结果

统计结果保存在 `outputs/statistics/` 目录：

- **extraction_stats_detailed.csv** - CSV 格式详细数据
- **extraction_stats_detailed.xlsx** - Excel 多 Sheet 数据
  - Sheet "All": 所有模型的数据
  - Sheet "DeepSeek": DeepSeek 模型数据
  - Sheet "Gemini": Gemini 模型数据
  - Sheet "Kimi": Kimi 模型数据
- **extraction_stats_summary.json** - JSON 格式汇总统计

## 📈 统计指标

### 按论文统计（详细数据）

| 列名 | 说明 |
|------|------|
| `paper` | 论文文件名（不含扩展名） |
| `model` | 模型名称（DeepSeek/Gemini/Kimi） |
| `entity_count` | 实体数量 |
| `entity_type_count` | 实体类型数量 |
| `relation_count` | 关系数量 |
| `relation_type_count` | 关系类型数量 |

### 按模型汇总（汇总数据）

每个模型包含以下统计：

- `paper_count` - 论文数量
- `entity_count_total` - 实体总数
- `entity_count_avg` - 实体平均数
- `entity_count_median` - 实体中位数
- `entity_count_min` - 实体最小值
- `entity_count_max` - 实体最大值
- `entity_type_count_avg` - 实体类型平均数
- `entity_type_count_median` - 实体类型中位数
- `relation_count_total` - 关系总数
- `relation_count_avg` - 关系平均数
- `relation_count_median` - 关系中位数
- `relation_count_min` - 关系最小值
- `relation_count_max` - 关系最大值
- `relation_type_count_avg` - 关系类型平均数
- `relation_type_count_median` - 关系类型中位数

## 💡 示例输出

### 控制台输出

```
================================================================================
📊 实体关系抽取结果统计
================================================================================

目标目录:
  - DeepSeek: E:\entities\experiments\exp01_baseline\outputs\extractions\deepseek\priority
  - Gemini: E:\entities\experiments\exp01_baseline\outputs\extractions\gemini\priority
  - Kimi: E:\entities\experiments\exp01_baseline\outputs\extractions\kimi\priority

📊 统计 DeepSeek 模型...
   目录: E:\entities\experiments\exp01_baseline\outputs\extractions\deepseek\priority
   文件数: 50
   ✅ 统计完成: 50 篇论文
   实体总数: 2250
   关系总数: 1800

📊 统计 Gemini 模型...
   目录: E:\entities\experiments\exp01_baseline\outputs\extractions\gemini\priority
   文件数: 50
   ✅ 统计完成: 50 篇论文
   实体总数: 2100
   关系总数: 1650

📊 统计 Kimi 模型...
   目录: E:\entities\experiments\exp01_baseline\outputs\extractions\kimi\priority
   文件数: 50
   ✅ 统计完成: 50 篇论文
   实体总数: 2180
   关系总数: 1720

💾 详细统计已保存: outputs\statistics\extraction_stats_detailed.csv
💾 Excel 统计已保存: outputs\statistics\extraction_stats_detailed.xlsx
💾 汇总统计已保存: outputs\statistics\extraction_stats_summary.json

================================================================================
📈 汇总统计
================================================================================

总论文数: 50

【DeepSeek】
  论文数: 50
  实体: 2250 个 (均值: 45.0, 中位数: 44)
  实体类型: 均值 8.5, 中位数 8
  关系: 1800 个 (均值: 36.0, 中位数: 35)
  关系类型: 均值 6.2, 中位数 6

【Gemini】
  论文数: 50
  实体: 2100 个 (均值: 42.0, 中位数: 41)
  实体类型: 均值 8.0, 中位数 8
  关系: 1650 个 (均值: 33.0, 中位数: 32)
  关系类型: 均值 5.8, 中位数 6

【Kimi】
  论文数: 50
  实体: 2180 个 (均值: 43.6, 中位数: 43)
  实体类型: 均值 8.2, 中位数 8
  关系: 1720 个 (均值: 34.4, 中位数: 34)
  关系类型: 均值 6.0, 中位数 6

================================================================================
✅ 统计完成
================================================================================
```

### JSON 汇总示例

```json
{
  "total_papers": 50,
  "by_model": {
    "DeepSeek": {
      "paper_count": 50,
      "entity_count_total": 2250,
      "entity_count_avg": 45.0,
      "entity_count_median": 44,
      "entity_count_min": 28,
      "entity_count_max": 65,
      "entity_type_count_avg": 8.5,
      "entity_type_count_median": 8,
      "relation_count_total": 1800,
      "relation_count_avg": 36.0,
      "relation_count_median": 35,
      "relation_count_min": 20,
      "relation_count_max": 52,
      "relation_type_count_avg": 6.2,
      "relation_type_count_median": 6
    },
    "Gemini": { ... },
    "Kimi": { ... }
  },
  "overall": {
    "entity_count_total": 6530,
    "entity_count_avg": 43.53,
    "relation_count_total": 5170,
    "relation_count_avg": 34.47
  }
}
```

## 🔧 自定义统计

您可以修改 `stats_extraction.py` 来添加自定义统计逻辑：

```python
# 示例：统计特定实体类型的数量
def count_specific_entity_type(json_file: Path, entity_type: str) -> int:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entities = data.get('entities', [])
    return sum(1 for e in entities if e.get('type') == entity_type)
```

## 📝 注意事项

1. **只统计 priority 论文**：脚本仅统计 `outputs/extractions/{model}/priority/` 目录下的文件
2. **需要完整的 JSON 结构**：确保 JSON 文件包含 `entities` 和 `relations` 字段
3. **自动忽略错误文件**：如果某个 JSON 文件读取失败，会跳过并继续统计

## 🎯 使用场景

- ✅ 对比不同模型的抽取效果
- ✅ 评估抽取质量（实体/关系数量、类型多样性）
- ✅ 生成实验报告数据
- ✅ 质量检查和异常检测

## 📧 问题反馈

如有问题或建议，请提交 Issue 或联系维护者。
