# -*- coding: utf-8 -*-
# 文件：code/提取脚本.py
import os
import json
import time
from datetime import datetime, timezone

# 通过 OpenAI SDK 直连 hiapi.online（Gemini OpenAI 兼容端点）
from openai import OpenAI

# ------------------------------
# 路径配置
# ------------------------------
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CODE_DIR)

COMPLETE_PROMPT_DIR = os.path.join(BASE_DIR, "完整prompt")  # 完整prompt目录
PAPERS_DIR = os.path.join(BASE_DIR, "论文文献")
DATA_RESULT_DIR = os.path.join(BASE_DIR, "数据结果")
EXTRACT_RESULT_DIR = os.path.join(DATA_RESULT_DIR, "提取结果_by_gemini")  # JSON结果存放目录
LOG_DIR = os.path.join(DATA_RESULT_DIR, "log")              # 日志文件存放目录
MAIN_LOG_FILE = os.path.join(LOG_DIR, "extraction_log.ndjson")  # 总日志文件
TIMING_FILE = os.path.join(LOG_DIR, "timings.ndjson")           # 耗时统计

os.makedirs(DATA_RESULT_DIR, exist_ok=True)
os.makedirs(EXTRACT_RESULT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 默认使用 Gemini 模型（hiapi.online 支持的模型名，见站点教程）
# 可按需改为："gemini-2.5-pro-preview-06-05"、"gemini-2.5-pro"、"gpt-5" 等
MODEL_NAME = "gemini-2.5-pro"
PROVIDER_NAME = "gemini"

# ------------------------------
# 速度/鲁棒性参数（可通过环境变量覆盖）
# ------------------------------
# 每篇结束后等待秒数（默认 1.0；置 0 可更快，但更易触发限流）
SLEEP_SECS = float(os.getenv("EXTRACT_SLEEP_SECS", "1"))
# 最大重试次数（默认 3；可通过 EXTRACT_MAX_RETRIES 调整）
try:
    MAX_RETRIES = int(os.getenv("EXTRACT_MAX_RETRIES", "3"))
except Exception:
    MAX_RETRIES = 3
# 跳过 /models 预检（默认否；设 EXTRACT_SKIP_PREFLIGHT=1 可跳过，减少启动耗时）
SKIP_PREFLIGHT = os.getenv("EXTRACT_SKIP_PREFLIGHT", "0") in {"1", "true", "TRUE"}

# ------------------------------
# 进度条（tqdm 优先，缺失则用简易控制台进度）
# ------------------------------
try:
    from tqdm.auto import tqdm  # type: ignore
    HAVE_TQDM = True
except Exception:
    tqdm = None  # type: ignore
    HAVE_TQDM = False

def _iter_with_progress(items, desc: str):
    total = len(items)
    if HAVE_TQDM:
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

# ------------------------------
# 工具函数
# ------------------------------
def strip_code_fences(s: str) -> str:
    """去除```json ... ```样式的围栏，并移除语言行"""
    if not isinstance(s, str):
        return s
    s = s.strip()
    if s.startswith("```") and s.endswith("```"):
        s = s[3:-3].strip()
        # 可能以语言标记开头，比如 "json"
        if "\n" in s:
            first_line, rest = s.split("\n", 1)
            if first_line.strip().lower() in {"json", "js", "javascript"}:
                s = rest
    return s

def parse_strict_json(content: str):
    """将模型输出解析为严格 JSON，自动剥离代码围栏"""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        cleaned = strip_code_fences(content)
        return json.loads(cleaned)

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _usage_to_dict(usage_obj):
    """尽量把 usage 转为 dict。"""
    if usage_obj is None:
        return None
    try:
        if hasattr(usage_obj, "model_dump"):
            return usage_obj.model_dump()
        if hasattr(usage_obj, "to_dict"):
            return usage_obj.to_dict()
        if isinstance(usage_obj, dict):
            return usage_obj
        # 尝试提取常见字段
        keys = ("prompt_tokens", "completion_tokens", "total_tokens")
        d = {k: getattr(usage_obj, k) for k in keys if hasattr(usage_obj, k)}
        return d or str(usage_obj)
    except Exception:
        return str(usage_obj)

def append_run_log(item: dict):
    with open(MAIN_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def append_timing(item: dict):
    with open(TIMING_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def save_prompt(paper_file: str, prompt_text: str) -> str:
    """保存单篇论文的 prompt 到日志，并写入总日志，返回 prompt 内容"""
    log_item = {
        "time": now_iso(),
        "paper": paper_file,
        "prompt_length": len(prompt_text),
        "action": "prompt_generated"
    }
    with open(MAIN_LOG_FILE, "a", encoding="utf-8") as logf:
        logf.write(json.dumps(log_item, ensure_ascii=False) + "\n")

    return prompt_text  # 返回 prompt 内容而不是文件路径

def get_prompt_for_paper(paper_file: str) -> str:
    """根据论文文件名获取对应的完整prompt文件内容
    
    Args:
        paper_file: 论文文件名，如 '飞机操纵面故障的多参数预测模型_MinerU__20250913053608.md'
    
    Returns:
        对应的完整prompt文件内容
    """
    # 从论文文件名生成对应的prompt文件名
    # 论文文件：飞机操纵面故障的多参数预测模型_MinerU__20250913053608.md
    # 对应prompt：prompt_飞机操纵面故障的多参数预测模型_MinerU__20250913053608.txt
    if paper_file.endswith('.md'):
        prompt_filename = f"prompt_{paper_file[:-3]}.txt"
    else:
        prompt_filename = f"prompt_{paper_file}.txt"
    
    prompt_path = os.path.join(COMPLETE_PROMPT_DIR, prompt_filename)
    
    if not os.path.exists(prompt_path):
        # 如果找不到对应的prompt文件，记录错误并返回空字符串
        print(f"警告：找不到对应的prompt文件：{prompt_path}")
        return ""
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"读取prompt文件失败：{prompt_path}，错误：{e}")
        return ""

# ------------------------------
# 初始化 Gemini 客户端（通过 hiapi.online 的 OpenAI 兼容接口）
# ------------------------------

def _mask_key(k: str) -> str:
    if not k or len(k) < 8:
        return "***"
    return f"{k[:6]}...{k[-4:]}"

# 支持多种环境变量名，按优先级获取，并记录来源
api_key_source = None
for _var in ("HIAPI_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", "API_KEY"):
    _v = os.getenv(_var)
    if _v:
        api_key = _v.strip()
        api_key_source = _var
        break
else:
    api_key = None

if not api_key:
    raise ValueError(
        "未检测到 API Key。请在环境变量中设置 HIAPI_API_KEY（或 GEMINI_API_KEY/OPENAI_API_KEY/API_KEY）。"
    )

# 允许通过 HIAPI_BASE_URL 覆盖（默认 https://hiapi.online/v1）
_base_env = os.getenv("HIAPI_BASE_URL")
if _base_env:
    _base_clean = _base_env.rstrip("/")
    BASE_URL = _base_clean if _base_clean.endswith("/v1") else _base_clean + "/v1"
else:
    BASE_URL = "https://hiapi.online/v1"

# 若当前目标是 hiapi.online，通常使用 sk- 开头的密钥
if "hiapi.online" in (BASE_URL or "") and not api_key.lower().startswith("sk-"):
    raise ValueError(
        f"当前 base_url={BASE_URL} 指向 hiapi.online，但从 {api_key_source} 读取到的 Key 看起来不是 sk- 开头：{_mask_key(api_key)}。\n"
        "请到 hiapi 后台复制以 sk- 开头的密钥，并设置到 HIAPI_API_KEY（重开终端或重新加载会话）。"
    )

client = OpenAI(api_key=api_key, base_url=BASE_URL)

# 启动预检：尝试 /models 以提前发现 401 或 URL 配置问题
if not SKIP_PREFLIGHT:
    try:
        models_res = client.models.list()
        models_cnt = len(getattr(models_res, "data", []) or [])
        print(
            f"预检通过：已连接 {BASE_URL}（模型数≈{models_cnt}）。Key 来源={api_key_source}，Key 掩码={_mask_key(api_key)}"
        )
    except Exception as _e:
        _msg = str(_e)
        if "401" in _msg or "unauthorized" in _msg.lower() or "invalid" in _msg.lower():
            raise RuntimeError(
                "预检失败：鉴权未通过(401)。请确认：\n"
                f"- base_url 是否为 {BASE_URL}\n"
                f"- 当前会话是否已加载 {api_key_source}（Key 掩码：{_mask_key(api_key)}）\n"
                "- Key 是否为 hiapi 后台颁发、且未被撤销/未超额\n"
                "- 如刚设置环境变量，请重开 PowerShell 或在同一会话中重新设置 `$env:HIAPI_API_KEY` 后重试"
            )
        else:
            print("预检警告：/models 接口不可用或返回非 401 错误，将继续执行。详情：" + _msg)

# ------------------------------
# 获取所有论文文件
# ------------------------------
papers = sorted(f for f in os.listdir(PAPERS_DIR) if f.endswith(".md"))
print(f"找到 {len(papers)} 篇论文：{papers}")

# ------------------------------
# 批量提交
# ------------------------------
success, failed = 0, 0
aborted_for_balance = False

# 包装带进度的迭代器
paper_iter = _iter_with_progress(papers, desc="Gemini抽取")

for paper_file in paper_iter:
    # 输出文件路径（支持断点续跑）
    output_file = os.path.join(EXTRACT_RESULT_DIR, paper_file.replace(".md", ".json"))
    if os.path.exists(output_file):
        print(f"已存在结果，跳过：{paper_file}")
        append_run_log({
            "time": now_iso(),
            "paper": paper_file,
            "status": "skipped",
            "reason": "exists",
            "output": output_file
        })
        append_timing({
            "time": now_iso(),
            "paper": paper_file,
            "provider": PROVIDER_NAME,
            "model": MODEL_NAME,
            "status": "skipped",
            "duration_seconds": 0,
            "attempts": 0,
            "output": output_file
        })
        # 进度更新
        if HAVE_TQDM:
            if hasattr(paper_iter, "set_postfix"):
                paper_iter.set_postfix(success=success, failed=failed, skipped=True)
        continue

    paper_path = os.path.join(PAPERS_DIR, paper_file)
    with open(paper_path, "r", encoding="utf-8") as f:
        paper_text = f.read()

    # 获取对应的完整prompt内容
    prompt_content = get_prompt_for_paper(paper_file)
    if not prompt_content:
        print(f"跳过论文（无对应prompt）：{paper_file}")
        append_run_log({
            "time": now_iso(),
            "paper": paper_file,
            "status": "skipped",
            "reason": "no_prompt_found"
        })
        continue

    # 使用完整的prompt内容（已包含论文内容，无需再填充占位符）
    prompt_filled = prompt_content

    # 记录 prompt
    save_prompt(paper_file, prompt_filled)

    print(f"提交论文：{paper_file} ...")
    start_ts = time.time()
    attempts = 0

    # 轻量重试
    max_retries = MAX_RETRIES
    for attempt in range(max_retries):
        attempts += 1
        try:
            # 默认尝试使用 response_format 强制 JSON；若服务端不支持将捕获后降级
            use_response_format = True
            try:
                resp = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "你是信息抽取助手，只输出严格的 JSON，不要添加多余文本。"},
                        {"role": "user", "content": prompt_filled}
                    ],
                    temperature=0,
                    response_format={"type": "json_object"}
                )
            except Exception as e_first:
                msg_first = str(e_first)
                # 兼容部分网关不支持 response_format 的情况
                if "response_format" in msg_first.lower() or "unsupported" in msg_first.lower():
                    use_response_format = False
                    resp = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "你是信息抽取助手，只输出严格的 JSON，不要添加多余文本。"},
                            {"role": "user", "content": prompt_filled}
                        ],
                        temperature=0
                    )
                else:
                    raise
            content = resp.choices[0].message.content
            data = parse_strict_json(content)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 日志：成功与用量
            append_run_log({
                "time": now_iso(),
                "paper": paper_file,
                "status": "success",
                "output": output_file,
                "model": MODEL_NAME,
                "usage": _usage_to_dict(getattr(resp, "usage", None))
            })
            append_timing({
                "time": now_iso(),
                "paper": paper_file,
                "provider": PROVIDER_NAME,
                "model": MODEL_NAME,
                "status": "success",
                "duration_seconds": round(time.time() - start_ts, 3),
                "attempts": attempts,
                "output": output_file,
                "usage": _usage_to_dict(getattr(resp, "usage", None))
            })

            print(f"结果已保存到 {output_file}")
            success += 1
            if HAVE_TQDM and hasattr(paper_iter, "set_postfix"):
                paper_iter.set_postfix(success=success, failed=failed)
            break  # 成功则跳出重试
        except Exception as e:
            msg = str(e)
            # 余额不足：HTTP 402 或错误信息包含关键词，直接中止后续任务
            if ("402" in msg) or ("Insufficient Balance" in msg) or ("insufficient balance" in msg.lower()):
                print(f"余额不足，终止后续任务：{msg}")
                append_run_log({
                    "time": now_iso(),
                    "paper": paper_file,
                    "status": "aborted_balance",
                    "error": msg
                })
                append_timing({
                    "time": now_iso(),
                    "paper": paper_file,
                    "provider": PROVIDER_NAME,
                    "model": MODEL_NAME,
                    "status": "aborted_balance",
                    "duration_seconds": round(time.time() - start_ts, 3),
                    "attempts": attempts,
                    "error": msg
                })
                aborted_for_balance = True
                break
            is_last = (attempt == max_retries - 1)
            print(f"第 {attempt+1}/{max_retries} 次尝试失败：{msg}{'（已放弃）' if is_last else '，重试中…'}")
            if is_last:
                # 失败也保留错误记录，便于复现
                fail_flag = output_file.replace(".json", ".failed.txt")
                with open(fail_flag, "w", encoding="utf-8") as ff:
                    ff.write(f"失败时间: {now_iso()}\n异常: {msg}\n")
                append_run_log({
                    "time": now_iso(),
                    "paper": paper_file,
                    "status": "failed",
                    "error": msg,
                    "fail_flag": fail_flag
                })
                append_timing({
                    "time": now_iso(),
                    "paper": paper_file,
                    "provider": PROVIDER_NAME,
                    "model": MODEL_NAME,
                    "status": "failed",
                    "duration_seconds": round(time.time() - start_ts, 3),
                    "attempts": attempts,
                    "error": msg,
                    "fail_flag": fail_flag
                })
                failed += 1
                if HAVE_TQDM and hasattr(paper_iter, "set_postfix"):
                    paper_iter.set_postfix(success=success, failed=failed)
            else:
                # 指数退避
                time.sleep(2 ** attempt)

    if aborted_for_balance:
        # 若使用 tqdm，主动关闭
        if HAVE_TQDM and hasattr(paper_iter, "close"):
            paper_iter.close()
        break

    # 轻限速（可按需调整或移除）
    if SLEEP_SECS > 0:
        time.sleep(SLEEP_SECS)

print(f"\n批量提交完成。成功: {success}，失败: {failed}，{'因余额不足提前终止' if aborted_for_balance else '全部处理完成'}。")