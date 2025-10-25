# 文件迁移脚本
# 用于将旧项目结构的文件整理到新结构中

Write-Host "================================================" -ForegroundColor Green
Write-Host "  知识图谱项目 - 文件迁移工具" -ForegroundColor Green  
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# 检查是否在项目根目录
if (-not (Test-Path "README.md")) {
    Write-Host "错误: 请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

$ErrorCount = 0
$SuccessCount = 0

# ============================================
# 第1步: 迁移论文文件
# ============================================
Write-Host "[1/4] 迁移论文文件到 data/raw/papers/..." -ForegroundColor Cyan

if (Test-Path "论文文献\markdown") {
    try {
        $mdFiles = Get-ChildItem "论文文献\markdown\*.md" -File
        $count = $mdFiles.Count
        Write-Host "  找到 $count 个Markdown文件"
        
        foreach ($file in $mdFiles) {
            Copy-Item $file.FullName "data\raw\papers\" -Force
        }
        Write-Host "  ✓ 成功复制 $count 个论文文件" -ForegroundColor Green
        $SuccessCount++
    } catch {
        Write-Host "  ✗ 失败: $_" -ForegroundColor Red
        $ErrorCount++
    }
} else {
    Write-Host "  跳过: 论文文献\markdown 目录不存在" -ForegroundColor Yellow
}

# ============================================
# 第2步: 迁移提示词文件
# ============================================
Write-Host "`n[2/4] 迁移提示词文件到 config/prompts/..." -ForegroundColor Cyan

$promptMappings = @(
    # EXP-01
    @{Src="EXP-1\抽取\prompt\prompt.txt"; Dst="config\prompts\exp01_extraction_prompt.txt"},
    @{Src="EXP-1\抽取\prompt\gemini_entity_relation_evaluation_prompt.md.txt"; Dst="config\prompts\exp01_evaluation_prompt.txt"},
    @{Src="EXP-1\指标统计计算\指标三：模型打分\prompt\prompt.txt"; Dst="config\prompts\exp01_scoring_prompt.txt"},
    
    # EXP-02
    @{Src="EXP-2\抽取\prompt\prompt.txt"; Dst="config\prompts\exp02_extraction_prompt.txt"},
    @{Src="EXP-2\抽取\评估\prompt\prompt.txt"; Dst="config\prompts\exp02_evaluation_prompt.txt"},
    @{Src="EXP-2\依存句法分析\实体对抽取\prompt\prompt.txt"; Dst="config\prompts\exp02_dependency_prompt.txt"},
    @{Src="EXP-2\指标统计计算\指标三：模型打分\prompt\prompt.txt"; Dst="config\prompts\exp02_scoring_prompt.txt"},
    
    # EXP-03
    @{Src="EXP-3\抽取\评估\prompt\prompt.txt"; Dst="config\prompts\exp03_evaluation_prompt.txt"},
    @{Src="EXP-3\主题聚类\prompt\prompt.txt"; Dst="config\prompts\exp03_clustering_prompt.txt"},
    
    # EXP-04
    @{Src="EXP-4\抽取\评估\prompt\prompt.txt"; Dst="config\prompts\exp04_evaluation_prompt.txt"},
    @{Src="EXP-4\主题聚类\prompt\prompt.txt"; Dst="config\prompts\exp04_clustering_prompt.txt"},
    @{Src="EXP-4\指标统计计算\指标三：模型打分\prompt\prompt_eva.txt"; Dst="config\prompts\exp04_scoring_prompt.txt"}
)

$copiedPrompts = 0
foreach ($mapping in $promptMappings) {
    if (Test-Path $mapping.Src) {
        try {
            Copy-Item $mapping.Src $mapping.Dst -Force
            $copiedPrompts++
        } catch {
            Write-Host "  ✗ 失败: $($mapping.Src) -> $($mapping.Dst)" -ForegroundColor Red
            $ErrorCount++
        }
    }
}

Write-Host "  ✓ 成功复制 $copiedPrompts 个提示词文件" -ForegroundColor Green
$SuccessCount++

# ============================================
# 第3步: 创建实验目录结构并存档代码
# ============================================
Write-Host "`n[3/4] 创建实验目录结构..." -ForegroundColor Cyan

$experiments = @(
    @{Name="exp01_baseline"; Source="EXP-1"},
    @{Name="exp02_improved"; Source="EXP-2"},
    @{Name="exp03_clustering"; Source="EXP-3"},
    @{Name="exp04_final"; Source="EXP-4"}
)

foreach ($exp in $experiments) {
    $expPath = "experiments\$($exp.Name)"
    $legacyPath = "$expPath\legacy_code"
    $resultsPath = "data\results\$($exp.Name)"
    
    # 创建目录
    New-Item -ItemType Directory -Force -Path $legacyPath | Out-Null
    New-Item -ItemType Directory -Force -Path $resultsPath | Out-Null
    Write-Host "  ✓ 创建目录: $expPath" -ForegroundColor Green
    
    # 复制原始代码
    if (Test-Path "$($exp.Source)\抽取\code") {
        try {
            Copy-Item "$($exp.Source)\抽取\code\*" $legacyPath -Recurse -Force
            Write-Host "    → 存档代码: $($exp.Source)\抽取\code" -ForegroundColor Gray
        } catch {
            Write-Host "    ✗ 代码存档失败: $_" -ForegroundColor Red
            $ErrorCount++
        }
    }
    
    # 复制指标统计代码
    if (Test-Path "$($exp.Source)\指标统计计算") {
        $metricsPath = "$legacyPath\metrics"
        New-Item -ItemType Directory -Force -Path $metricsPath | Out-Null
        try {
            Copy-Item "$($exp.Source)\指标统计计算\*" $metricsPath -Recurse -Force
            Write-Host "    → 存档指标代码: $($exp.Source)\指标统计计算" -ForegroundColor Gray
        } catch {
            Write-Host "    ✗ 指标代码存档失败: $_" -ForegroundColor Red
        }
    }
}

Write-Host "  ✓ 实验目录结构创建完成" -ForegroundColor Green
$SuccessCount++

# ============================================
# 第4步: 创建实验配置文件
# ============================================
Write-Host "`n[4/4] 创建实验配置文件..." -ForegroundColor Cyan

# 为每个实验创建基本的config.yaml
$configTemplate = @"
# {EXP_NAME} 配置文件
# 自动生成于 {DATE}

experiment:
  name: "{EXP_NAME}"
  description: "{EXP_DESC}"
  
  # 使用的模型
  model: "gemini-2.5-pro"
  
  # 提示词文件
  prompts:
    extraction: "config/prompts/{EXP_PREFIX}_extraction_prompt.txt"
    
paths:
  # 输入输出路径
  input_dir: "data/raw/papers"
  output_dir: "data/results/{EXP_NAME}"
  legacy_code: "experiments/{EXP_NAME}/legacy_code"
  
extraction:
  batch_size: 10
  max_files: 0  # 0 = 无限制
  overwrite: false
  sleep_seconds: 1.0
  max_retries: 3

logging:
  level: "INFO"
  file: "logs/{EXP_NAME}.log"
"@

$expConfigs = @(
    @{Name="exp01_baseline"; Prefix="exp01"; Desc="Baseline experiment"},
    @{Name="exp02_improved"; Prefix="exp02"; Desc="Improved extraction with metadata"},
    @{Name="exp03_clustering"; Prefix="exp03"; Desc="Clustering experiment"},
    @{Name="exp04_final"; Prefix="exp04"; Desc="Final version with all improvements"}
)

foreach ($expCfg in $expConfigs) {
    $configPath = "experiments\$($expCfg.Name)\config.yaml"
    $date = Get-Date -Format "yyyy-MM-dd"
    
    $content = $configTemplate -replace '{EXP_NAME}', $expCfg.Name
    $content = $content -replace '{EXP_PREFIX}', $expCfg.Prefix
    $content = $content -replace '{EXP_DESC}', $expCfg.Desc
    $content = $content -replace '{DATE}', $date
    
    $content | Out-File -FilePath $configPath -Encoding UTF8 -Force
    Write-Host "  ✓ 创建: $configPath" -ForegroundColor Green
}

$SuccessCount++

# ============================================
# 总结
# ============================================
Write-Host "`n================================================" -ForegroundColor Green
Write-Host "  迁移完成！" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "统计信息:" -ForegroundColor Cyan
Write-Host "  ✓ 成功步骤: $SuccessCount/4" -ForegroundColor Green
if ($ErrorCount -gt 0) {
    Write-Host "  ✗ 错误数量: $ErrorCount" -ForegroundColor Red
}
Write-Host ""
Write-Host "后续步骤:" -ForegroundColor Cyan
Write-Host "  1. 查看项目结构: python scripts\show_tree.py --depth 3" -ForegroundColor Yellow
Write-Host "  2. 查看迁移计划: cat docs\FILE_MIGRATION_PLAN.md" -ForegroundColor Yellow
Write-Host "  3. 检查配置文件: ls experiments\*\config.yaml" -ForegroundColor Yellow
Write-Host ""
Write-Host "注意: 原始EXP-*目录保持不变，可作为备份。" -ForegroundColor Gray
Write-Host ""
