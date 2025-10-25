# -*- coding: utf-8 -*-
"""
数据检查脚本 - 查看聚类数据结构
"""

import json
from pathlib import Path

# 路径配置
CODE_DIR = Path(__file__).parent
BASE_DIR = CODE_DIR.parent
DATA_DIR = BASE_DIR / "数据结果"

def check_data_structure():
    """检查数据文件结构"""
    
    # 检查聚类结果文件
    cluster_file = DATA_DIR / "embedding_clusters_with_paragraph_annots.json"
    print(f"检查文件: {cluster_file}")
    
    if cluster_file.exists():
        with open(cluster_file, 'r', encoding='utf-8') as f:
            cluster_data = json.load(f)
        
        print(f"聚类数据长度: {len(cluster_data)}")
        print(f"前3个样本的键:")
        for i, item in enumerate(cluster_data[:3]):
            print(f"  样本 {i+1}: {list(item.keys())}")
            print(f"  样本 {i+1} 内容预览: {str(item)[:200]}...")
            print()
    else:
        print("聚类结果文件不存在")
    
    # 检查向量文件
    vector_file = DATA_DIR / "embedding_vectors.json"
    print(f"检查文件: {vector_file}")
    
    if vector_file.exists():
        with open(vector_file, 'r', encoding='utf-8') as f:
            vector_data = json.load(f)
        
        print(f"向量数据长度: {len(vector_data)}")
        print(f"前3个样本的键:")
        for i, item in enumerate(vector_data[:3]):
            print(f"  样本 {i+1}: {list(item.keys())}")
            if 'embedding' in item:
                print(f"  样本 {i+1} 向量维度: {len(item['embedding'])}")
            print()
    else:
        print("向量文件不存在")

if __name__ == "__main__":
    check_data_structure()