# 知识图谱构建项目 (Knowledge Graph Construction)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📖 项目简介

本项目是一个基于大语言模型的知识图谱构建研究项目，专注于从航空领域学术论文中自动抽取实体和关系，构建领域知识图谱。

### 主要功能

- **实体关系抽取**: 使用多个LLM模型（Gemini、DeepSeek、Kimi等）从论文中抽取实体和关系
- **模型评估**: 多维度评估抽取质量（密度、一致性、准确性等）
- **主题聚类**: 对抽取的知识进行主题分类和聚类分析
- **元数据增强**: 自动填充论文元数据（作者、单位、发表时间等）

## 🗂️ 项目结构

```
.
├── README.md                    # 项目说明文档
├── requirements.txt             # Python依赖列表
├── setup.py                     # 项目安装配置
├── .gitignore                   # Git忽略文件配置
│
├── config/                      # 配置文件目录
│   ├── config.yaml             # 主配置文件
│   └── prompts/                # LLM提示词模板
│
├── data/                        # 数据目录
│   ├── raw/                    # 原始数据
│   │   └── papers/             # 原始论文（PDF和Markdown）
│   ├── processed/              # 处理后的数据
│   └── results/                # 实验结果数据
│
├── src/                        # 源代码
│   ├── extraction/             # 实体关系抽取模块
│   ├── evaluation/             # 评估指标计算模块
│   ├── clustering/             # 主题聚类模块
│   ├── preprocessing/          # 数据预处理模块
│   └── utils/                  # 工具函数
│
├── experiments/                # 实验记录和配置
│   ├── exp01_baseline/         # 实验1：基线实验
│   ├── exp02_improved/         # 实验2：改进方法
│   ├── exp03_clustering/       # 实验3：聚类实验
│   └── exp04_final/            # 实验4：最终版本
│
├── notebooks/                  # Jupyter notebooks（探索性分析）
├── tests/                      # 单元测试
├── docs/                       # 项目文档
└── scripts/                    # 辅助脚本
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Conda (推荐) 或 virtualenv

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/Augusteing/entities.git
cd entities
```

2. **创建虚拟环境**
```bash
conda create -n kg-construction python=3.10
conda activate kg-construction
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置API密钥**
```bash
# 在config/config.yaml中配置你的API密钥
# 或设置环境变量
export HIAPI_API_KEY="your-api-key-here"
```

### 基本使用

1. **实体关系抽取**
```bash
python scripts/run_extraction.py --model gemini --input data/raw/papers --output data/results
```

2. **评估指标计算**
```bash
python scripts/run_evaluation.py --experiment exp04_final
```

3. **主题聚类**
```bash
python scripts/run_clustering.py --input data/results/entities
```

## 📊 实验说明

### 实验1 (EXP-1): 基线实验
- **目标**: 建立基线方法，测试基本抽取能力
- **方法**: 使用单一模型直接抽取
- **指标**: 实体关系密度、一致性

### 实验2 (EXP-2): 改进实验
- **目标**: 改进抽取质量
- **方法**: 优化提示词，增加元数据填充
- **指标**: 模型打分、准确率提升

### 实验3 (EXP-3): 聚类实验
- **目标**: 实现主题聚类
- **方法**: 依存句法分析 + 主题聚类
- **指标**: 聚类质量评估

### 实验4 (EXP-4): 最终版本
- **目标**: 综合所有改进，产出最终结果
- **方法**: 完整流程 + 多模型对比
- **指标**: 全方位评估

详细实验记录请查看 [实验文档](docs/experiments.md)

## 📈 评估指标

本项目使用以下评估指标：

1. **实体关系密度**: 千字实体/关系数量
2. **一致性**: 多次抽取结果的一致性评分
3. **模型打分**: 使用评估模型对抽取质量打分
4. **准确率**: 人工标注数据上的准确率

## 🛠️ 开发指南

### 代码规范

- 遵循 PEP 8 Python代码规范
- 使用类型注解
- 编写文档字符串
- 添加单元测试

### 提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
refactor: 代码重构
test: 测试相关
chore: 构建/工具链相关
```

## 📝 引用

如果本项目对你的研究有帮助，请引用：

```bibtex
@software{kg_construction_2025,
  title={Knowledge Graph Construction from Academic Papers},
  author={Your Name},
  year={2025},
  url={https://github.com/Augusteing/entities}
}
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

- 项目维护者: [Your Name]
- Email: [your.email@example.com]
- GitHub: [@Augusteing](https://github.com/Augusteing)

## 🙏 致谢

感谢所有为本项目做出贡献的研究者和开发者。

---

**最后更新时间**: 2025年10月17日
