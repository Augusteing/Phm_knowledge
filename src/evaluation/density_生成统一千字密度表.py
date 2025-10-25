import json
import re
import csv
from pathlib import Path
import argparse
from typing import Dict, List, Tuple

"""
重构说明:
1. 去除硬编码 ROOT (原指向 EXP-1), 增加 auto_detect_root() 依据存在的 '抽取/数据结果/提取结果_by_*' 目录自动定位实验根。
2. 动态发现模型: 扫描 抽取/数据结果 下形如 '提取结果_by_*' 的目录并确认存在 in_scope 子目录。
3. 增加 CLI:
   --root <path>         手动指定根 (优先级最高)
   --models m1 m2 ...    仅统计给定模型 (默认全部发现的模型)
   --paper-dir <path>    强制指定论文 markdown 目录
   --expected N          期望论文篇数 (仅用于提示, 不阻断)
   --debug               输出调试信息
4. 仍输出: 统一总表 + 各模型分表, 目录结构不变。
5. 兼容旧调用: 直接运行不带参数 => 自动 root + 全部模型。
"""

SCRIPT_DIR = Path(__file__).resolve().parent  # .../指标统计计算/指标二：实体关系密度/code
INDICATOR_DIR = SCRIPT_DIR.parent             # .../指标统计计算/指标二：实体关系密度

def auto_detect_root(start: Path) -> Path:
    """向上搜索包含 抽取/数据结果/提取结果_by_* 结构的目录, 以匹配数评分选最大者。"""
    candidates: List[Tuple[int, Path]] = []
    for parent in [start, *start.parents]:
        base = parent / '抽取' / '数据结果'
        if base.exists() and base.is_dir():
            pattern_dirs = list(base.glob('提取结果_by_*'))
            score = 0
            for d in pattern_dirs:
                if (d / 'in_scope').exists():
                    score += 2
                else:
                    score += 1
            if score > 0:
                candidates.append((score, parent))
        # 限制向上深度 (避免扫到盘符根) — 找到后继续记录, 最终取最大
        if parent == parent.parent:  # reached root
            break
    if not candidates:
        return start  # fallback
    # 取评分最高, 若并列取路径层级较深 (更接近 start)
    candidates.sort(key=lambda x: (x[0], -len(x[1].parts)), reverse=True)
    return candidates[0][1]


def discover_models(root: Path) -> Dict[str, Path]:
    base = root / '抽取' / '数据结果'
    models: Dict[str, Path] = {}
    if not base.exists():
        return models
    for d in base.glob('提取结果_by_*'):
        if not d.is_dir():
            continue
        name = d.name.split('提取结果_by_')[-1]
        in_scope = d / 'in_scope'
        if in_scope.exists():
            models[name] = in_scope
    return models


def choose_paper_dir(root: Path, override: Path = None) -> Path:
    """优先返回 需要评估的论文 目录 (50篇), 而不是选最大数量的上级目录。"""
    if override:
        return override
    eval_primary = root / '抽取' / '论文文献' / '需要评估的论文'
    if eval_primary.exists() and any(eval_primary.glob('*.md')):
        return eval_primary
    # 次优候选 (保持原顺序, 但不再用最大数量策略)
    for p in [
        root / '评估' / '需要评估的论文',
        root / '论文文献' / '需要评估的论文',
        root / '抽取' / '论文文献',
        root / '论文文献',
    ]:
        if p.exists() and any(p.glob('*.md')):
            return p
    return eval_primary  # fallback

def list_md_count(path: Path) -> int:
    try:
        return sum(1 for _ in path.glob('*.md'))
    except Exception:
        return 0

def debug_paper_dir(root: Path):
    print('[调试] 论文目录候选及其 .md 数量:')
    for idx, d in enumerate([
        root / '抽取' / '论文文献' / '需要评估的论文',
        root / '评估' / '需要评估的论文',
        root / '论文文献' / '需要评估的论文',
        root / '抽取' / '论文文献',
        root / '论文文献',
    ]):
        print(f"  - [{idx}] {d} -> {list_md_count(d)}")

def list_md_count(path: Path) -> int:
    try:
        return sum(1 for _ in path.glob('*.md'))
    except Exception:
        return 0

# 输出位置调整：指标统计计算/指标二：实体关系密度/统计结果/表格/
OUT_TABLE_DIR = INDICATOR_DIR / '统计结果' / '按论文统计'
OUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

# 统一总表
OUT_CSV = OUT_TABLE_DIR / '按论文模型_实体关系千字密度_统一口径.csv'

CODE_FENCE_PATTERN = re.compile(r"```[\s\S]*?```", re.MULTILINE)
INLINE_CODE_PATTERN = re.compile(r"`[^`]*`")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\([^)]*\)")
HEADING_PATTERN = re.compile(r"^#+.*$", re.MULTILINE)
QUOTE_PATTERN = re.compile(r"^>.*$", re.MULTILINE)
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
EMPHASIS_PATTERN = re.compile(r"[*_~]")
WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_and_count(text: str) -> int:
    """返回: 去 markdown 语法后再去全部空白的字符数 (不可逆清洗)."""
    # 去代码块 & 行内代码
    text = CODE_FENCE_PATTERN.sub('', text)
    text = INLINE_CODE_PATTERN.sub('', text)
    # 图片 / 链接 (放前防止残留方括号)
    text = IMAGE_PATTERN.sub('', text)
    text = LINK_PATTERN.sub('', text)
    # 标题 / 引用
    text = HEADING_PATTERN.sub('', text)
    text = QUOTE_PATTERN.sub('', text)
    # HTML 标记 与强调符
    text = HTML_TAG_PATTERN.sub('', text)
    text = EMPHASIS_PATTERN.sub('', text)
    # 去所有空白
    text = WHITESPACE_PATTERN.sub('', text)
    return len(text)


def read_markdown_lengths(paper_dir: Path):
    mapping = {}
    if not paper_dir.exists():
        return mapping
    for md in paper_dir.glob('*.md'):
        try:
            raw = md.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        raw_len = len(raw)
        cleaned_len = clean_and_count(raw)
        mapping[md.stem] = (raw_len, cleaned_len)
    return mapping


def load_json(path: Path):
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description='生成统一千字密度表 (自动 root / 模型发现)')
    parser.add_argument('--root', type=Path, help='手动指定实验根目录 (包含 抽取/数据结果)')
    parser.add_argument('--models', nargs='*', help='仅统计这些模型 (默认全部发现)')
    parser.add_argument('--paper-dir', type=Path, help='指定论文 markdown 目录 (覆盖自动检测)')
    parser.add_argument('--expected', type=int, default=50, help='期望论文篇数 (用于提示)')
    parser.add_argument('--debug', action='store_true', help='输出调试信息')
    args = parser.parse_args()

    start = args.root if args.root else auto_detect_root(SCRIPT_DIR)
    ROOT = start
    if args.debug:
        print(f'[调试] 采用 ROOT: {ROOT}')

    model_dirs = discover_models(ROOT)
    if not model_dirs:
        print('[警告] 未发现任何模型目录 (提取结果_by_*)')
    if args.models:
        # 过滤, 不存在的给出提示
        filtered = {}
        missing = []
        for m in args.models:
            if m in model_dirs:
                filtered[m] = model_dirs[m]
            else:
                missing.append(m)
        if missing:
            print('[警告] 下列模型未发现, 将忽略:', ', '.join(missing))
        model_dirs = filtered
    print('[信息] 统计模型列表:', ', '.join(sorted(model_dirs.keys())) or '<<空>>')

    paper_dir = choose_paper_dir(ROOT, args.paper_dir)
    print(f'[信息] 使用论文目录: {paper_dir}')
    if args.debug:
        debug_paper_dir(ROOT)

    paper_lengths = read_markdown_lengths(paper_dir)
    stems = sorted(paper_lengths.keys())
    if len(stems) != args.expected:
        print(f"[提示] 发现评估论文 {len(stems)} 篇 (期望{args.expected})，继续处理。")
        if args.debug and len(stems) == 0:
            print('[调试] 未找到任何 .md 文件, 请检查 --paper-dir 或目录结构。')

    # 模型 in_scope JSON 数量提示
    for m, d in model_dirs.items():
        json_count = len(list(d.glob('*.json')))
        print(f"[信息] 模型 {m} in_scope JSON 数: {json_count}")

    rows = []
    per_model_rows = {m: [] for m in model_dirs.keys()}
    total_entities = 0
    total_relations = 0
    total_clean_len = 0

    for stem in stems:
        raw_len, cleaned_len = paper_lengths[stem]
        base_len = max(cleaned_len, 1)
        for model, mdir in model_dirs.items():
            jpath = mdir / f'{stem}.json'
            ent_cnt = rel_cnt = 0
            if jpath.exists():
                data = load_json(jpath)
                if isinstance(data, dict):
                    entities = data.get('entities', []) or []
                    relations = data.get('relations', []) or []
                    ent_cnt = len(entities)
                    rel_cnt = len(relations)
            ent_density = ent_cnt * 1000 / base_len
            rel_density = rel_cnt * 1000 / base_len
            ratio = (rel_cnt / ent_cnt) if ent_cnt else 0
            row = [
                stem, model, raw_len, cleaned_len, ent_cnt, rel_cnt,
                f'{ent_density:.4f}', f'{rel_density:.4f}', f'{ratio:.4f}'
            ]
            rows.append(row)
            per_model_rows[model].append([
                stem, raw_len, cleaned_len, ent_cnt, rel_cnt,
                f'{ent_density:.4f}', f'{rel_density:.4f}', f'{ratio:.4f}'
            ])
            total_entities += ent_cnt
            total_relations += rel_cnt
            total_clean_len += cleaned_len

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow([
            '论文stem','模型','原始字符数','去空白字符数','实体数量','关系数量',
            '实体千字密度(按去空白)','关系千字密度(按去空白)','关系/实体比'
        ])
        w.writerows(rows)

    for model, mrows in per_model_rows.items():
        out_path = OUT_TABLE_DIR / f'{model}_按论文_实体关系千字密度.csv'
        with out_path.open('w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow([
                '论文stem','原始字符数','去空白字符数','实体数量','关系数量',
                '实体千字密度(按去空白)','关系千字密度(按去空白)','关系/实体比'
            ])
            w.writerows(mrows)
        print('已生成分模型表 ->', out_path)

    weighted_entity_density = (total_entities * 1000 / total_clean_len) if total_clean_len else 0
    weighted_relation_density = (total_relations * 1000 / total_clean_len) if total_clean_len else 0
    print('已生成统一口径 CSV ->', OUT_CSV)
    print('总体加权实体千字密度:', f'{weighted_entity_density:.4f}')
    print('总体加权关系千字密度:', f'{weighted_relation_density:.4f}')


if __name__ == '__main__':
    main()
