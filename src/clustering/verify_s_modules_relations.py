import re
import json
from pathlib import Path

"""验证 数据结果/s_modules 目录下 S_module_*.txt 文件中的 JSON 片段，
确保 relations 中的每个对象均为 {type, head, tail} 结构（仅这三键，且值为字符串或可转为字符串）。
"""

ROOT = Path(__file__).resolve().parents[1]
S_MODULE_DIR = ROOT / '数据结果' / 's_modules'

CODE_BLOCK_RE = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)

def check_rel_obj(rel: dict) -> tuple[bool, str]:
    if not isinstance(rel, dict):
        return False, 'not_dict'
    keys = set(rel.keys())
    expected = {'type','head','tail'}
    if not expected.issubset(keys):
        return False, f'missing:{sorted(expected-keys)}'
    if keys - expected:
        return False, f'extra:{sorted(keys-expected)}'
    for k in ('type','head','tail'):
        v = rel.get(k)
        if v is None:
            return False, f'none_value:{k}'
        # 允许数字但统一转为字符串无报错
        if not isinstance(v, (str, int, float)):
            return False, f'bad_type:{k}:{type(v).__name__}'
    return True, ''

def main():
    if not S_MODULE_DIR.exists():
        print('[ERROR] S_module 目录不存在:', S_MODULE_DIR)
        return
    files = sorted(S_MODULE_DIR.glob('S_module_*.txt'))
    total_files = len(files)
    checked_blocks = 0
    total_rel = 0
    ok_rel = 0
    violations = []
    files_with_no_rel = 0

    for fp in files:
        text = fp.read_text(encoding='utf-8', errors='ignore')
        blocks = CODE_BLOCK_RE.findall(text)
        file_rel_count = 0
        for block in blocks:
            try:
                obj = json.loads(block)
            except Exception:
                continue
            checked_blocks += 1
            rels = obj.get('relations') if isinstance(obj, dict) else None
            if not rels:
                continue
            if not isinstance(rels, list):
                violations.append((fp.name, 'relations_not_list'))
                continue
            for rel in rels:
                total_rel += 1
                ok, reason = check_rel_obj(rel)
                if ok:
                    ok_rel += 1
                    file_rel_count += 1
                else:
                    violations.append((fp.name, reason, rel))
        if file_rel_count == 0:
            files_with_no_rel += 1

    print('== 校验结果 ==')
    print('S_module 文件数     :', total_files)
    print('解析到的 JSON 片段数:', checked_blocks)
    print('关系总数            :', total_rel)
    print('合规关系数          :', ok_rel)
    print('无关系示例的文件数  :', files_with_no_rel)
    if violations:
        print('发现违规条目数      :', len(violations))
        # 列出前 10 条
        for it in violations[:10]:
            print('[VIOLATION]', it[0], '|', it[1])
    else:
        print('未发现违规关系结构，全部为 {type, head, tail}')

if __name__ == '__main__':
    main()
