# 文件迁移计划

本文档记录了文件整理和迁移的详细计划。

## 📋 迁移概览

### 阶段1: 论文文件迁移 ✅ 准备中
- **源位置**: `论文文献/markdown/`
- **目标位置**: `data/raw/papers/`
- **文件数量**: ~100篇 Markdown文件
- **操作**: 复制（保留原文件作为备份）

### 阶段2: 提示词文件整理
- **源位置**: 各EXP目录下的 `prompt/` 文件夹
- **目标位置**: `config/prompts/`
- **命名规范**: `{实验名}_{用途}_{模型}.txt`

### 阶段3: 实验结果数据整理
- **源位置**: 各EXP目录下的 `数据结果/`
- **目标位置**: `data/results/exp0X_{name}/`
- **保留结构**: 保持原有的子目录结构

### 阶段4: 实验代码存档
- **源位置**: 各EXP目录下的 `code/`
- **目标位置**: `experiments/exp0X_{name}/legacy_code/`
- **目的**: 保存原始代码快照，便于对比

---

## 📁 详细迁移映射

### 1. 论文文件 (Markdown)

```
源: 论文文献/markdown/*.md
↓
目标: data/raw/papers/*.md
```

**操作命令** (PowerShell):
```powershell
# 复制所有Markdown论文
Copy-Item "论文文献\markdown\*.md" "data\raw\papers\" -Force
```

**预期结果**: 约100个 `.md` 文件

---

### 2. 提示词文件

#### EXP-01 提示词

| 源文件 | 用途 | 目标文件 |
|--------|------|----------|
| `EXP-1/抽取/prompt/prompt.txt` | 实体关系抽取 | `config/prompts/exp01_extraction_prompt.txt` |
| `EXP-1/抽取/prompt/gemini_entity_relation_evaluation_prompt.md.txt` | 评估 | `config/prompts/exp01_evaluation_prompt.txt` |
| `EXP-1/指标统计计算/指标三：模型打分/prompt/prompt.txt` | 模型打分 | `config/prompts/exp01_scoring_prompt.txt` |

**操作命令**:
```powershell
# EXP-01 提示词
Copy-Item "EXP-1\抽取\prompt\prompt.txt" "config\prompts\exp01_extraction_prompt.txt"
Copy-Item "EXP-1\抽取\prompt\gemini_entity_relation_evaluation_prompt.md.txt" "config\prompts\exp01_evaluation_prompt.txt"
Copy-Item "EXP-1\指标统计计算\指标三：模型打分\prompt\prompt.txt" "config\prompts\exp01_scoring_prompt.txt"
```

#### EXP-02 提示词

| 源文件 | 用途 | 目标文件 |
|--------|------|----------|
| `EXP-2/抽取/prompt/prompt.txt` | 实体关系抽取 | `config/prompts/exp02_extraction_prompt.txt` |
| `EXP-2/抽取/评估/prompt/prompt.txt` | 评估 | `config/prompts/exp02_evaluation_prompt.txt` |
| `EXP-2/依存句法分析/实体对抽取/prompt/prompt.txt` | 依存分析 | `config/prompts/exp02_dependency_prompt.txt` |
| `EXP-2/指标统计计算/指标三：模型打分/prompt/prompt.txt` | 模型打分 | `config/prompts/exp02_scoring_prompt.txt` |

**操作命令**:
```powershell
# EXP-02 提示词
Copy-Item "EXP-2\抽取\prompt\prompt.txt" "config\prompts\exp02_extraction_prompt.txt"
Copy-Item "EXP-2\抽取\评估\prompt\prompt.txt" "config\prompts\exp02_evaluation_prompt.txt"
Copy-Item "EXP-2\依存句法分析\实体对抽取\prompt\prompt.txt" "config\prompts\exp02_dependency_prompt.txt"
Copy-Item "EXP-2\指标统计计算\指标三：模型打分\prompt\prompt.txt" "config\prompts\exp02_scoring_prompt.txt"
```

#### EXP-03 提示词

| 源文件 | 用途 | 目标文件 |
|--------|------|----------|
| `EXP-3/抽取/评估/prompt/prompt.txt` | 评估 | `config/prompts/exp03_evaluation_prompt.txt` |
| `EXP-3/主题聚类/prompt/prompt.txt` | 主题聚类 | `config/prompts/exp03_clustering_prompt.txt` |

**操作命令**:
```powershell
# EXP-03 提示词
Copy-Item "EXP-3\抽取\评估\prompt\prompt.txt" "config\prompts\exp03_evaluation_prompt.txt"
Copy-Item "EXP-3\主题聚类\prompt\prompt.txt" "config\prompts\exp03_clustering_prompt.txt"
```

#### EXP-04 提示词

| 源文件 | 用途 | 目标文件 |
|--------|------|----------|
| `EXP-4/抽取/评估/prompt/prompt.txt` | 评估 | `config/prompts/exp04_evaluation_prompt.txt` |
| `EXP-4/主题聚类/prompt/prompt.txt` | 主题聚类 | `config/prompts/exp04_clustering_prompt.txt` |
| `EXP-4/指标统计计算/指标三：模型打分/prompt/prompt_eva.txt` | 模型打分 | `config/prompts/exp04_scoring_prompt.txt` |

**操作命令**:
```powershell
# EXP-04 提示词
Copy-Item "EXP-4\抽取\评估\prompt\prompt.txt" "config\prompts\exp04_evaluation_prompt.txt"
Copy-Item "EXP-4\主题聚类\prompt\prompt.txt" "config\prompts\exp04_clustering_prompt.txt"
Copy-Item "EXP-4\指标统计计算\指标三：模型打分\prompt\prompt_eva.txt" "config\prompts\exp04_scoring_prompt.txt"
```

---

### 3. 实验结果数据

#### EXP-01 数据

```
源目录结构:
EXP-1/
├── 抽取/数据结果/
├── 指标统计计算/
│   ├── 指标二：实体关系密度/统计结果/
│   └── 指标三：模型打分/打分结果/

目标结构:
data/results/exp01_baseline/
├── extraction/          # 从 抽取/数据结果/
├── density/            # 从 指标二/统计结果/
└── scoring/            # 从 指标三/打分结果/
```

**操作命令**:
```powershell
# EXP-01 结果数据
New-Item -ItemType Directory -Force -Path "data\results\exp01_baseline\extraction"
New-Item -ItemType Directory -Force -Path "data\results\exp01_baseline\density"
New-Item -ItemType Directory -Force -Path "data\results\exp01_baseline\scoring"

# 复制数据（如果目录存在）
if (Test-Path "EXP-1\抽取\数据结果") {
    Copy-Item "EXP-1\抽取\数据结果\*" "data\results\exp01_baseline\extraction\" -Recurse -Force
}
```

#### EXP-02 数据

```
目标结构:
data/results/exp02_improved/
├── extraction/
├── evaluation/
├── dependency/
├── density/
└── scoring/
```

#### EXP-03 数据

```
目标结构:
data/results/exp03_clustering/
├── extraction/
├── evaluation/
└── clustering/
```

#### EXP-04 数据

```
目标结构:
data/results/exp04_final/
├── extraction/
├── evaluation/
├── density/
├── consistency/
├── scoring/
└── clustering/
```

---

### 4. 实验代码存档

```
目标结构:
experiments/exp01_baseline/
├── README.md           # 已创建
├── legacy_code/        # 原始代码存档
│   ├── extraction/
│   ├── evaluation/
│   └── utils/
└── config.yaml         # 待创建

experiments/exp02_improved/
├── README.md
├── legacy_code/
└── config.yaml

experiments/exp03_clustering/
├── README.md
├── legacy_code/
└── config.yaml

experiments/exp04_final/
├── README.md           # 已创建
├── legacy_code/
└── config.yaml
```

**操作命令**:
```powershell
# 为每个实验创建 legacy_code 目录
New-Item -ItemType Directory -Force -Path "experiments\exp01_baseline\legacy_code"
New-Item -ItemType Directory -Force -Path "experiments\exp02_improved\legacy_code"
New-Item -ItemType Directory -Force -Path "experiments\exp03_clustering\legacy_code"
New-Item -ItemType Directory -Force -Path "experiments\exp04_final\legacy_code"

# 复制原始代码
Copy-Item "EXP-1\抽取\code\*" "experiments\exp01_baseline\legacy_code\" -Recurse -Force
Copy-Item "EXP-2\抽取\code\*" "experiments\exp02_improved\legacy_code\" -Recurse -Force
Copy-Item "EXP-3\抽取\code\*" "experiments\exp03_clustering\legacy_code\" -Recurse -Force
Copy-Item "EXP-4\抽取\code\*" "experiments\exp04_final\legacy_code\" -Recurse -Force
```

---

## 🚀 快速执行脚本

创建一个PowerShell脚本一次性执行所有迁移：

```powershell
# 文件: scripts\migrate_files.ps1

Write-Host "开始文件迁移..." -ForegroundColor Green

# 1. 迁移论文文件
Write-Host "`n[1/4] 迁移论文文件..." -ForegroundColor Cyan
Copy-Item "论文文献\markdown\*.md" "data\raw\papers\" -Force
Write-Host "✓ 论文文件迁移完成" -ForegroundColor Green

# 2. 迁移提示词
Write-Host "`n[2/4] 迁移提示词文件..." -ForegroundColor Cyan
# EXP-01
Copy-Item "EXP-1\抽取\prompt\prompt.txt" "config\prompts\exp01_extraction_prompt.txt" -Force
Copy-Item "EXP-1\指标统计计算\指标三：模型打分\prompt\prompt.txt" "config\prompts\exp01_scoring_prompt.txt" -Force
# EXP-02
Copy-Item "EXP-2\抽取\prompt\prompt.txt" "config\prompts\exp02_extraction_prompt.txt" -Force
Copy-Item "EXP-2\指标统计计算\指标三：模型打分\prompt\prompt.txt" "config\prompts\exp02_scoring_prompt.txt" -Force
# EXP-03
Copy-Item "EXP-3\主题聚类\prompt\prompt.txt" "config\prompts\exp03_clustering_prompt.txt" -Force
# EXP-04
Copy-Item "EXP-4\抽取\评估\prompt\prompt.txt" "config\prompts\exp04_evaluation_prompt.txt" -Force
Copy-Item "EXP-4\主题聚类\prompt\prompt.txt" "config\prompts\exp04_clustering_prompt.txt" -Force
Write-Host "✓ 提示词文件迁移完成" -ForegroundColor Green

# 3. 创建实验目录结构
Write-Host "`n[3/4] 创建实验目录结构..." -ForegroundColor Cyan
$experiments = @("exp01_baseline", "exp02_improved", "exp03_clustering", "exp04_final")
foreach ($exp in $experiments) {
    New-Item -ItemType Directory -Force -Path "experiments\$exp\legacy_code" | Out-Null
    New-Item -ItemType Directory -Force -Path "data\results\$exp" | Out-Null
}
Write-Host "✓ 目录结构创建完成" -ForegroundColor Green

# 4. 复制原始代码
Write-Host "`n[4/4] 存档原始代码..." -ForegroundColor Cyan
Copy-Item "EXP-1\抽取\code\*" "experiments\exp01_baseline\legacy_code\" -Recurse -Force
Copy-Item "EXP-2\抽取\code\*" "experiments\exp02_improved\legacy_code\" -Recurse -Force  
Copy-Item "EXP-3\抽取\code\*" "experiments\exp03_clustering\legacy_code\" -Recurse -Force
Copy-Item "EXP-4\抽取\code\*" "experiments\exp04_final\legacy_code\" -Recurse -Force
Write-Host "✓ 代码存档完成" -ForegroundColor Green

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Yellow  
Write-Host "=" -NoNewline -ForegroundColor Red
Write-Host " 文件迁移全部完成！" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Red
Write-Host "=" -NoNewline -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Green

Write-Host "`n查看迁移结果:" -ForegroundColor Cyan
Write-Host "  python scripts\show_tree.py --depth 3" -ForegroundColor Yellow
```

---

## ✅ 迁移检查清单

执行迁移后，请检查：

- [ ] `data/raw/papers/` 包含所有Markdown论文
- [ ] `config/prompts/` 包含所有提示词文件，命名规范
- [ ] `experiments/exp0X_*/legacy_code/` 包含原始代码
- [ ] `data/results/exp0X_*/` 目录已创建
- [ ] 原始 `EXP-*` 目录保持不变（作为备份）

---

## 📝 注意事项

1. **所有操作都是复制，不会删除原文件**
2. **原始EXP-*目录保持不变，可随时回滚**
3. **如有冲突，使用 `-Force` 参数覆盖**
4. **迁移后原目录可以重命名为 `_archived_EXP-*` 标记**

---

**创建时间**: 2025年10月17日  
**更新时间**: 2025年10月17日
