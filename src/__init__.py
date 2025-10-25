"""
知识图谱构建工具包
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# 导出主要模块
from . import extraction
from . import evaluation
from . import clustering
from . import preprocessing
from . import utils

__all__ = [
    "extraction",
    "evaluation", 
    "clustering",
    "preprocessing",
    "utils",
]
