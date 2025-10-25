# -*- coding: utf-8 -*-
# 文件：code/提取脚本.py
import os
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any

# 通过 OpenAI SDK 直连 hiapi.online（Gemini OpenAI 兼容端点）
from openai import OpenAI

# 导入日志管理器
from log_manager import ExtractionLogger, count_entities_and_relations

# ------------------------------
# 路径配置
# ------------------------------
CODE_DIR = os.path.dirname(os.path.abspath(__file__))        # .../src/extraction
EXTRACTION_DIR = CODE_DIR                                     # .../src/extraction
SRC_DIR = os.path.dirname(EXTRACTION_DIR)                     # .../src
EXP_DIR = os.path.dirname(SRC_DIR)                            # .../exp01_baseline

# 配置文件路径
CONFIG_DIR = os.path.join(EXP_DIR, "config")
PROMPT_DIR = os.path.join(CONFIG_DIR, "prompt")

def _resolve_prompt_file() -> str:
    env_path = os.getenv("EXTRACT_PROMPT_FILE", "").strip()
    if env_path:
        p = env_path if os.path.isabs(env_path) else os.path.join(EXP_DIR, env_path)
        if os.path.isfile(p):
            return p
        raise FileNotFoundError(f"EXTRACT_PROMPT_FILE 指定的文件不存在: {p}")
    candidates = [
        os.path.join(PROMPT_DIR, "prompt实验二.txt"),
        os.path.join(PROMPT_DIR, "prompt_exp2.txt"),
        os.path.join(PROMPT_DIR, "prompt.txt"),
        os.path.join(PROMPT_DIR, "prompt实验一.txt"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    if os.path.isdir(PROMPT_DIR):
        txts = [f for f in os.listdir(PROMPT_DIR) if f.lower().endswith(".txt")]
        if len(txts) == 1:
            return os.path.join(PROMPT_DIR, txts[0])
    # 实验三：允许无通用 prompt（优先使用 per-article 提示词）。返回空字符串表示“无默认模板”。
    return ""

PROMPT_FILE = _resolve_prompt_file()

# 数据路径
DATA_DIR = os.path.join(EXP_DIR, "data")
PAPERS_DIR = os.path.join(DATA_DIR, "raw", "papers")
PRIORITY_DIR = os.path.join(PAPERS_DIR, "priority")           # 优先抽取的论文
GENERAL_DIR = os.path.join(PAPERS_DIR, "general")             # 普通论文

# 输出路径
OUTPUTS_DIR = os.path.join(EXP_DIR, "outputs")
EXTRACTIONS_DIR = os.path.join(OUTPUTS_DIR, "extractions")
GEMINI_DIR = os.path.join(EXTRACTIONS_DIR, "gemini")          # Gemini结果存放目录
IN_SCOPE_DIR = os.path.join(GEMINI_DIR, "priority")           # 优先论文输出
OUT_SCOPE_DIR = os.path.join(GEMINI_DIR, "general")           # 普通论文输出
LOG_DIR = os.path.join(OUTPUTS_DIR, "logs", "gemini")         # 日志文件存放目录

os.makedirs(GEMINI_DIR, exist_ok=True)
os.makedirs(IN_SCOPE_DIR, exist_ok=True)
os.makedirs(OUT_SCOPE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 初始化日志记录器
logger = ExtractionLogger(LOG_DIR, "gemini")

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
    """为列表添加进度条（旧 Gemini 风格）"""
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

# ------------------------------
# 加载 prompt 与 schema（实验三：priority 每篇对应 prompt_*.txt）
# ------------------------------
def _load_prompt_template_for(paper_file: str, is_priority: bool) -> tuple[str, str]:
    """为指定论文选择并加载提示词模板。

    选择顺序：
    - 若为 priority 论文，优先匹配 config/prompt/prompt_<论文文件名去扩展名>.txt
    - 若上述不存在，则回退到环境变量 EXTRACT_PROMPT_FILE 指定的模板（若设置）
    - 否则回退到默认全局 PROMPT_FILE（通过 _resolve_prompt_file 已解析）
    """
    base_name = os.path.splitext(paper_file)[0]
    if is_priority:
        per_article = os.path.join(PROMPT_DIR, f"prompt_{base_name}.txt")
        if os.path.isfile(per_article):
            with open(per_article, "r", encoding="utf-8") as f:
                return f.read(), per_article

    # 环境变量覆盖（若没有专属 prompt）
    env_path = os.getenv("EXTRACT_PROMPT_FILE", "").strip()
    if env_path:
        p = env_path if os.path.isabs(env_path) else os.path.join(EXP_DIR, env_path)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read(), p

    # 全局默认 prompt
    if PROMPT_FILE and os.path.isfile(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read(), PROMPT_FILE
    raise FileNotFoundError("未能找到可用的 prompt 模板。")

SCHEMA_FILE = os.path.join(CONFIG_DIR, "schema", "phm_semantic_patterns.json")
def _load_schema_text() -> str:
    if not os.path.isfile(SCHEMA_FILE):
        return ""
    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as sf:
            schema_obj: Dict[str, Any] = json.load(sf)
        wanted = os.getenv("EXTRACT_SCHEMA_FIELDS", "entity_types,relation_types").strip()
        if wanted:
            fields = [w.strip() for w in wanted.split(',') if w.strip()]
            filtered = {k: schema_obj.get(k) for k in fields if k in schema_obj}
            if filtered:
                return json.dumps(filtered, ensure_ascii=False, indent=2)
        return json.dumps(schema_obj, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  加载 schema 失败，将忽略。原因: {e}")
        return ""

SCHEMA_TEXT = _load_schema_text()

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
# 优先处理：data/raw/papers/priority 下的论文
# 普通论文：data/raw/papers/general 下的论文
# ------------------------------
priority_files = []
if os.path.isdir(PRIORITY_DIR):
    priority_files = sorted(
        f for f in os.listdir(PRIORITY_DIR) if f.endswith(".md") and os.path.isfile(os.path.join(PRIORITY_DIR, f))
    )

general_files = []
if os.path.isdir(GENERAL_DIR):
    general_files = sorted(
        f for f in os.listdir(GENERAL_DIR) if f.endswith(".md") and os.path.isfile(os.path.join(GENERAL_DIR, f))
    )

# 去除已在优先目录中的重名文件
ONLY_PRIORITY = os.getenv("EXTRACT_ONLY_PRIORITY", "").strip().lower() in {"1", "true"}
remaining_files = [f for f in general_files if f not in priority_files]
if ONLY_PRIORITY:
    # 不处理 general 论文
    remaining_files = []
papers = priority_files + remaining_files

print(
    f"找到 {len(papers)} 篇论文（优先目录 {len(priority_files)} 篇 + 普通目录 {len(remaining_files)} 篇）。优先处理：{priority_files}"
)

# in_scope/out_scope 设置
FIRST_BATCH_SIZE = int(os.getenv("FIRST_BATCH_SIZE", "10"))
IN_SCOPE_LIMIT = int(os.getenv("IN_SCOPE_LIMIT", "50"))
AUTO_CONTINUE_REST = os.getenv("AUTO_CONTINUE_REST", "").strip().lower()

# 分批策略
first_batch = priority_files[:FIRST_BATCH_SIZE]
second_batch = priority_files[FIRST_BATCH_SIZE:IN_SCOPE_LIMIT]
third_batch = priority_files[IN_SCOPE_LIMIT:] + remaining_files

print(f"计划：第1批（试运行）{len(first_batch)} 篇；第2批（优先）{len(second_batch)} 篇；第3批（普通）{len(third_batch)} 篇。")

# ------------------------------
# 批量提交
# ------------------------------
success, failed, skipped = 0, 0, 0
aborted_for_balance = False

# 设置总论文数
logger.set_total_papers(len(papers))

def _process_one(paper_file: str, target_dir: str, progress_bar=None):
    global success, failed, skipped, aborted_for_balance  # noqa
    
    # 构造相对路径（priority/xxx.md 或 general/xxx.md）
    if paper_file in priority_files:
        paper_rel_path = f"priority/{paper_file}"
        paper_path = os.path.join(PRIORITY_DIR, paper_file)
    else:
        paper_rel_path = f"general/{paper_file}"
        paper_path = os.path.join(GENERAL_DIR, paper_file)
    
    # 输出文件路径（支持断点续跑）
    output_file = os.path.join(target_dir, paper_file.replace(".md", ".json"))
    
    if os.path.exists(output_file):
        if HAVE_TQDM and progress_bar:
            tqdm.write(f"已存在结果，跳过：{paper_file}")
        else:
            print(f"已存在结果，跳过：{paper_file}")
        # 跳过的也记录（duration=0）
        logger.add_log_entry(
            paper=paper_rel_path,
            success=True,
            duration_seconds=0,
            entity_count=0,
            relation_count=0,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            skipped=True
        )
        skipped += 1
        if HAVE_TQDM and progress_bar:
            progress_bar.set_postfix(success=success, failed=failed, skipped=skipped)
        return

    # 读取论文
    with open(paper_path, "r", encoding="utf-8") as f:
        paper_text = f.read()

    # 为该论文选择并加载模板
    is_priority = (paper_file in priority_files)
    prompt_template, prompt_source = _load_prompt_template_for(paper_file, is_priority)

    # 填充 prompt（占位符替换；注入 schema，如无占位符则追加在末尾；若缺少全文占位符则追加在末尾）
    prompt_filled = (
        prompt_template
        .replace("{schema_placeholder}", SCHEMA_TEXT or "")
        .replace("{schema_json_placeholder}", SCHEMA_TEXT or "")
    )
    if "{full_text_placeholder}" in prompt_template:
        prompt_filled = prompt_filled.replace("{full_text_placeholder}", paper_text)
    else:
        prompt_filled = prompt_filled + "\n\n【全文】\n" + paper_text
    if SCHEMA_TEXT and "{schema_placeholder}" not in prompt_template and "{schema_json_placeholder}" not in prompt_template:
        prompt_filled = prompt_filled + "\n\n【Schema】\n" + SCHEMA_TEXT

    if HAVE_TQDM and progress_bar:
        tqdm.write(f"提交论文：{paper_file} ...")
    else:
        print(f"提交论文：{paper_file} ...")
    start_ts = time.time()
    attempts = 0
    
    # 轻量重试
    max_retries = MAX_RETRIES
    for attempt in range(max_retries):
        attempts += 1
        try:
            # 默认尝试使用 response_format 强制 JSON；若服务端不支持将捕获后降级
            try:
                response = client.chat.completions.create(
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
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "你是信息抽取助手，只输出严格的 JSON，不要添加多余文本。"},
                            {"role": "user", "content": prompt_filled}
                        ],
                        temperature=0
                    )
                else:
                    raise
            
            content = response.choices[0].message.content
            data = parse_strict_json(content)
            
            # 保存结果
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 统计实体和关系数量
            entity_count, relation_count = count_entities_and_relations(data)
            
            # 提取 token 使用量
            usage = getattr(response, "usage", None)
            prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
            completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
            total_tokens = getattr(usage, "total_tokens", 0) if usage else 0
            
            # 记录成功日志
            logger.add_log_entry(
                paper=paper_rel_path,
                success=True,
                duration_seconds=time.time() - start_ts,
                entity_count=entity_count,
                relation_count=relation_count,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                attempts=attempts,
                prompt_source=prompt_source
            )

            if HAVE_TQDM and progress_bar:
                tqdm.write(f"结果已保存到 {output_file}")
            else:
                print(f"结果已保存到 {output_file}")
            success += 1
            if HAVE_TQDM and progress_bar:
                progress_bar.set_postfix(success=success, failed=failed, skipped=skipped)
            break  # 成功则跳出重试
            
        except Exception as e:
            msg = str(e)
            # 余额不足：HTTP 402 或错误信息包含关键词，直接中止后续任务
            if ("402" in msg) or ("Insufficient Balance" in msg) or ("insufficient balance" in msg.lower()):
                if HAVE_TQDM and progress_bar:
                    tqdm.write(f"余额不足，终止后续任务：{msg}")
                else:
                    print(f"余额不足，终止后续任务：{msg}")
                logger.add_log_entry(
                    paper=paper_rel_path,
                    success=False,
                    duration_seconds=time.time() - start_ts,
                    error=f"余额不足: {msg}",
                    attempts=attempts,
                    prompt_source=prompt_source
                )
                aborted_for_balance = True
                break
            
            is_last = (attempt == max_retries - 1)
            if HAVE_TQDM and progress_bar:
                tqdm.write(f"第 {attempt+1}/{max_retries} 次尝试失败：{msg}{'（已放弃）' if is_last else '，重试中…'}")
            else:
                print(f"第 {attempt+1}/{max_retries} 次尝试失败：{msg}{'（已放弃）' if is_last else '，重试中…'}")
            
            if is_last:
                # 失败也保留错误记录，便于复现
                fail_flag = output_file.replace(".json", ".failed.txt")
                with open(fail_flag, "w", encoding="utf-8") as ff:
                    ff.write(f"失败时间: {now_iso()}\n异常: {msg}\n")
                
                logger.add_log_entry(
                    paper=paper_rel_path,
                    success=False,
                    duration_seconds=time.time() - start_ts,
                    error=msg,
                    attempts=attempts,
                    fail_flag=fail_flag,
                    prompt_source=prompt_source
                )
                failed += 1
                if HAVE_TQDM and progress_bar:
                    progress_bar.set_postfix(success=success, failed=failed, skipped=skipped)
            else:
                # 指数退避
                time.sleep(2 ** attempt)

# ------------------------------
# 第1批：试运行（前 10 篇）
# ------------------------------
if first_batch:
    print(f"\n{'='*70}")
    print(f"开始第1批处理（试运行）：{len(first_batch)} 篇")
    print(f"{'='*70}")
    
    progress_bar_1 = _iter_with_progress(first_batch, desc="Gemini [1/3] 试运行")
    for pf in progress_bar_1:
        _process_one(pf, IN_SCOPE_DIR, progress_bar_1 if HAVE_TQDM else None)
        if aborted_for_balance:
            break
        if SLEEP_SECS > 0:
            time.sleep(SLEEP_SECS)
    
    if not aborted_for_balance:
        print(f"\n第1批完成：成功 {success} 篇，失败 {failed} 篇，跳过 {skipped} 篇")
        
        # 询问是否继续
        if second_batch or third_batch:
            proceed = None
            if AUTO_CONTINUE_REST in {"y", "yes"}:
                proceed = True
                print("→ 自动继续（AUTO_CONTINUE_REST=y）")
            elif AUTO_CONTINUE_REST in {"n", "no"}:
                proceed = False
                print("→ 自动停止（AUTO_CONTINUE_REST=n）")
            else:
                try:
                    remaining_count = len(second_batch) + len(third_batch)
                    ans = input(f"\n是否继续处理剩余 {remaining_count} 篇？(y/n): ").strip().lower()
                    proceed = ans in {"y", "yes"}
                except (EOFError, KeyboardInterrupt):
                    proceed = False
            
            if not proceed:
                print("→ 用户选择停止，剩余论文未抽取。")

# ------------------------------
# 第2批：优先论文剩余部分
# ------------------------------
if not aborted_for_balance and second_batch and (AUTO_CONTINUE_REST in {"y", "yes"} or proceed):
    print(f"\n{'='*70}")
    print(f"开始第2批处理（优先论文）：{len(second_batch)} 篇")
    print(f"{'='*70}")
    
    progress_bar_2 = _iter_with_progress(second_batch, desc="Gemini [2/3] 优先论文")
    for pf in progress_bar_2:
        _process_one(pf, IN_SCOPE_DIR, progress_bar_2 if HAVE_TQDM else None)
        if aborted_for_balance:
            break
        if SLEEP_SECS > 0:
            time.sleep(SLEEP_SECS)
    
    if not aborted_for_balance:
        print(f"\n第2批完成：当前总计成功 {success} 篇，失败 {failed} 篇，跳过 {skipped} 篇")

# ------------------------------
# 第3批：普通论文
# ------------------------------
if not aborted_for_balance and third_batch and (AUTO_CONTINUE_REST in {"y", "yes"} or proceed):
    print(f"\n{'='*70}")
    print(f"开始第3批处理（普通论文）：{len(third_batch)} 篇")
    print(f"{'='*70}")
    
    progress_bar_3 = _iter_with_progress(third_batch, desc="Gemini [3/3] 普通论文")
    for pf in progress_bar_3:
        _process_one(pf, OUT_SCOPE_DIR, progress_bar_3 if HAVE_TQDM else None)
        if aborted_for_balance:
            break
        if SLEEP_SECS > 0:
            time.sleep(SLEEP_SECS)
    
    if not aborted_for_balance:
        print(f"\n第3批完成：当前总计成功 {success} 篇，失败 {failed} 篇，跳过 {skipped} 篇")

# ------------------------------
# 最终总结
# ------------------------------
print(f"\n{'='*70}")
print(f"Gemini 处理结束")
print(f"{'='*70}")
print(f"成功: {success} 篇")
print(f"失败: {failed} 篇")
print(f"状态: {'因余额不足提前终止' if aborted_for_balance else '正常完成'}")
print(f"{'='*70}")

# 保存详细抽取日志
logger.save()
print(f"{'='*70}")