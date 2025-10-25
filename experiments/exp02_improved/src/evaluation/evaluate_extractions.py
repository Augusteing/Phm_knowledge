"""
实体关系抽取结果评估脚本
使用 Gemini 模型对抽取结果进行合理性评估

更新点：
- 采用 EXP 目录内的 outputs 结构：outputs/extractions/<model> → outputs/evaluations/<model>
- 递归扫描抽取结果文件（支持子目录，如 priority/general）
- Prompt 路径改为：EXP_DIR/config/prompt/prompt_eva.txt（若缺失则回退旧路径）
- 支持 CLI 参数：--outputs-dir 覆盖 outputs 根目录；--models 指定评估模型列表
"""
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm

# OpenAI SDK (Gemini 兼容接口)
from openai import OpenAI

# ------------------------------
# 路径配置
# ------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # exp01_baseline 根目录

# 评估 Prompt，优先使用用户提供的新位置；若不存在则尝试旧位置
EVAL_PROMPT_PRIMARY = PROJECT_ROOT / "config" / "prompt" / "prompt_eva.txt"
EVAL_PROMPT_FALLBACK = PROJECT_ROOT / "configs" / "prompts" / "prompt_eva.txt"

# 原始论文目录（用于提供上下文，如未来需要可使用）
PAPERS_DIR = PROJECT_ROOT / "data" / "raw" / "papers"

# Gemini 评估配置
EVAL_MODEL = "gemini-2.5-pro"
PROVIDER_NAME = "gemini_evaluator"

# ------------------------------
# 工具函数
# ------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def strip_code_fences(s: str) -> str:
    """去除 ```json ... ``` 样式的代码围栏"""
    if not isinstance(s, str):
        return s
    s = s.strip()
    if s.startswith("```") and s.endswith("```"):
        s = s[3:-3].strip()
        if "\n" in s:
            first_line, rest = s.split("\n", 1)
            if first_line.strip().lower() in {"json", "js", "javascript"}:
                s = rest
    # 尝试提取 { } 之间的内容
    first_brace = s.find('{')
    last_brace = s.rfind('}')
    if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
        s = s[first_brace:last_brace + 1]
    return s

def parse_json_response(content: str) -> dict:
    """解析 JSON 响应,自动清理代码围栏"""
    if not content:
        raise ValueError("API 返回了空内容")
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        cleaned = strip_code_fences(content)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON 解析失败: {e}")
            print(f"   原始内容长度: {len(content)} 字符")
            print(f"   清理后内容长度: {len(cleaned)} 字符")
            print(f"   清理后内容预览: {cleaned[:500]}")
            raise ValueError(f"无法解析 JSON: {e}")

def resolve_prompt_file() -> Path:
    if EVAL_PROMPT_PRIMARY.exists():
        return EVAL_PROMPT_PRIMARY
    if EVAL_PROMPT_FALLBACK.exists():
        return EVAL_PROMPT_FALLBACK
    raise FileNotFoundError(
        f"未找到评估 Prompt 文件。优先路径: {EVAL_PROMPT_PRIMARY}；回退路径: {EVAL_PROMPT_FALLBACK}"
    )

def init_client() -> OpenAI:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("请设置 GEMINI_API_KEY 环境变量")
    return OpenAI(api_key=api_key, base_url="https://hiapi.online/v1")

# ------------------------------
# 评估函数
# ------------------------------
def evaluate_extraction(client: OpenAI, eval_prompt_template: str, extraction_data: dict, paper_name: str, model_name: str) -> dict:
    """
    使用 Gemini 评估单个抽取结果
    
    Args:
        extraction_data: 抽取的实体和关系 JSON
        paper_name: 论文名称
        model_name: 抽取模型名称
    
    Returns:
        评估后的 JSON (添加了 evaluation 字段)
    """
    # 构建评估 Prompt
    extraction_json = json.dumps(extraction_data, ensure_ascii=False, indent=2)
    
    eval_prompt = eval_prompt_template + f"""

## 待评估的抽取结果

论文: {paper_name}
抽取模型: {model_name}

```json
{extraction_json}
```

请严格按照要求输出评估后的 JSON,为每个实体和关系添加 `evaluation` 字段。
"""
    
    # 调用 Gemini API
    try:
        response = client.chat.completions.create(
            model=EVAL_MODEL,
            messages=[
                {"role": "system", "content": "你是 PHM 领域的知识抽取评估专家。只输出严格的 JSON，不添加任何解释。"},
                {"role": "user", "content": eval_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        evaluated_data = parse_json_response(content)
        
        # 验证返回格式
        if "entities" not in evaluated_data or "relations" not in evaluated_data:
            raise ValueError(f"返回的 JSON 缺少必需字段: {evaluated_data.keys()}")
        
        return {
            "evaluated_data": evaluated_data,
            "raw_response": content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if hasattr(response, 'usage') else None
        }
        
    except Exception as e:
        print(f"❌ 评估失败: {e}")
        raise

# ------------------------------
# 批量评估
# ------------------------------
def evaluate_model_results(client: OpenAI, eval_prompt_template: str, model_name: str, extraction_dir: Path, eval_output_root: Path, eval_log_dir: Path, overwrite: bool = False):
    """评估单个模型的所有抽取结果"""
    
    print(f"\n{'='*80}")
    print(f"🔍 评估 {model_name} 模型的抽取结果")
    print(f"{'='*80}")
    
    # 获取所有 JSON 文件（递归）
    json_files = sorted(extraction_dir.rglob("*.json"))
    
    if not json_files:
        print(f"⚠️ 未找到任何 JSON 文件: {extraction_dir}")
        return
    
    print(f"📊 找到 {len(json_files)} 个抽取结果文件")
    
    # 创建模型专用输出目录（如 deepseek/gemini/kimi）
    model_eval_dir = eval_output_root / model_name.lower()
    os.makedirs(model_eval_dir, exist_ok=True)
    
    # 统计信息
    success_count = 0
    failed_count = 0
    total_correct_entities = 0
    total_incorrect_entities = 0
    total_correct_relations = 0
    total_incorrect_relations = 0
    
    # 评估日志
    eval_log = []
    
    # 逐个评估
    for json_file in tqdm(json_files, desc=f"评估 {model_name}", unit="篇"):
        paper_name = json_file.stem
        
        try:
            # 若已有评估结果且未指定覆盖，则跳过并纳入统计（断点续跑）
            eval_output_file = model_eval_dir / f"{paper_name}_evaluated.json"
            if eval_output_file.exists() and not overwrite:
                try:
                    with open(eval_output_file, 'r', encoding='utf-8') as ef:
                        evaluated = json.load(ef)
                    entities_correct = sum(1 for e in evaluated.get('entities', []) if e.get('evaluation') == '正确')
                    entities_incorrect = sum(1 for e in evaluated.get('entities', []) if e.get('evaluation') == '错误')
                    relations_correct = sum(1 for r in evaluated.get('relations', []) if r.get('evaluation') == '正确')
                    relations_incorrect = sum(1 for r in evaluated.get('relations', []) if r.get('evaluation') == '错误')

                    total_correct_entities += entities_correct
                    total_incorrect_entities += entities_incorrect
                    total_correct_relations += relations_correct
                    total_incorrect_relations += relations_incorrect

                    log_entry = {
                        "time": now_iso(),
                        "paper": paper_name,
                        "model": model_name,
                        "status": "skipped",
                        "reason": "exists",
                        "eval_time": 0,
                        "entities": {
                            "total": len(evaluated.get('entities', [])),
                            "correct": entities_correct,
                            "incorrect": entities_incorrect,
                            "uncertain": len(evaluated.get('entities', [])) - entities_correct - entities_incorrect
                        },
                        "relations": {
                            "total": len(evaluated.get('relations', [])),
                            "correct": relations_correct,
                            "incorrect": relations_incorrect,
                            "uncertain": len(evaluated.get('relations', [])) - relations_correct - relations_incorrect
                        },
                        "usage": None,
                        "output_file": str(eval_output_file)
                    }
                    eval_log.append(log_entry)
                    tqdm.write(f"   ⏭️ 跳过（已存在）: {paper_name}")
                    success_count += 1
                    continue
                except Exception as _e_skip:
                    tqdm.write(f"   ⚠️ 跳过失败，尝试重评: {paper_name}（原因: {_e_skip}）")

            # 读取抽取结果
            with open(json_file, 'r', encoding='utf-8') as f:
                extraction_data = json.load(f)
            
            # 调用评估
            tqdm.write(f"   📝 评估: {paper_name}")
            start_time = time.time()
            
            eval_result = evaluate_extraction(client, eval_prompt_template, extraction_data, paper_name, model_name)
            
            eval_time = time.time() - start_time
            
            # 只保存评估后的 JSON 结果
            with open(eval_output_file, 'w', encoding='utf-8') as f:
                json.dump(eval_result['evaluated_data'], f, ensure_ascii=False, indent=2)
            
            # 统计评估结果
            evaluated = eval_result['evaluated_data']
            entities_correct = sum(1 for e in evaluated.get('entities', []) if e.get('evaluation') == '正确')
            entities_incorrect = sum(1 for e in evaluated.get('entities', []) if e.get('evaluation') == '错误')
            relations_correct = sum(1 for r in evaluated.get('relations', []) if r.get('evaluation') == '正确')
            relations_incorrect = sum(1 for r in evaluated.get('relations', []) if r.get('evaluation') == '错误')
            
            total_correct_entities += entities_correct
            total_incorrect_entities += entities_incorrect
            total_correct_relations += relations_correct
            total_incorrect_relations += relations_incorrect
            
            # 记录日志
            log_entry = {
                "time": now_iso(),
                "paper": paper_name,
                "model": model_name,
                "status": "success",
                "eval_time": round(eval_time, 2),
                "entities": {
                    "total": len(evaluated.get('entities', [])),
                    "correct": entities_correct,
                    "incorrect": entities_incorrect,
                    "uncertain": len(evaluated.get('entities', [])) - entities_correct - entities_incorrect
                },
                "relations": {
                    "total": len(evaluated.get('relations', [])),
                    "correct": relations_correct,
                    "incorrect": relations_incorrect,
                    "uncertain": len(evaluated.get('relations', [])) - relations_correct - relations_incorrect
                },
                "usage": eval_result.get('usage'),
                "output_file": str(eval_output_file)
            }
            eval_log.append(log_entry)
            
            tqdm.write(f"   ✅ 实体: {entities_correct}/{len(evaluated.get('entities', []))} 正确, "
                      f"关系: {relations_correct}/{len(evaluated.get('relations', []))} 正确")
            
            success_count += 1
            
            # 避免 API 限流
            time.sleep(1)
            
        except Exception as e:
            tqdm.write(f"   ❌ 失败: {e}")
            
            # 记录失败日志
            log_entry = {
                "time": now_iso(),
                "paper": paper_name,
                "model": model_name,
                "status": "failed",
                "error": str(e)
            }
            eval_log.append(log_entry)
            
            failed_count += 1
            continue
    
    # 保存评估日志
    log_file = eval_log_dir / f"{model_name.lower()}_evaluation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(eval_log, f, ensure_ascii=False, indent=2)
    
    # 打印汇总
    print(f"\n{'='*80}")
    print(f"📊 {model_name} 评估汇总")
    print(f"{'='*80}")
    print(f"✅ 成功: {success_count}/{len(json_files)}")
    print(f"❌ 失败: {failed_count}/{len(json_files)}")
    
    if success_count > 0:
        total_entities = total_correct_entities + total_incorrect_entities
        total_relations = total_correct_relations + total_incorrect_relations
        
        entity_accuracy = (total_correct_entities / total_entities * 100) if total_entities > 0 else 0
        relation_accuracy = (total_correct_relations / total_relations * 100) if total_relations > 0 else 0
        
        print(f"\n实体准确率: {entity_accuracy:.2f}% ({total_correct_entities}/{total_entities})")
        print(f"关系准确率: {relation_accuracy:.2f}% ({total_correct_relations}/{total_relations})")
    
    print(f"\n💾 评估日志: {log_file}")
    print(f"📁 评估结果: {model_eval_dir}")
    
    return {
        "model": model_name,
        "success": success_count,
        "failed": failed_count,
        "total": len(json_files),
        "entity_accuracy": entity_accuracy if success_count > 0 else 0,
        "relation_accuracy": relation_accuracy if success_count > 0 else 0,
        "correct_entities": total_correct_entities,
        "incorrect_entities": total_incorrect_entities,
        "correct_relations": total_correct_relations,
        "incorrect_relations": total_incorrect_relations
    }

def detect_model_dir(model_name: str, extractions_root: Path) -> Optional[Path]:
    name = model_name.lower()
    candidates = [
        name,
        f"{name}_rag",
    ]
    for c in candidates:
        p = extractions_root / c
        if p.exists():
            return p
    return None


# ------------------------------
# 主程序
# ------------------------------
def main():
    parser = argparse.ArgumentParser(description="实体关系抽取结果质量评估")
    parser.add_argument(
        "--outputs-dir",
        type=str,
        default=str(PROJECT_ROOT / "outputs"),
        help="outputs 根目录（包含 extractions/evaluations/logs 等子目录）"
    )
    parser.add_argument(
        "--models",
        type=str,
        default="DeepSeek,Gemini,Kimi",
        help="要评估的模型列表，逗号分隔，例如: DeepSeek,Gemini"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="如已存在评估结果，是否强制覆盖重评（默认跳过以支持断点续跑）"
    )
    args = parser.parse_args()

    outputs_root = Path(args.outputs_dir).resolve()
    extractions_root = outputs_root / "extractions"
    eval_output_root = outputs_root / "evaluations"
    eval_log_dir = outputs_root / "logs" / "evaluation"
    os.makedirs(eval_output_root, exist_ok=True)
    os.makedirs(eval_log_dir, exist_ok=True)

    prompt_path = resolve_prompt_file()
    print("=" * 80)
    print("🔬 实体关系抽取结果质量评估")
    print("=" * 80)
    print(f"评估模型: {EVAL_MODEL}")
    print(f"评估 Prompt: {prompt_path}")
    print(f"outputs 根目录: {outputs_root}")

    print(f"📄 加载评估 Prompt: {prompt_path}")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        eval_prompt_template = f.read()
    print(f"✅ Prompt 长度: {len(eval_prompt_template)} 字符\n")

    client = init_client()

    # 评估指定模型
    models = [m.strip() for m in args.models.split(',') if m.strip()]
    all_results = []

    for model_name in models:
        model_dir = detect_model_dir(model_name, extractions_root)
        if model_dir is None:
            print(f"\n⚠️ 跳过 {model_name}: 未在 {extractions_root} 下找到目录（尝试过 {model_name.lower()} 与 *_rag）")
            continue

        result = evaluate_model_results(
            client=client,
            eval_prompt_template=eval_prompt_template,
            model_name=model_name,
            extraction_dir=model_dir,
            eval_output_root=eval_output_root,
            eval_log_dir=eval_log_dir,
            overwrite=args.overwrite,
        )
        all_results.append(result)

    # 生成对比报告
    if all_results:
        print("\n" + "=" * 80)
        print("📋 模型评估对比汇总")
        print("=" * 80)

        import pandas as pd

        summary_df = pd.DataFrame([
            {
                "模型": r["model"],
                "评估成功数": r["success"],
                "评估失败数": r["failed"],
                "实体准确率(%)": round(r["entity_accuracy"], 2),
                "关系准确率(%)": round(r["relation_accuracy"], 2),
                "正确实体数": r["correct_entities"],
                "错误实体数": r["incorrect_entities"],
                "正确关系数": r["correct_relations"],
                "错误关系数": r["incorrect_relations"]
            }
            for r in all_results
        ])

        print(summary_df.to_string(index=False))

        # 保存汇总
        summary_file = eval_output_root / f"evaluation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 评估汇总已保存: {summary_file}")

    print("\n" + "=" * 80)
    print("✅ 评估完成!")
    print("=" * 80)

if __name__ == "__main__":
    main()
