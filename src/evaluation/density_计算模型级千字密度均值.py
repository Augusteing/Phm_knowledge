import csv
from pathlib import Path
from collections import defaultdict
import argparse

"""
重构说明:
1. 移除硬编码 ROOT, 自动依据脚本路径向上定位包含 统计结果/按论文统计 的目录。
2. 增加 CLI:
   --root <path>   可强制指定指标二目录 (包含 统计结果/按论文统计)。
   --input <csv>   指定统一口径输入 CSV (默认自动寻找)。
   --models m1 m2  仅输出这些模型 (过滤)。
   --out-dir <dir> 覆盖默认 输出目录 (统计结果/模型统计)。
3. 保持输出文件名不变: 模型_实体关系千字密度均值.csv
4. 新增列: 未加权论文数(paper_count) 已存在, 同时保留原结构。
"""

SCRIPT_DIR = Path(__file__).resolve().parent
INDICATOR_DIR = SCRIPT_DIR.parent  # 指标二：实体关系密度

def auto_locate_input(root: Path) -> Path:
    cand = root / '统计结果' / '按论文统计' / '按论文模型_实体关系千字密度_统一口径.csv'
    if cand.exists():
        return cand
    # 向上两级尝试
    for p in [root.parent, root.parent.parent]:
        c = p / '统计结果' / '按论文统计' / '按论文模型_实体关系千字密度_统一口径.csv'
        if c.exists():
            return c
    return cand  # 返回默认 (可能不存在)

def default_out_dir(root: Path) -> Path:
    return root / '统计结果' / '模型统计'

def parse_args():
    ap = argparse.ArgumentParser(description='计算模型级千字密度均值 (自动 root)')
    ap.add_argument('--root', type=Path, help='指标二：实体关系密度 目录路径 (包含 统计结果 子目录)')
    ap.add_argument('--input', type=Path, help='统一口径按论文 CSV 路径 (按论文模型_实体关系千字密度_统一口径.csv)')
    ap.add_argument('--models', nargs='*', help='仅统计这些模型')
    ap.add_argument('--out-dir', type=Path, help='输出目录 (默认 统计结果/模型统计)')
    ap.add_argument('--debug', action='store_true')
    return ap.parse_args()

def resolve_root(args_root: Path) -> Path:
    if args_root:
        return args_root
    # 依据脚本位置回溯, 直到出现 '统计结果/按论文统计'
    for parent in [INDICATOR_DIR, *INDICATOR_DIR.parents]:
        target = parent / '统计结果' / '按论文统计'
        if target.exists():
            return parent
    return INDICATOR_DIR

def load_rows(path: Path):
    if not path.exists():
        raise FileNotFoundError(f'未找到输入文件: {path}')
    with path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def main():
    args = parse_args()
    root = resolve_root(args.root)
    if args.input:
        input_csv = args.input
    else:
        input_csv = auto_locate_input(root)
    out_dir = args.out_dir if args.out_dir else default_out_dir(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / '模型_实体关系千字密度均值.csv'

    if args.debug:
        print(f'[调试] root={root}')
        print(f'[调试] input_csv={input_csv}')
        print(f'[调试] out_dir={out_dir}')

    data_per_model = defaultdict(lambda: {
        'entity_density_list': [],
        'relation_density_list': [],
        'total_entities': 0,
        'total_relations': 0,
        'total_clean_len': 0,
        'paper_count': 0,
    })

    for row in load_rows(input_csv):
        try:
            model = row['模型']
        except KeyError:
            continue
        if args.models and model not in args.models:
            continue
        try:
            clean_len = int(row['去空白字符数'])
            ent_cnt = int(row['实体数量'])
            rel_cnt = int(row['关系数量'])
            ent_density = float(row['实体千字密度(按去空白)'])
            rel_density = float(row['关系千字密度(按去空白)'])
        except (KeyError, ValueError):
            continue
        m = data_per_model[model]
        m['entity_density_list'].append(ent_density)
        m['relation_density_list'].append(rel_density)
        m['total_entities'] += ent_cnt
        m['total_relations'] += rel_cnt
        m['total_clean_len'] += clean_len
        m['paper_count'] += 1

    with out_csv.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow([
            '模型',
            '实体千字密度_未加权均值','关系千字密度_未加权均值',
            '实体千字密度_加权','关系千字密度_加权',
            '覆盖论文数','总实体数','总关系数','总去空白字符数'
        ])
        for model in sorted(data_per_model.keys()):
            m = data_per_model[model]
            unweighted_ent_mean = (sum(m['entity_density_list']) / len(m['entity_density_list'])) if m['entity_density_list'] else 0.0
            unweighted_rel_mean = (sum(m['relation_density_list']) / len(m['relation_density_list'])) if m['relation_density_list'] else 0.0
            if m['total_clean_len'] > 0:
                weighted_ent = m['total_entities'] * 1000 / m['total_clean_len']
                weighted_rel = m['total_relations'] * 1000 / m['total_clean_len']
            else:
                weighted_ent = weighted_rel = 0.0
            w.writerow([
                model,
                f'{unweighted_ent_mean:.4f}', f'{unweighted_rel_mean:.4f}',
                f'{weighted_ent:.4f}', f'{weighted_rel:.4f}',
                m['paper_count'], m['total_entities'], m['total_relations'], m['total_clean_len']
            ])

    print('模型级均值输出 ->', out_csv)


if __name__ == '__main__':
    main()
