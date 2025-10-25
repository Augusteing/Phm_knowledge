"""
文件操作工具函数
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Union


def read_json(file_path: Union[str, Path]) -> Union[Dict, List]:
    """
    读取JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        解析后的数据（字典或列表）
    """
    file_path = Path(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(
    data: Union[Dict, List],
    file_path: Union[str, Path],
    indent: int = 2,
    ensure_ascii: bool = False
) -> None:
    """
    写入JSON文件
    
    Args:
        data: 要写入的数据
        file_path: 输出文件路径
        indent: 缩进空格数
        ensure_ascii: 是否确保ASCII编码
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)


def read_markdown(file_path: Union[str, Path]) -> str:
    """
    读取Markdown文件
    
    Args:
        file_path: Markdown文件路径
        
    Returns:
        文件内容
    """
    file_path = Path(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text(content: str, file_path: Union[str, Path]) -> None:
    """
    写入文本文件
    
    Args:
        content: 文本内容
        file_path: 输出文件路径
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False
) -> List[Path]:
    """
    列出目录中的文件
    
    Args:
        directory: 目录路径
        pattern: 文件名模式（支持通配符）
        recursive: 是否递归搜索子目录
        
    Returns:
        文件路径列表
    """
    directory = Path(directory)
    
    if recursive:
        return sorted(directory.rglob(pattern))
    else:
        return sorted(directory.glob(pattern))


def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    确保目录存在，不存在则创建
    
    Args:
        directory: 目录路径
        
    Returns:
        目录Path对象
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
