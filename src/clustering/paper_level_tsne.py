# -*- coding: utf-8 -*-
"""
论文级别t-SNE聚类可视化脚本
聚合段落数据到论文级别，生成清晰的聚类图
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from pathlib import Path
from collections import defaultdict

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def main():
    """主函数"""
    print("开始论文级别t-SNE可视化...")
    
    # 路径配置
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "数据结果"
    output_dir = base_dir / "可视化结果"
    output_dir.mkdir(exist_ok=True)
    
    # 加载段落级别的聚类数据
    cluster_file = data_dir / "embedding_clusters_with_paragraph_annots.json"
    with open(cluster_file, 'r', encoding='utf-8') as f:
        paragraph_data = json.load(f)
    
    print(f"加载了 {len(paragraph_data)} 个段落级别的数据项")
    
    # 聚合到论文级别
    paper_data = defaultdict(list)
    
    for item in paragraph_data:
        filename = item['file']
        if filename.endswith('.md'):
            filename = filename[:-3]
        
        paper_data[filename].append({
            'cluster': item['cluster'],
            'embedding': np.array(item['embedding'])
        })
    
    print(f"聚合为 {len(paper_data)} 篇论文的数据")
    
    # 为每篇论文计算平均嵌入向量和主要聚类
    paper_records = []
    
    for filename, paragraphs in paper_data.items():
        # 计算平均嵌入向量
        embeddings = np.array([p['embedding'] for p in paragraphs])
        avg_embedding = np.mean(embeddings, axis=0)
        
        # 选择最频繁的聚类作为论文的聚类
        clusters = [p['cluster'] for p in paragraphs]
        main_cluster = max(set(clusters), key=clusters.count)
        
        paper_records.append({
            'filename': filename,
            'cluster_id': main_cluster,
            'embedding': avg_embedding,
            'paragraph_count': len(paragraphs)
        })
    
    df = pd.DataFrame(paper_records)
    print(f"生成 {len(df)} 篇论文的记录")
    print(f"聚类分布: {dict(df['cluster_id'].value_counts().sort_index())}")
    
    # 执行t-SNE降维
    embeddings = np.stack(df['embedding'].values)
    print("执行t-SNE降维...")
    
    tsne = TSNE(
        n_components=2,
        random_state=42,
        perplexity=min(50, len(embeddings) - 1),  # 使用更大的perplexity
        max_iter=1000,
        learning_rate=200,  # 调整学习率
        verbose=1
    )
    tsne_result = tsne.fit_transform(embeddings)
    
    # 绘制散点图
    plt.figure(figsize=(14, 10))
    
    unique_clusters = sorted(df['cluster_id'].unique())
    n_clusters = len(unique_clusters)
    
    # 使用更好的颜色映射
    colors = plt.cm.tab20(np.linspace(0, 1, min(n_clusters, 20)))
    if n_clusters > 20:
        # 如果聚类超过20个，使用连续色彩映射
        colors = plt.cm.viridis(np.linspace(0, 1, n_clusters))
    
    for i, cluster_id in enumerate(unique_clusters):
        mask = df['cluster_id'] == cluster_id
        points = tsne_result[mask]
        cluster_size = np.sum(mask)
        
        plt.scatter(
            points[:, 0], points[:, 1],
            c=[colors[i % len(colors)]], 
            label=f'聚类 {cluster_id} ({cluster_size}篇)',
            alpha=0.7,
            s=80,  # 稍大的点
            edgecolors='white',  # 白色边框
            linewidth=0.5
        )
    
    plt.title('论文聚类可视化 (t-SNE)', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('t-SNE 维度 1', fontsize=14)
    plt.ylabel('t-SNE 维度 2', fontsize=14)
    
    # 调整图例
    if n_clusters <= 15:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    else:
        # 聚类过多时不显示图例
        plt.text(0.02, 0.98, f'共{n_clusters}个聚类', transform=plt.gca().transAxes,
                verticalalignment='top', fontsize=12,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # 保存图片
    save_path = output_dir / "paper_level_tsne.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"论文级别t-SNE图片已保存: {save_path}")
    
    plt.show()
    
    # 打印统计信息
    print(f"\n聚类统计:")
    for cluster_id in sorted(unique_clusters):
        count = sum(df['cluster_id'] == cluster_id)
        print(f"聚类 {cluster_id}: {count} 篇论文")

if __name__ == "__main__":
    main()