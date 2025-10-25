# 项目迁移指南

本指南说明如何将旧项目结构迁移到新的标准化结构。

## 📋 迁移前准备

### 1. 备份原始数据
```bash
# 建议在迁移前先备份整个项目
# 原项目已经是副本，但建议再做一次备份
```

### 2. 确认环境
```bash
# 确认Python环境
python --version  # 应该是 3.10+

# 激活conda环境
conda activate base
```

## 🗂️ 文件迁移对照表

### 数据文件迁移

| 原位置 | 新位置 | 说明 |
|-------|-------|------|
| `论文文献/paper/` | `data/raw/papers/` | 原始PDF论文 |
| `论文文献/markdown/` | `data/raw/papers/` | Markdown格式论文 |
| `EXP-*/抽取/数据结果/` | `data/results/exp0*/extraction/` | 抽取结果 |
| `EXP-*/指标统计计算/*/统计结果/` | `data/results/exp0*/evaluation/` | 评估结果 |
| `EXP-*/主题聚类/数据结果/` | `data/results/exp0*/clustering/` | 聚类结果 |

### 代码文件迁移

| 原位置 | 新位置 | 说明 |
|-------|-------|------|
| `EXP-*/抽取/code/抽取脚本/exact_*.py` | `src/extraction/` | 抽取脚本 |
| `EXP-*/指标统计计算/*/code/*.py` | `src/evaluation/` | 评估脚本 |
| `EXP-*/主题聚类/code/*.py` | `src/clustering/` | 聚类脚本 |
| `论文文献/code/transfer.py` | `src/preprocessing/` | 预处理脚本 |

### 配置文件迁移

| 原位置 | 新位置 | 说明 |
|-------|-------|------|
| `EXP-*/抽取/prompt/` | `config/prompts/` | 提示词模板 |
| `EXP-*/指标统计计算/*/prompt/` | `config/prompts/` | 评估提示词 |

### 实验记录迁移

| 原位置 | 新位置 | 说明 |
|-------|-------|------|
| `EXP-1/` | `experiments/exp01_baseline/` | 实验1 |
| `EXP-2/` | `experiments/exp02_improved/` | 实验2 |
| `EXP-3/` | `experiments/exp03_clustering/` | 实验3 |
| `EXP-4/` | `experiments/exp04_final/` | 实验4 |
| `实验文档.pdf` | `docs/experiments.md` | 实验文档（已转换） |

## 🔧 迁移步骤

### 步骤1: 迁移论文数据
```bash
# 迁移PDF论文（如果需要保留）
# 注意：PDF文件较大，可以选择不迁移，只保留Markdown

# 迁移Markdown论文
xcopy "论文文献\markdown\*.md" "data\raw\papers\" /Y
```

### 步骤2: 整理实验结果
每个实验的结果按照以下结构组织：
```
experiments/exp0X_name/
├── README.md           # 实验说明
├── config.yaml         # 实验配置
├── data/              # 实验专属数据
├── results/           # 实验结果
│   ├── extraction/    # 抽取结果
│   ├── evaluation/    # 评估结果
│   └── clustering/    # 聚类结果
└── notebooks/         # 分析笔记本
```

### 步骤3: 重构代码
代码需要进行模块化重构：

1. **提取通用函数到utils**
   - 文件读写 → `src/utils/file_utils.py`
   - 配置加载 → `src/utils/config_loader.py`
   - 日志处理 → `src/utils/logger.py`

2. **模块化业务逻辑**
   - 抽取逻辑 → `src/extraction/`
   - 评估逻辑 → `src/evaluation/`
   - 聚类逻辑 → `src/clustering/`

3. **创建统一入口脚本**
   - `scripts/run_extraction.py`
   - `scripts/run_evaluation.py`
   - `scripts/run_clustering.py`

### 步骤4: 更新配置文件
1. 将硬编码的路径移到 `config/config.yaml`
2. 将API密钥移到环境变量
3. 将提示词移到 `config/prompts/`

### 步骤5: 添加文档
- [x] README.md（已创建）
- [x] docs/experiments.md（已创建）
- [ ] docs/api_reference.md（待创建）
- [ ] docs/user_guide.md（待创建）

## ⚠️ 注意事项

### 1. 路径更新
所有脚本中的硬编码路径需要更新：
```python
# 旧代码
paper_folder = Path("E:\知识图谱构建\9.15之前的实验\文献处理\paper")

# 新代码
from src.utils.config_loader import load_config
config = load_config()
paper_folder = Path(config['paths']['raw_papers'])
```

### 2. 导入路径更新
```python
# 旧代码
from code.utils import some_function

# 新代码
from src.utils import some_function
```

### 3. API密钥管理
```python
# 旧代码
api_key = "sk-xxxxx"

# 新代码
import os
api_key = os.getenv("HIAPI_API_KEY")
```

### 4. 日志管理
```python
# 旧代码
print("Processing...")

# 新代码
from src.utils.logger import setup_logger
logger = setup_logger()
logger.info("Processing...")
```

## 🚀 迁移后验证

### 1. 检查文件结构
```bash
tree /F /A > project_structure.txt
# 检查是否符合标准结构
```

### 2. 测试导入
```python
# 测试各模块是否能正常导入
from src.utils import load_config
from src.extraction import EntityRelationExtractor
from src.evaluation import calculate_density
```

### 3. 运行测试
```bash
# 运行示例脚本测试
python scripts/run_extraction.py --help
```

## 📝 迁移检查清单

- [x] 创建新目录结构
- [x] 创建核心文档（README, .gitignore等）
- [x] 创建配置文件
- [x] 创建模块初始化文件
- [ ] 迁移论文数据
- [ ] 迁移实验结果
- [ ] 重构代码文件
- [ ] 迁移配置和提示词
- [ ] 更新所有路径引用
- [ ] 测试基本功能
- [ ] 编写使用文档
- [ ] 清理旧文件（可选）

## 💡 建议

1. **分批迁移**: 不要一次性迁移所有内容，先迁移一个实验验证流程
2. **保留原文件**: 在确认新结构工作正常前，不要删除原文件
3. **版本控制**: 使用git追踪迁移过程中的变化
4. **持续测试**: 每迁移一部分就测试一次

---

**创建时间**: 2025年10月17日
