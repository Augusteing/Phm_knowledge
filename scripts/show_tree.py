"""
生成项目目录结构树

用于查看和导出项目目录结构
"""
import os
from pathlib import Path
from typing import List, Set


# 忽略的目录和文件
IGNORE_DIRS: Set[str] = {
    '__pycache__', '.git', '.idea', '.vscode', 
    'node_modules', '.pytest_cache', '.mypy_cache',
    'EXP-1', 'EXP-2', 'EXP-3', 'EXP-3 - 改', 'EXP-4',  # 旧实验目录
    '论文文献',  # 旧论文目录
}

IGNORE_PATTERNS: Set[str] = {
    '*.pyc', '*.pyo', '*.pyd', '.DS_Store', 'Thumbs.db',
    '*.log', '*.tmp', '*.bak', '*.swp',
}


def should_ignore(path: Path) -> bool:
    """判断是否应该忽略该路径"""
    # 检查目录名
    if path.is_dir() and path.name in IGNORE_DIRS:
        return True
    
    # 检查文件模式
    for pattern in IGNORE_PATTERNS:
        if path.match(pattern):
            return True
    
    return False


def generate_tree(
    directory: Path,
    prefix: str = "",
    is_last: bool = True,
    max_depth: int = 5,
    current_depth: int = 0,
    show_hidden: bool = False
) -> List[str]:
    """
    生成目录树
    
    Args:
        directory: 目录路径
        prefix: 前缀字符串
        is_last: 是否是最后一个项目
        max_depth: 最大深度
        current_depth: 当前深度
        show_hidden: 是否显示隐藏文件
        
    Returns:
        目录树字符串列表
    """
    lines = []
    
    if current_depth >= max_depth:
        return lines
    
    try:
        # 获取所有项目并排序
        items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        
        # 过滤隐藏文件和需要忽略的项目
        if not show_hidden:
            items = [item for item in items if not item.name.startswith('.')]
        
        items = [item for item in items if not should_ignore(item)]
        
        for index, item in enumerate(items):
            is_last_item = index == len(items) - 1
            
            # 当前项目的连接符
            connector = "└── " if is_last_item else "├── "
            
            # 当前行
            if item.is_dir():
                line = f"{prefix}{connector}{item.name}/"
            else:
                line = f"{prefix}{connector}{item.name}"
            
            lines.append(line)
            
            # 如果是目录，递归处理
            if item.is_dir():
                # 下一级的前缀
                next_prefix = prefix + ("    " if is_last_item else "│   ")
                
                # 递归生成子树
                sub_lines = generate_tree(
                    item,
                    prefix=next_prefix,
                    is_last=is_last_item,
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                    show_hidden=show_hidden
                )
                lines.extend(sub_lines)
    
    except PermissionError:
        lines.append(f"{prefix}[Permission Denied]")
    
    return lines


def print_tree(
    root_dir: str = ".",
    max_depth: int = 5,
    show_hidden: bool = False,
    output_file: str = None
) -> None:
    """
    打印目录树
    
    Args:
        root_dir: 根目录路径
        max_depth: 最大显示深度
        show_hidden: 是否显示隐藏文件
        output_file: 输出文件路径（可选）
    """
    root = Path(root_dir).resolve()
    
    # 生成树
    print(f"\n{root.name}/")
    lines = generate_tree(root, max_depth=max_depth, show_hidden=show_hidden)
    
    # 输出
    tree_text = "\n".join(lines)
    print(tree_text)
    
    # 如果指定了输出文件，写入文件
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"{root.name}/\n")
            f.write(tree_text)
        
        print(f"\n✅ 目录树已保存到: {output_path}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成项目目录结构树")
    parser.add_argument(
        "--root",
        default=".",
        help="根目录路径（默认: 当前目录）"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=5,
        help="最大显示深度（默认: 5）"
    )
    parser.add_argument(
        "--hidden",
        action="store_true",
        help="是否显示隐藏文件"
    )
    parser.add_argument(
        "--output",
        help="输出文件路径（可选）"
    )
    
    args = parser.parse_args()
    
    print_tree(
        root_dir=args.root,
        max_depth=args.depth,
        show_hidden=args.hidden,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
