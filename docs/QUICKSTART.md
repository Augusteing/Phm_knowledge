# 快速开始指南

本指南帮助你快速上手使用本项目。

## 🚀 5分钟快速开始

### 1. 环境准备

```bash
# 确认Python版本
python --version  # 需要 3.10+

# 激活conda环境（如果使用conda）
conda activate base
```

### 2. 安装依赖

```bash
# 安装必要的依赖包
pip install -r requirements.txt
```

### 3. 配置API密钥

在PowerShell中设置环境变量：

```powershell
# 设置API密钥（替换为你的真实密钥）
$env:HIAPI_API_KEY = "sk-your-api-key-here"
```

或者直接修改 `config/config.yaml` 文件中的 `api_key` 字段。

### 4. 查看项目结构

```bash
# 查看项目目录树
python scripts\show_tree.py --depth 3
```

### 5. 运行示例

```bash
# 查看已有的实验结果
ls experiments\

# 查看实验文档
cat docs\experiments.md
```

## 📚 详细使用指南

### 文件组织建议

#### 如果你要开始新实验

1. 在 `experiments/` 下创建新的实验目录：
```bash
mkdir experiments\exp05_my_experiment
```

2. 复制实验README模板：
```bash
copy experiments\exp01_baseline\README.md experiments\exp05_my_experiment\README.md
```

3. 创建实验子目录：
```bash
cd experiments\exp05_my_experiment
mkdir data results notebooks
```

#### 如果你要添加新功能

1. 在 `src/` 对应模块下添加代码：
```python
# 例如：src/extraction/my_extractor.py
```

2. 在模块的 `__init__.py` 中导出：
```python
from .my_extractor import MyExtractor
__all__ = [..., "MyExtractor"]
```

### 常用操作

#### 1. 加载配置

```python
from src.utils import load_config

# 加载配置
config = load_config("config/config.yaml")

# 获取API密钥
api_key = config['api']['api_key']

# 获取数据路径
data_root = config['paths']['data_root']
```

#### 2. 设置日志

```python
from src.utils import setup_logger

# 设置日志
logger = setup_logger(
    name="my_script",
    level="INFO",
    log_file="logs/my_script.log",
    console=True
)

# 使用日志
logger.info("Processing started...")
logger.error("An error occurred")
```

#### 3. 读写文件

```python
from src.utils import read_json, write_json, read_markdown

# 读取JSON
data = read_json("data/results/output.json")

# 写入JSON
write_json(data, "data/processed/processed.json")

# 读取Markdown
content = read_markdown("data/raw/papers/paper1.md")
```

#### 4. 列出文件

```python
from src.utils import list_files

# 列出所有Markdown文件
papers = list_files("data/raw/papers", pattern="*.md")

# 递归列出所有JSON文件
results = list_files("data/results", pattern="*.json", recursive=True)
```

### 实验工作流

#### 典型实验流程

1. **准备数据**
   ```bash
   # 将论文放到 data/raw/papers/
   ```

2. **创建实验目录**
   ```bash
   mkdir experiments\my_exp
   cd experiments\my_exp
   mkdir data results notebooks
   ```

3. **编写抽取脚本**
   ```python
   # 创建 my_extraction.py
   from src.utils import load_config, setup_logger
   from src.extraction import EntityRelationExtractor
   
   # 初始化
   config = load_config()
   logger = setup_logger()
   
   # 执行抽取
   # ...
   ```

4. **运行实验**
   ```bash
   python my_extraction.py
   ```

5. **评估结果**
   ```bash
   python my_evaluation.py
   ```

6. **记录结果**
   - 更新实验README
   - 保存结果到 results/
   - 更新 docs/experiments.md

## 🔧 配置说明

### 主配置文件: config/config.yaml

```yaml
# API配置
api:
  base_url: "https://api.siliconflow.cn/v1"
  api_key: ${HIAPI_API_KEY}  # 从环境变量读取
  default_model: "gemini-2.5-pro"

# 路径配置
paths:
  data_root: "data"
  raw_papers: "data/raw/papers"
  results: "data/results"

# 抽取配置
extraction:
  batch_size: 10
  max_files: 0  # 0表示无限制
  overwrite: false
```

### 修改配置

你可以通过以下方式修改配置：

1. **直接编辑YAML文件**
2. **通过代码修改**：
```python
from src.utils import load_config, update_config_value

config = load_config()
update_config_value(config, "extraction.batch_size", 20)
```

3. **环境变量覆盖**：
```powershell
$env:HIAPI_API_KEY = "your-key"
```

## 📊 查看实验结果

### 已完成的实验

项目包含4个已完成的实验：

1. **EXP-01**: 基线实验
   - 位置: `experiments/exp01_baseline/`
   - 文档: [README](../experiments/exp01_baseline/README.md)

2. **EXP-02**: 改进实验
   - 位置: `experiments/exp02_improved/`

3. **EXP-03**: 聚类实验
   - 位置: `experiments/exp03_clustering/`

4. **EXP-04**: 最终版本 ⭐
   - 位置: `experiments/exp04_final/`
   - 文档: [README](../experiments/exp04_final/README.md)

### 实验对比

查看所有实验的对比数据：
```bash
cat docs\experiments.md
```

## 🐛 常见问题

### Q1: 导入模块失败

**问题**:
```python
ModuleNotFoundError: No module named 'src'
```

**解决方案**:
```bash
# 方案1: 安装项目包
pip install -e .

# 方案2: 添加到PYTHONPATH
$env:PYTHONPATH = "E:\知识图谱构建\9.15之前的实验 - 副本"
```

### Q2: 配置文件找不到

**问题**:
```
FileNotFoundError: 配置文件不存在: config/config.yaml
```

**解决方案**:
确保在项目根目录运行脚本，或使用绝对路径。

### Q3: API调用失败

**问题**:
```
OpenAI API Error: Unauthorized
```

**解决方案**:
检查API密钥是否正确设置：
```powershell
echo $env:HIAPI_API_KEY
```

### Q4: 旧代码运行失败

**问题**:
旧的实验代码引用了不存在的路径。

**解决方案**:
参考 [迁移指南](MIGRATION.md) 更新路径引用。

## 📖 更多资源

- [完整文档](experiments.md) - 详细的实验记录
- [迁移指南](MIGRATION.md) - 从旧结构迁移的指南
- [API参考](api_reference.md) - 代码API文档（待创建）
- [主README](../README.md) - 项目总览

## 💡 最佳实践

1. **版本控制**: 使用git追踪代码变化
   ```bash
   git init
   git add .
   git commit -m "Initial commit with restructured project"
   ```

2. **环境隔离**: 为项目创建独立的虚拟环境
   ```bash
   conda create -n kg-env python=3.10
   conda activate kg-env
   ```

3. **日志记录**: 始终使用日志而不是print
   ```python
   logger.info("...")  # 而不是 print("...")
   ```

4. **配置管理**: 不要硬编码路径和参数
   ```python
   # ❌ 不好
   path = "E:\\hard\\coded\\path"
   
   # ✅ 好
   config = load_config()
   path = config['paths']['data_root']
   ```

5. **文档更新**: 每次实验后更新相关文档

## 🎯 下一步

- [ ] 熟悉项目结构
- [ ] 查看已有实验结果
- [ ] 阅读实验文档
- [ ] 运行示例代码
- [ ] 开始你的实验！

祝研究顺利！ 🚀

---

**最后更新**: 2025年10月17日
