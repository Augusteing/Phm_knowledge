# -*- coding: utf-8 -*-
# 文件：code/提取脚本.py
import os
import json
import time
from datetime import datetime, timezone

# 使用 OpenAI 官方 SDK 直连 DeepSeek
from openai import OpenAI

# ------------------------------
# 路径配置
# ------------------------------
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CODE_DIR)

COMPLETE_PROMPT_DIR = os.path.join(BASE_DIR, "完整prompt")  # 完整prompt目录
PAPERS_DIR = os.path.join(BASE_DIR, "论文文献")
DATA_RESULT_DIR = os.path.join(BASE_DIR, "数据结果")
EXTRACT_RESULT_DIR = os.path.join(DATA_RESULT_DIR, "提取结果_by_deepseek")  # JSON结果存放目录
LOG_DIR = os.path.join(DATA_RESULT_DIR, "log_by_deepseek")              # 日志文件存放目录
MAIN_LOG_FILE = os.path.join(LOG_DIR, "extraction_log.ndjson")  # 总日志文件
TIMING_FILE = os.path.join(LOG_DIR, "timings.ndjson")           # 耗时统计

os.makedirs(DATA_RESULT_DIR, exist_ok=True)
os.makedirs(EXTRACT_RESULT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

MODEL_NAME = "deepseek-chat"  # 可按需改为 deepseek-reasoner
PROVIDER_NAME = "deepseek"

# 输出与重试相关可配参数（可用环境变量覆盖）
# - DEEPSEEK_MAX_TOKENS_BASE: 首次尝试的 max_tokens（默认 2048）
# - DEEPSEEK_MAX_TOKENS_CAP: 逐步放大的上限（默认 8192）
# - DEEPSEEK_TEMPERATURE: 采样温度（默认 0）
MAX_TOKENS_BASE = int(os.getenv("DEEPSEEK_MAX_TOKENS_BASE", "2048"))
MAX_TOKENS_CAP = int(os.getenv("DEEPSEEK_MAX_TOKENS_CAP", "8192"))
DEFAULT_TEMPERATURE = float(os.getenv("DEEPSEEK_TEMPERATURE", "0"))


def build_json_hint() -> str:
    """在不修改外部模板文件的前提下，为模型追加清晰的 JSON 输出指令。

    DeepSeek 官方建议：
    - 设置 response_format 为 {"type": "json_object"}
    - 在提示词中包含 "json" 字样，并给出期望的 JSON 格式示例
    - 合理提高 max_tokens 以避免输出被截断
    - 个别情况下 API 可能返回空 content，可调整提示词并重试
    """
    user_override = os.getenv("DEEPSEEK_JSON_HINT")
    if user_override:
        return user_override

    return (
        "\n\n【JSON Output 要求】\n"
        "- 只输出严格合法的 json 对象（object），不要任何解释、前后缀或 Markdown 代码围栏。\n"
        "- 字段值若无则给出合理的空值（例如空字符串、空数组或 null），保持可解析。\n"
        "- 编码为 UTF-8。\n"
    )

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
        try:
            return json.loads(cleaned)
        except Exception:
            extracted = extract_first_json(cleaned)
            if extracted is not None:
                return json.loads(extracted)
            raise

def extract_first_json(text: str):
    """从文本中提取第一个平衡的 JSON 对象或数组；失败返回 None。"""
    if not isinstance(text, str) or not text:
        return None
    s = strip_code_fences(text)
    start_obj = s.find("{")
    start_arr = s.find("[")
    candidates = [i for i in (start_obj, start_arr) if i != -1]
    if not candidates:
        return None
    start = min(candidates)
    stack = []
    in_str = False
    str_ch = ''
    escape = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == str_ch:
                in_str = False
        else:
            if ch in ('"', "'"):
                in_str = True
                str_ch = ch
            elif ch == '{':
                stack.append('}')
            elif ch == '[':
                stack.append(']')
            elif ch in ('}', ']'):
                if not stack or stack[-1] != ch:
                    return None
                stack.pop()
                if not stack:
                    end = i + 1
                    return s[start:end]
    return None

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

# ------------------------------
# 初始化 DeepSeek 客户端（通过 OpenAI SDK 直连）
# ------------------------------
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在环境变量中设置 DEEPSEEK_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

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

for paper_file in papers:
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
    prompt_filled = prompt_content + build_json_hint()

    # 记录 prompt
    save_prompt(paper_file, prompt_filled)

    print(f"提交论文：{paper_file} ...")
    start_ts = time.time()
    attempts = 0

    # 轻量重试
    max_retries = 3
    for attempt in range(max_retries):
        attempts += 1
        try:
            # 针对每次尝试动态提升 max_tokens，缓解长输出被截断
            curr_max_tokens = min(MAX_TOKENS_BASE * (2 ** attempt), MAX_TOKENS_CAP)
            # 优先尝试 response_format 强制 JSON，不支持则降级
            try:
                resp = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "你是信息抽取助手。必须只输出严格且可解析的 JSON 对象，不要任何解释或 Markdown 代码围栏。"},
                        {"role": "user", "content": prompt_filled}
                    ],
                    temperature=DEFAULT_TEMPERATURE,
                    max_tokens=curr_max_tokens,
                    response_format={"type": "json_object"}
                )
            except Exception as e_first:
                msg_first = str(e_first)
                if "response_format" in msg_first.lower() or "unsupported" in msg_first.lower() or "invalid_request" in msg_first.lower():
                    resp = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "你是信息抽取助手。必须只输出严格且可解析的 JSON 对象，不要任何解释或 Markdown 代码围栏。"},
                            {"role": "user", "content": prompt_filled}
                        ],
                        temperature=DEFAULT_TEMPERATURE,
                        max_tokens=curr_max_tokens
                    )
                else:
                    raise
            # 记录 finish_reason 便于判断是否被长度截断
            finish_reason = None
            try:
                finish_reason = getattr(resp.choices[0], "finish_reason", None)
            except Exception:
                finish_reason = None

            content = resp.choices[0].message.content if resp and resp.choices and resp.choices[0].message else ""

            # 处理空 content（DeepSeek 官方提示：偶发空返回，可通过调整 prompt 或重试缓解）
            if not content or not str(content).strip():
                raise ValueError("API 返回空 content —— 将在下一次尝试中重试（可能原因：服务端空响应或提示词触发）。")
            try:
                data = parse_strict_json(content)
            except Exception as parse_err:
                raw_file = output_file.replace(".json", ".raw.txt")
                with open(raw_file, "w", encoding="utf-8") as rf:
                    rf.write(content)
                # 若 finish_reason 显示为被长度截断，抛出的错误信息中加入提示，下一次将自动提高 max_tokens
                hint = "；疑似输出被长度截断（finish_reason=length），下一次将提高 max_tokens 重试" if str(finish_reason).lower() == "length" else ""
                raise ValueError(f"JSON 解析失败: {parse_err}{hint}. 原始输出已保存到 {raw_file}")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 日志：成功与用量
            append_run_log({
                "time": now_iso(),
                "paper": paper_file,
                "status": "success",
                "output": output_file,
                "model": MODEL_NAME,
                "usage": _usage_to_dict(getattr(resp, "usage", None)),
                "finish_reason": str(finish_reason) if finish_reason is not None else None,
                "max_tokens_request": curr_max_tokens,
                "content_chars": len(content) if isinstance(content, str) else None
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
                "usage": _usage_to_dict(getattr(resp, "usage", None)),
                "finish_reason": str(finish_reason) if finish_reason is not None else None,
                "max_tokens_request": curr_max_tokens,
                "content_chars": len(content) if isinstance(content, str) else None
            })

            print(f"结果已保存到 {output_file}")
            success += 1
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
            else:
                # 指数退避
                time.sleep(2 ** attempt)

    if aborted_for_balance:
        break

    # 轻限速（可按需调整或移除）
    time.sleep(1)

print(f"批量提交完成。成功: {success}，失败: {failed}，{'因余额不足提前终止' if aborted_for_balance else '全部处理完成'}。")