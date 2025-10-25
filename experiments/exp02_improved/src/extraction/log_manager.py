# -*- coding: utf-8 -*-
"""
统一的日志管理模块
用于保存详细的抽取日志，格式参考 RAG 脚本
"""
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


class ExtractionLogger:
    """抽取过程日志记录器"""
    
    def __init__(self, log_dir: str, provider_name: str):
        """
        初始化日志记录器
        
        Args:
            log_dir: 日志保存目录（如 outputs/logs/deepseek）
            provider_name: 提供商名称（deepseek/gemini/kimi）
        """
        self.log_dir = log_dir
        self.provider_name = provider_name
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成带时间戳的日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"extraction_log_{timestamp}.json")
        
        # 初始化日志结构
        self.logs: List[Dict[str, Any]] = []
        self.total_papers = 0
        self.successful_extractions = 0
        self.failed_extractions = 0
    
    def add_log_entry(
        self,
        paper: str,
        success: bool,
        duration_seconds: float,
        entity_count: int = 0,
        relation_count: int = 0,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        error: Optional[str] = None,
        **kwargs  # 额外的字段
    ):
        """
        添加一条日志记录
        
        Args:
            paper: 论文文件名（相对路径，如 priority/xxx.md）
            success: 是否成功
            duration_seconds: 耗时（秒）
            entity_count: 实体数量
            relation_count: 关系数量
            prompt_tokens: prompt token 数
            completion_tokens: completion token 数
            total_tokens: 总 token 数
            error: 错误信息（如果失败）
            **kwargs: 其他额外字段
        """
        log_entry = {
            "paper": paper,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration_seconds, 3),
            "entity_count": entity_count,
            "relation_count": relation_count,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "success": success
        }
        
        # 添加错误信息（如果有）
        if error:
            log_entry["error"] = error
        
        # 添加额外字段
        log_entry.update(kwargs)
        
        self.logs.append(log_entry)
        
        # 更新统计
        if success:
            self.successful_extractions += 1
        else:
            self.failed_extractions += 1
    
    def set_total_papers(self, total: int):
        """设置总论文数"""
        self.total_papers = total
    
    def save(self):
        """保存日志到文件"""
        log_data = {
            "total_papers": self.total_papers,
            "successful_extractions": self.successful_extractions,
            "failed_extractions": self.failed_extractions,
            "logs": self.logs
        }
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n日志已保存到: {self.log_file}")
        return self.log_file
    
    def get_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        return {
            "total_papers": self.total_papers,
            "successful": self.successful_extractions,
            "failed": self.failed_extractions,
            "success_rate": (
                round(self.successful_extractions / self.total_papers * 100, 2)
                if self.total_papers > 0 else 0
            )
        }


def count_entities_and_relations(json_data: Dict[str, Any]) -> tuple[int, int]:
    """
    从抽取结果 JSON 中统计实体和关系数量
    
    Args:
        json_data: 抽取的 JSON 结果
    
    Returns:
        (entity_count, relation_count)
    """
    entity_count = 0
    relation_count = 0
    
    # 统计实体
    if "entities" in json_data:
        entities = json_data["entities"]
        if isinstance(entities, list):
            entity_count = len(entities)
        elif isinstance(entities, dict):
            # 如果是按类型分组的字典
            entity_count = sum(len(v) if isinstance(v, list) else 1 for v in entities.values())
    
    # 统计关系
    if "relations" in json_data:
        relations = json_data["relations"]
        if isinstance(relations, list):
            relation_count = len(relations)
        elif isinstance(relations, dict):
            # 如果是按类型分组的字典
            relation_count = sum(len(v) if isinstance(v, list) else 1 for v in relations.values())
    
    return entity_count, relation_count
