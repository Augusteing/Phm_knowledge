"""
配置加载器
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict
from string import Template


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    加载YAML配置文件，支持环境变量替换
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # 替换环境变量 ${VAR_NAME}
    config_content = _substitute_env_vars(config_content)
    
    # 解析YAML
    config = yaml.safe_load(config_content)
    
    return config


def _substitute_env_vars(content: str) -> str:
    """
    替换字符串中的环境变量
    
    Args:
        content: 包含环境变量的字符串
        
    Returns:
        替换后的字符串
    """
    # 使用Template进行替换
    template = Template(content)
    
    # 获取所有环境变量
    env_vars = dict(os.environ)
    
    # 安全替换（缺失的变量保持原样）
    try:
        return template.substitute(env_vars)
    except KeyError:
        # 如果有缺失的变量，使用safe_substitute
        return template.safe_substitute(env_vars)


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    通过点分隔的路径获取配置值
    
    Args:
        config: 配置字典
        key_path: 键路径，如 "api.base_url"
        default: 默认值
        
    Returns:
        配置值
        
    Example:
        >>> config = {"api": {"base_url": "https://api.example.com"}}
        >>> get_config_value(config, "api.base_url")
        'https://api.example.com'
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def update_config_value(config: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    通过点分隔的路径更新配置值
    
    Args:
        config: 配置字典
        key_path: 键路径，如 "api.base_url"
        value: 新值
    """
    keys = key_path.split('.')
    current = config
    
    # 导航到最后一个键之前
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # 设置值
    current[keys[-1]] = value


def save_config(config: Dict[str, Any], config_path: str = "config/config.yaml") -> None:
    """
    保存配置到YAML文件
    
    Args:
        config: 配置字典
        config_path: 配置文件路径
    """
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
