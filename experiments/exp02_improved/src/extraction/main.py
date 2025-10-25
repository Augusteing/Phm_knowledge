# -*- coding: utf-8 -*-
"""
实体提取主入口
支持运行 DeepSeek、Gemini、Kimi 三种提取器
"""
import os
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# 项目路径
SCRIPT_DIR = Path(__file__).parent
SRC_DIR = SCRIPT_DIR.parent
EXP_DIR = SRC_DIR.parent

# 可用的提取器
EXTRACTORS = {
    "deepseek": {
        "script": SCRIPT_DIR / "exact_deepseek.py",
        "name": "DeepSeek",
        "env_vars": ["DEEPSEEK_API_KEY"],
        "optional_vars": ["DEEPSEEK_MAX_TOKENS_BASE", "DEEPSEEK_MAX_TOKENS_CAP", "DEEPSEEK_TEMPERATURE"]
    },
    "gemini": {
        "script": SCRIPT_DIR / "exact_gemini.py",
        "name": "Gemini",
        "env_vars": ["HIAPI_API_KEY", "GEMINI_API_KEY"],  # 任一即可
        "optional_vars": ["HIAPI_BASE_URL", "EXTRACT_SLEEP_SECS", "EXTRACT_MAX_RETRIES"]
    },
    "kimi": {
        "script": SCRIPT_DIR / "exact_kimi.py",
        "name": "Kimi",
        "env_vars": ["KIMI_API_KEY", "MOONSHOT_API_KEY"],  # 任一即可
        "optional_vars": []
    }
}


def print_banner():
    """打印欢迎横幅"""
    print("=" * 70)
    print(" " * 20 + "实体提取工具 v1.0")
    print("=" * 70)
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {EXP_DIR}")
    print("=" * 70)
    print()


def check_environment(extractor_key):
    """检查提取器所需的环境变量"""
    config = EXTRACTORS[extractor_key]
    
    # 检查必需的环境变量（至少一个存在）
    env_vars = config["env_vars"]
    has_key = any(os.getenv(var) for var in env_vars)
    
    if not has_key:
        print(f"❌ {config['name']}: 缺少必需的环境变量")
        print(f"   请设置以下任一变量: {', '.join(env_vars)}")
        return False
    
    # 显示已配置的环境变量
    configured = [var for var in env_vars if os.getenv(var)]
    print(f"✓ {config['name']}: 已配置 {configured[0]}")
    
    # 显示可选的环境变量
    optional = [var for var in config.get("optional_vars", []) if os.getenv(var)]
    if optional:
        print(f"  可选配置: {', '.join(optional)}")
    
    return True


def check_data_paths():
    """检查数据路径是否存在"""
    data_dir = EXP_DIR / "data" / "raw" / "papers"
    priority_dir = data_dir / "priority"
    general_dir = data_dir / "general"
    
    issues = []
    
    if not data_dir.exists():
        issues.append(f"数据目录不存在: {data_dir}")
    
    priority_count = 0
    general_count = 0
    
    if priority_dir.exists():
        priority_count = len(list(priority_dir.glob("*.md")))
    else:
        issues.append(f"优先论文目录不存在: {priority_dir}")
    
    if general_dir.exists():
        general_count = len(list(general_dir.glob("*.md")))
    
    if issues:
        print("\n⚠️  数据路径警告:")
        for issue in issues:
            print(f"   - {issue}")
        print()
    
    print(f"📊 论文统计:")
    print(f"   - 优先论文: {priority_count} 篇")
    print(f"   - 普通论文: {general_count} 篇")
    print(f"   - 合计: {priority_count + general_count} 篇")
    print()
    
    return priority_count > 0 or general_count > 0


def check_prompt_file():
    """检查 prompt 文件是否存在（支持实验二命名与环境变量覆盖）。"""
    prompt_dir = EXP_DIR / "config" / "prompt"
    env_path = os.getenv("EXTRACT_PROMPT_FILE", "").strip()
    if env_path:
        p = Path(env_path)
        if not p.is_absolute():
            p = EXP_DIR / env_path
        if p.exists():
            print(f"✓ Prompt 文件(ENV): {p}")
            return True
        print(f"⚠️  EXTRACT_PROMPT_FILE 指向的文件不存在: {p}")

    candidates = [
        prompt_dir / "prompt实验二.txt"
        
    ]
    for c in candidates:
        if c.exists():
            print(f"✓ Prompt 文件: {c}")
            return True
    # fallback: 唯一 .txt
    if prompt_dir.exists():
        txts = list(prompt_dir.glob("*.txt"))
        if len(txts) == 1:
            print(f"✓ Prompt 文件: {txts[0]}")
            return True
    print(f"⚠️  未找到 prompt 文件，请在 {prompt_dir} 放置 prompt实验二.txt 或设置 EXTRACT_PROMPT_FILE")
    return False


def run_extractor(extractor_key, dry_run=False):
    """运行指定的提取器"""
    config = EXTRACTORS[extractor_key]
    script_path = config["script"]
    
    if not script_path.exists():
        print(f"❌ 脚本不存在: {script_path}")
        return False
    
    print("\n" + "=" * 70)
    print(f"🚀 启动 {config['name']} 提取器")
    print("=" * 70)
    
    if dry_run:
        print(f"[DRY RUN] 将执行: python {script_path}")
        return True
    
    try:
        # 关键修复：不要用管道捕获输出，直接继承父进程的 TTY
        # 这样子进程中的 tqdm 能检测到控制台并进行单行刷新，避免多行重复输出
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"  # 确保子进程即时输出

        result = subprocess.run(
            [sys.executable, str(script_path)],
            env=env,
            check=False
        )

        if result.returncode == 0:
            print(f"\n✅ {config['name']} 提取完成")
            return True
        else:
            print(f"\n❌ {config['name']} 提取失败 (退出码: {result.returncode})")
            return False
            
    except KeyboardInterrupt:
        print(f"\n⚠️  用户中断 {config['name']} 提取")
        # 使用 subprocess.run 后没有进程句柄可终止，这里仅返回 False
        return False
    except Exception as e:
        print(f"\n❌ 运行 {config['name']} 时出错: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="实体提取工具 - 支持 DeepSeek、Gemini、Kimi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 运行所有提取器
  python main.py --all
  
  # 运行指定提取器
  python main.py --extractors deepseek gemini
  
  # 检查环境但不运行
  python main.py --check-only
  
  # 仅检查环境配置，不验证数据
  python main.py --extractors kimi --dry-run

环境变量配置:
  DeepSeek: DEEPSEEK_API_KEY
  Gemini:   HIAPI_API_KEY 或 GEMINI_API_KEY
  Kimi:     KIMI_API_KEY 或 MOONSHOT_API_KEY
  
  通用:     IN_SCOPE_LIMIT, AUTO_CONTINUE_REST
        """
    )
    
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="运行所有可用的提取器"
    )
    
    parser.add_argument(
        "-e", "--extractors",
        nargs="+",
        choices=list(EXTRACTORS.keys()),
        help="指定要运行的提取器"
    )
    
    parser.add_argument(
        "-c", "--check-only",
        action="store_true",
        help="仅检查环境和数据，不运行提取"
    )
    
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="模拟运行，不实际执行提取"
    )
    
    parser.add_argument(
        "--skip-data-check",
        action="store_true",
        help="跳过数据路径检查"
    )
    
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 确定要运行的提取器
    if args.all:
        selected_extractors = list(EXTRACTORS.keys())
    elif args.extractors:
        selected_extractors = args.extractors
    else:
        # 如果没有指定，显示帮助
        parser.print_help()
        return
    
    print(f"📋 选择的提取器: {', '.join([EXTRACTORS[k]['name'] for k in selected_extractors])}")
    print()
    
    # 检查环境变量
    print("🔍 检查环境配置...")
    print("-" * 70)
    env_check_results = {}
    for extractor_key in selected_extractors:
        env_check_results[extractor_key] = check_environment(extractor_key)
    print()
    
    # 检查数据路径
    if not args.skip_data_check:
        print("🔍 检查数据路径...")
        print("-" * 70)
        has_data = check_data_paths()
        if not has_data:
            print("❌ 没有找到论文文件，请检查数据目录")
            return
    
    # 检查 prompt 文件
    print("🔍 检查配置文件...")
    print("-" * 70)
    check_prompt_file()
    print()
    
    # 如果只是检查，到此结束
    if args.check_only:
        print("✓ 环境检查完成")
        return
    
    # 过滤出环境检查通过的提取器
    valid_extractors = [k for k in selected_extractors if env_check_results[k]]
    
    if not valid_extractors:
        print("❌ 没有可用的提取器（环境变量未配置）")
        return
    
    failed_env = [k for k in selected_extractors if not env_check_results[k]]
    if failed_env:
        print(f"⚠️  跳过环境未配置的提取器: {', '.join([EXTRACTORS[k]['name'] for k in failed_env])}")
        print()
    
    # 运行提取器
    results = {}
    for i, extractor_key in enumerate(valid_extractors, 1):
        print(f"\n[{i}/{len(valid_extractors)}] 处理 {EXTRACTORS[extractor_key]['name']}")
        results[extractor_key] = run_extractor(extractor_key, dry_run=args.dry_run)
    
    # 打印总结
    print("\n" + "=" * 70)
    print(" " * 25 + "执行总结")
    print("=" * 70)
    
    for extractor_key, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{EXTRACTORS[extractor_key]['name']:15s} - {status}")
    
    print("=" * 70)
    
    # 显示输出位置
    outputs_dir = EXP_DIR / "outputs" / "extractions"
    print(f"\n📁 提取结果保存在: {outputs_dir}")
    print(f"📊 查看日志: {outputs_dir / '<provider>' / 'logs'}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
