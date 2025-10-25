# 进度条显示修复总结

## 问题描述

在 Windows PowerShell 中运行提取脚本时，进度条显示异常：
- 出现重复的进度条输出
- 特殊字符（如 `|`）显示不正常
- 进度条被多次打印

## 根本原因

1. **自定义 `bar_format` 不兼容**: 使用 `bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}'` 在某些终端环境下会导致显示问题
2. **固定 `ncols` 限制**: 强制设置 `ncols=80` 可能与实际终端宽度不匹配
3. **tqdm 版本差异**: 使用 `from tqdm import tqdm` 而不是 `from tqdm.auto import tqdm`

## 解决方案

### 1. 统一使用 tqdm.auto

```python
try:
    from tqdm.auto import tqdm  # type: ignore
    HAVE_TQDM = True
except Exception:
    tqdm = None  # type: ignore
    HAVE_TQDM = False
```

**优势**:
- `tqdm.auto` 会自动选择最适合当前环境的进度条实现（notebook 或 console）
- 更好的跨平台兼容性

### 2. 简化进度条配置

```python
def _iter_with_progress(items, desc: str):
    """创建进度条迭代器，兼容 subprocess 输出"""
    total = len(items)
    if HAVE_TQDM:
        # 使用 tqdm.auto 的默认配置，简洁且兼容性好
        return tqdm(items, total=total, desc=desc, unit="篇")

    # 简易进度（每 1%/末尾刷新）
    def _gen():
        step = max(1, total // 100)
        for i, x in enumerate(items, 1):
            if (i % step == 0) or (i == total):
                pct = int(i * 100 / total)
                print(f"\r{desc}: {i}/{total} ({pct}%)", end="", flush=True)
            yield x
        print()
    return _gen()
```

**关键改进**:
- 移除 `bar_format` 参数
- 移除 `ncols` 参数
- 只保留核心参数：`desc`、`unit`、`total`
- 让 tqdm 自动适应终端宽度和样式

### 3. 正确使用 tqdm.write

在有进度条时使用 `tqdm.write()` 输出信息，避免破坏进度条：

```python
if HAVE_TQDM and progress_bar:
    tqdm.write(f"提交论文：{paper_file} ...")
else:
    print(f"提交论文：{paper_file} ...")
```

### 4. 优化 subprocess 输出处理

在 main.py 中使用无缓冲输出：

```python
process = subprocess.Popen(
    [sys.executable, str(script_path)],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=0,  # 无缓冲，立即输出
    env=os.environ.copy()
)

# 实时打印输出，保留 tqdm 进度条格式
for line in process.stdout:
    sys.stdout.write(line)
    sys.stdout.flush()
```

## 修改的文件

1. `exact_gemini.py` - Gemini 提取脚本
2. `exact_deepseek.py` - DeepSeek 提取脚本  
3. `exact_kimi.py` - Kimi 提取脚本
4. `main.py` - 主入口脚本

## 预期效果

修复后的进度条显示应该类似于：

```
Gemini [1/3] 试运行: 30%|███████████████▍                              | 3/10 [00:05<00:12,  1.75s/篇, failed=0, skipped=0, success=3]
```

**特点**:
- 单行显示，实时更新
- 百分比、进度条、计数、速度一目了然
- 右侧显示动态统计信息（success/failed/skipped）
- 在 PowerShell 中正常显示，无重复输出

## 测试方法

### 单独测试进度条

```bash
cd e:\entities\experiments\exp01_baseline\src\extraction
python test_progress.py
```

### 测试实际提取

```bash
# 直接运行
cd e:\entities\experiments\exp01_baseline\src\extraction
python exact_deepseek.py

# 通过 main.py 运行
python main.py --extractors deepseek --dry-run
```

## 兼容性说明

- ✅ Windows PowerShell 5.1
- ✅ Windows Terminal
- ✅ Git Bash
- ✅ Linux/macOS Terminal
- ✅ VS Code 集成终端
- ✅ Jupyter Notebook (通过 tqdm.auto)

## 参考

- 旧版 Gemini 脚本: `e:\知识图谱构建\9.15之前的实验\EXP-1\抽取\code\抽取脚本\exact_gemini.py`
- tqdm 文档: https://tqdm.github.io/
