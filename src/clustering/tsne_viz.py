# -*- coding: utf-8 -*-
"""
t-SNE聚类可视化脚本
只专注于生成一张t-SNE散点图
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def main():
    """主函数"""
    print("开始t-SNE可视化...")
    
    # 路径配置
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "数据结果"
    output_dir = base_dir / "可视化结果"
    output_dir.mkdir(exist_ok=True)
    
    # 加载聚类数据
    cluster_file = data_dir / "embedding_clusters_with_paragraph_annots.json"
    with open(cluster_file, 'r', encoding='utf-8') as f:
        cluster_data = json.load(f)
    
    # 加载词向量
    vector_file = data_dir / "embedding_vectors.json"
    with open(vector_file, 'r', encoding='utf-8') as f:
        vector_data = json.load(f)
    
    print(f"加载了 {len(cluster_data)} 个聚类项，{len(vector_data)} 个向量")
    
    # 创建文件名到向量的映射
    file_to_vector = {}
    for item in vector_data:
        filename = item['file']  # 字段名是 'file' 不是 'filename'
        if filename.endswith('.md'):
            filename = filename[:-3]
        file_to_vector[filename] = np.array(item['embedding'])
    
    # 准备数据
    data_rows = []
    for item in cluster_data:
        filename = item['file']
        if filename.endswith('.md'):
            filename = filename[:-3]
        
        if filename in file_to_vector:
            data_rows.append({
                'cluster_id': item['cluster'],
                'embedding': file_to_vector[filename]
            })
    
    df = pd.DataFrame(data_rows)
    print(f"匹配到 {len(df)} 条有效记录")
    
    # 执行t-SNE降维
    embeddings = np.stack(df['embedding'].values)
    print("执行t-SNE降维...")
    
    tsne = TSNE(
        n_components=2,
        random_state=42,
        perplexity=min(30, len(embeddings) - 1),
        max_iter=1000
    )
    tsne_result = tsne.fit_transform(embeddings)
    
    # 绘制散点图
    plt.figure(figsize=(12, 8))
    
    unique_clusters = sorted(df['cluster_id'].unique())
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_clusters)))
    
    for i, cluster_id in enumerate(unique_clusters):
        mask = df['cluster_id'] == cluster_id
        points = tsne_result[mask]
        
        plt.scatter(
            points[:, 0], points[:, 1],
            c=[colors[i]], 
            label=f'聚类 {cluster_id}',
            alpha=0.7,
            s=60
        )
    
    plt.title('论文聚类可视化 (t-SNE)', fontsize=16, fontweight='bold')
    plt.xlabel('t-SNE 维度 1', fontsize=12)
    plt.ylabel('t-SNE 维度 2', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # 保存图片
    save_path = output_dir / "tsne_visualization.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"图片已保存: {save_path}")
    
    plt.show()

if __name__ == "__main__":
    main()