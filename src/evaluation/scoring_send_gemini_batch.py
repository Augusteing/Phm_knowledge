# -*- coding: utf-8 -*-
"""
批量打分脚本（新版逻辑）：

目的：
    使用 统一的打分 prompt 对三个抽取模型 (deepseek / gemini / kimi) 的抽取结果进行 LLM 打分，
    将打分结果(JSON) 保存到： 指标统计计算/指标三：模型打分/打分结果/<model>/

数据来源：
    项目根目录下： 抽取/数据结果/提取结果_by_<model>/in_scope/*.json
    （仅处理 in_scope 目录中的 JSON）

使用的 prompt（固定，不再按文件同名匹配）：
    指标统计计算/指标三：模型打分/prompt/prompt.txt

调用方式：
    通过 hiapi.online 的 OpenAI 兼容接口（同 exact_gemini 方式）调用一个远程模型（缺省 gemini-2.5-pro），
    该“远程模型”用于执行打分（不是被打分的抽取模型）。

输出：
    打分结果/<model>/<原文件名>.response.json  （解析失败则包装 raw_text）
    日志：打分结果/_log/send_log.ndjson & send_timings.ndjson （所有模型公用）

命令行参数：
    --remote-model   指定调用的评分 LLM 模型名称（默认 gemini-2.5-pro）
    --models         逗号分隔要处理的抽取模型列表（默认 deepseek,gemini,kimi）
    --max            每个模型最多处理文件数（默认 50）
    --overwrite      已存在结果是否覆盖
    --force-json-output  尝试使用 response_format 强制 JSON（不支持自动降级）

示例（PowerShell）：
    $env:HIAPI_API_KEY = "sk-xxxxx" ; python ./code/抽取脚本/send_gemini_batch.py --models deepseek,gemini,kimi --max 999 --remote-model gemini-2.5-pro
"""

import os
import json
import time
import argparse
from datetime import datetime, timezone
from typing import List

from openai import OpenAI


# ------------------------------
# ------------------------------
# 路径配置（新）
# ------------------------------
CODE_DIR = os.path.dirname(os.path.abspath(__file__))               # .../指标统计计算/指标三：模型打分/code/抽取脚本
BASE_DIR = os.path.dirname(os.path.dirname(CODE_DIR))               # 提升一层到 code，再提升到 指标三：模型打分 目录

# 为健壮性：如果目录名判断失败，可回退再上一层
if not os.path.isdir(os.path.join(BASE_DIR, "prompt")):
    # 说明上面的推断可能少走了一层
    BASE_DIR = os.path.dirname(BASE_DIR)

PROMPT_FILE = os.path.join(BASE_DIR, "prompt", "prompt.txt")

# 项目根目录（包含 抽取/数据结果/...） -> 再往上两级
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

EXTRACTION_BASE = os.path.join(PROJECT_ROOT, "抽取", "数据结果")
SCORING_OUTPUT_BASE = os.path.join(BASE_DIR, "打分结果")
LOG_DIR = os.path.join(SCORING_OUTPUT_BASE, "_log")
MAIN_LOG_FILE = os.path.join(LOG_DIR, "send_log.ndjson")
TIMING_FILE = os.path.join(LOG_DIR, "send_timings.ndjson")

os.makedirs(SCORING_OUTPUT_BASE, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


# ------------------------------
# 默认远程评分模型（可通过命令行覆盖）
# ------------------------------
DEFAULT_REMOTE_MODEL = "gemini-2.5-pro"
PROVIDER_NAME = "gemini"   # 评分提供方标识（用于日志）


# ------------------------------
# 工具函数
# ------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _usage_to_dict(usage_obj):
    if usage_obj is None:
        return None
    try:
        if hasattr(usage_obj, "model_dump"):
            return usage_obj.model_dump()
        if hasattr(usage_obj, "to_dict"):
            return usage_obj.to_dict()
        if isinstance(usage_obj, dict):
            return usage_obj
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


def _mask_key(k: str) -> str:
    if not k or len(k) < 8:
        return "***"
    return f"{k[:6]}...{k[-4:]}"


def strip_code_fences(s: str) -> str:
    """去除```json ... ```样式的围栏，并移除语言行"""
    if not isinstance(s, str):
        return s
    s = s.strip()
    if s.startswith("```") and s.endswith("```"):
        s = s[3:-3].strip()
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


def ensure_prompt_exists() -> str:
    """确认固定 prompt 存在，返回其路径。"""
    if not os.path.isfile(PROMPT_FILE):
        raise FileNotFoundError(f"未找到打分 prompt 文件：{PROMPT_FILE}")
    return PROMPT_FILE


def build_messages(prompt_text: str, json_text: str, model_name: str) -> list:
    """构造对话消息：统一 prompt + 待打分的抽取 JSON。
    model_name: 被打分的抽取模型名称（用于上下文提示，可协助评分模型理解来源）。
    """
    content = (
        f"以下是对 抽取模型 `{model_name}` 的结果进行评价的任务。请根据指令严格输出打分 JSON。"\
        f"\n\n【评分指令】\n{prompt_text}\n\n"\
        f"【抽取结果 JSON】\n{json_text.strip()}\n"
    )
    return [
        {"role": "system", "content": "你是一个专业的评估助手，请依据评分指令生成结构化 JSON 打分结果。"},
        {"role": "user", "content": content},
    ]


def parse_models_arg(raw: str) -> List[str]:
    items = [m.strip() for m in raw.split(',') if m.strip()]
    valid_sequence = []
    seen = set()
    for m in items:
        if m not in seen:
            seen.add(m)
            valid_sequence.append(m)
    return valid_sequence


def main():
    parser = argparse.ArgumentParser(description="批量对三个抽取模型的 in_scope 结果进行 LLM 打分")
    parser.add_argument("--models", default="deepseek,gemini,kimi", help="要处理的抽取模型列表，逗号分隔（默认 deepseek,gemini,kimi）")
    parser.add_argument("--max", type=int, default=50, help="每个模型最多处理的文件数")
    parser.add_argument("--remote-model", default=DEFAULT_REMOTE_MODEL, help="用于评分的远程 LLM 模型名称")
    parser.add_argument("--force-json-output", action="store_true", help="尝试使用 response_format 强制 JSON 输出（如不支持将自动降级）")
    parser.add_argument("--overwrite", action="store_true", help="存在结果时是否覆盖")
    args = parser.parse_args()

    target_models = parse_models_arg(args.models)
    if not target_models:
        raise ValueError("--models 解析为空，请提供至少一个模型名称")

    # 固定 prompt 校验
    prompt_path = ensure_prompt_exists()
    with open(prompt_path, "r", encoding="utf-8") as pf:
        prompt_text = pf.read()

    # 读取并校验 API Key
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
        raise ValueError("未检测到 API Key。请设置 HIAPI_API_KEY（或 GEMINI_API_KEY/OPENAI_API_KEY/API_KEY）。")

    # base_url 处理：默认 https://hiapi.online/v1，可被 HIAPI_BASE_URL 覆盖
    _base_env = os.getenv("HIAPI_BASE_URL")
    if _base_env:
        _base_clean = _base_env.rstrip("/")
        base_url = _base_clean if _base_clean.endswith("/v1") else _base_clean + "/v1"
    else:
        base_url = "https://hiapi.online/v1"

    if "hiapi.online" in (base_url or "") and not api_key.lower().startswith("sk-"):
        raise ValueError(
            f"当前 base_url={base_url} 指向 hiapi.online，但从 {api_key_source} 读取到的 Key 看起来不是 sk- 开头：{_mask_key(api_key)}。\n"
            "请到 hiapi 后台复制以 sk- 开头的密钥，并设置到 HIAPI_API_KEY。"
        )

    client = OpenAI(api_key=api_key, base_url=base_url)

    # 预检
    try:
        models_res = client.models.list()
        models_cnt = len(getattr(models_res, "data", []) or [])
        print(
            f"预检通过：已连接 {base_url}（模型数≈{models_cnt}）。Key 来源={api_key_source}，Key 掩码={_mask_key(api_key)}"
        )
    except Exception as _e:
        _msg = str(_e)
        if ("401" in _msg) or ("unauthorized" in _msg.lower()) or ("invalid" in _msg.lower()):
            raise RuntimeError(
                "预检失败：鉴权未通过(401)。请确认 base_url、环境变量与 Key 有效后重试。"
            )
        else:
            print("预检警告：/models 不可用或返回非 401 错误，将继续执行。详情：" + _msg)

    grand_success, grand_failed = 0, 0
    aborted_for_balance = False

    for model_name in target_models:
        extraction_dir = os.path.join(EXTRACTION_BASE, f"提取结果_by_{model_name}", "in_scope")
        if not os.path.isdir(extraction_dir):
            print(f"[WARN] 模型 {model_name} 跳过：未找到目录 {extraction_dir}")
            continue

        output_dir = os.path.join(SCORING_OUTPUT_BASE, model_name)
        os.makedirs(output_dir, exist_ok=True)
        print(f"开始处理模型 {model_name}：输入 {extraction_dir} -> 输出 {output_dir}")

        all_files = [
            f for f in sorted(os.listdir(extraction_dir))
            if f.lower().endswith('.json') and os.path.isfile(os.path.join(extraction_dir, f))
        ]
        if not all_files:
            print(f"  无 JSON 文件，跳过 {model_name}")
            continue
        target_files = all_files[: max(args.max, 0)]
        print(f"  待打分文件：{len(target_files)}/{len(all_files)} (受 --max 限制)")

        success, failed = 0, 0

        for idx, json_name in enumerate(target_files, start=1):
            json_path = os.path.join(extraction_dir, json_name)
            stem = os.path.splitext(json_name)[0]
            output_file = os.path.join(output_dir, stem + ".response.json")

            if os.path.exists(output_file) and not args.overwrite:
                print(f"[{model_name} {idx}/{len(target_files)}] 已存在结果，跳过：{json_name}")
                append_run_log({
                    "time": now_iso(),
                    "file": json_name,
                    "model_scored": model_name,
                    "status": "skipped",
                    "reason": "exists",
                    "output": output_file,
                })
                append_timing({
                    "time": now_iso(),
                    "file": json_name,
                    "provider": PROVIDER_NAME,
                    "model_remote": args.remote_model,
                    "model_scored": model_name,
                    "status": "skipped",
                    "duration_seconds": 0,
                    "attempts": 0,
                    "output": output_file,
                })
                continue

            with open(json_path, 'r', encoding='utf-8') as jf:
                json_text = jf.read()

            messages = build_messages(prompt_text, json_text, model_name)
            print(f"[{model_name} {idx}/{len(target_files)}] 打分：{json_name}")
            start_ts = time.time()
            attempts = 0
            max_retries = 3

            for attempt in range(max_retries):
                attempts += 1
                try:
                    use_response_format = bool(args.force_json_output)
                    try:
                        if use_response_format:
                            resp = client.chat.completions.create(
                                model=args.remote_model,
                                messages=messages,
                                temperature=0,
                                response_format={"type": "json_object"},
                            )
                        else:
                            resp = client.chat.completions.create(
                                model=args.remote_model,
                                messages=messages,
                                temperature=0,
                            )
                    except Exception as e_first:
                        msg_first = str(e_first)
                        if use_response_format and ("response_format" in msg_first.lower() or "unsupported" in msg_first.lower()):
                            # 自动降级
                            resp = client.chat.completions.create(
                                model=args.remote_model,
                                messages=messages,
                                temperature=0,
                            )
                        else:
                            raise

                    content = resp.choices[0].message.content
                    try:
                        data = parse_strict_json(content)
                    except Exception:
                        data = {"raw_text": content}
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    append_run_log({
                        "time": now_iso(),
                        "file": json_name,
                        "model_scored": model_name,
                        "status": "success",
                        "output": output_file,
                        "remote_model": args.remote_model,
                        "usage": _usage_to_dict(getattr(resp, 'usage', None)),
                    })
                    append_timing({
                        "time": now_iso(),
                        "file": json_name,
                        "provider": PROVIDER_NAME,
                        "model_remote": args.remote_model,
                        "model_scored": model_name,
                        "status": "success",
                        "duration_seconds": round(time.time() - start_ts, 3),
                        "attempts": attempts,
                        "output": output_file,
                        "usage": _usage_to_dict(getattr(resp, 'usage', None)),
                    })
                    print(f"  完成 -> {output_file}")
                    success += 1
                    break
                except Exception as e:
                    msg = str(e)
                    if ("402" in msg) or ("Insufficient Balance" in msg) or ("insufficient balance" in msg.lower()):
                        print(f"  余额不足，中止后续：{msg}")
                        append_run_log({
                            "time": now_iso(),
                            "file": json_name,
                            "model_scored": model_name,
                            "status": "aborted_balance",
                            "error": msg,
                        })
                        append_timing({
                            "time": now_iso(),
                            "file": json_name,
                            "provider": PROVIDER_NAME,
                            "model_remote": args.remote_model,
                            "model_scored": model_name,
                            "status": "aborted_balance",
                            "duration_seconds": round(time.time() - start_ts, 3),
                            "attempts": attempts,
                            "error": msg,
                        })
                        aborted_for_balance = True
                        break

                    is_last = (attempt == max_retries - 1)
                    print(f"  第 {attempt+1}/{max_retries} 次失败：{msg}{'（放弃）' if is_last else '，重试…'}")
                    if is_last:
                        fail_flag = os.path.join(output_dir, stem + ".failed.txt")
                        with open(fail_flag, 'w', encoding='utf-8') as ff:
                            ff.write(f"失败时间: {now_iso()}\n异常: {msg}\n")
                        append_run_log({
                            "time": now_iso(),
                            "file": json_name,
                            "model_scored": model_name,
                            "status": "failed",
                            "error": msg,
                            "fail_flag": fail_flag,
                        })
                        append_timing({
                            "time": now_iso(),
                            "file": json_name,
                            "provider": PROVIDER_NAME,
                            "model_remote": args.remote_model,
                            "model_scored": model_name,
                            "status": "failed",
                            "duration_seconds": round(time.time() - start_ts, 3),
                            "attempts": attempts,
                            "error": msg,
                            "fail_flag": fail_flag,
                        })
                        failed += 1
                    else:
                        time.sleep(2 ** attempt)

            if aborted_for_balance:
                break
            time.sleep(1)  # 轻限速

        grand_success += success
        grand_failed += failed
        print(f"模型 {model_name} 完成：成功 {success} 失败 {failed}")
        if aborted_for_balance:
            break

    print(
        f"全部处理结束：总成功 {grand_success}，总失败 {grand_failed}，" +
        ("因余额不足提前终止" if aborted_for_balance else "已处理指定模型")
    )


if __name__ == "__main__":
    main()
