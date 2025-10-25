"""
实体关系抽取模块

提供从文本中抽取实体和关系的功能
"""

from .extractor import EntityRelationExtractor
from .llm_client import LLMClient

__all__ = ["EntityRelationExtractor", "LLMClient"]
