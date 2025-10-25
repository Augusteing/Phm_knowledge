# -*- coding: utf-8 -*-
"""
Cluster visualization script
Created: 2025-09-15
Purpose: Generate multiple visualizations for clustering results of aviation PHM papers.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set global font to Times New Roman (English)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
plt.rcParams['axes.unicode_minus'] = False

# 路径配置
CODE_DIR = Path(__file__).parent
BASE_DIR = CODE_DIR.parent
DATA_DIR = BASE_DIR / "数据结果"

def load_cluster_data():
    """Load clustering data"""
    print("Loading cluster data...")
    
    # Load cluster results
    cluster_file = DATA_DIR / "embedding_clusters_with_paragraph_annots.json"
    if not cluster_file.exists():
        raise FileNotFoundError(f"Cluster result file not found: {cluster_file}")
    
    with open(cluster_file, 'r', encoding='utf-8') as f:
        cluster_data = json.load(f)
    
    # Load embedding vectors
    vector_file = DATA_DIR / "embedding_vectors.json"
    if not vector_file.exists():
        raise FileNotFoundError(f"Embedding vector file not found: {vector_file}")
    
    with open(vector_file, 'r', encoding='utf-8') as f:
        vector_data = json.load(f)
    
    print(f"Loaded: {len(cluster_data)} clustered samples")
    return cluster_data, vector_data

def prepare_dataframe(cluster_data, vector_data):
    """Prepare DataFrame for visualization"""
    print("Preparing dataframe...")
    
    # Extract required fields
    data_list = []
    for item in cluster_data:
        paper_name = item.get('file', 'Unknown paper')
        cluster_id = item.get('cluster', -1)
        paragraph_text = item.get('text', '')
        embedding = item.get('embedding', None)
        
        if embedding is not None:
            data_list.append({
                'paper_name': paper_name,
                'cluster_id': cluster_id,
                'paragraph_text': paragraph_text,
                'vector': embedding,
                'title_short': paper_name.split('_')[0] if '_' in paper_name else paper_name
            })
    
    df = pd.DataFrame(data_list)
    print(f"Dataframe ready: {len(df)} rows, {len(df['cluster_id'].unique())} clusters")
    return df

def plot_cluster_distribution(df, save_path):
    """Plot cluster size distribution bar chart"""
    print("Plotting cluster distribution...")
    
    plt.figure(figsize=(12, 6))
    
    # Count samples per cluster
    cluster_counts = df['cluster_id'].value_counts().sort_index()
    
    # Plot bars
    bars = plt.bar(range(len(cluster_counts)), cluster_counts.values, 
                   color=plt.cm.Set3(np.linspace(0, 1, len(cluster_counts))))
    
    plt.xlabel('Cluster ID', fontsize=12)
    plt.ylabel('Paper count', fontsize=12)
    plt.title('Paper count per cluster', fontsize=14, fontweight='bold')
    plt.xticks(range(len(cluster_counts)), cluster_counts.index)
    
    # Value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10)
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path / "cluster_distribution.png", dpi=300, bbox_inches='tight')
    plt.show()

def plot_2d_clusters(df, save_path):
    """Plot 2D t-SNE scatter of clusters"""
    print("Plotting 2D t-SNE scatter...")
    
    try:
        from sklearn.manifold import TSNE
        from sklearn.decomposition import PCA
    except ImportError:
        print("scikit-learn not available, skip 2D scatter...")
        return
    
    # 提取向量矩阵
    vectors = np.array([item for item in df['vector'].tolist()])
    print(f"Vector shape: {vectors.shape}")
    
    # 使用t-SNE降维到2D
    print("Running t-SNE dimensionality reduction...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(vectors)-1))
    coords_2d = tsne.fit_transform(vectors)
    
    # 绘制散点图
    plt.figure(figsize=(12, 8))
    
    unique_clusters = sorted(df['cluster_id'].unique())
    colors = plt.cm.Set3(np.linspace(0, 1, len(unique_clusters)))
    
    for i, cluster_id in enumerate(unique_clusters):
        mask = df['cluster_id'] == cluster_id
        cluster_coords = coords_2d[mask]
        
        # No legend labels to avoid overcrowded legend
        plt.scatter(cluster_coords[:, 0], cluster_coords[:, 1], 
                   c=[colors[i]], 
                   alpha=0.7, s=60)
    
    plt.xlabel('t-SNE Dimension 1', fontsize=12)
    plt.ylabel('t-SNE Dimension 2', fontsize=12)
    plt.title('Paper clustering visualization (t-SNE)', fontsize=14, fontweight='bold')
    # Legend removed as requested
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path / "clusters_2d_tsne.png", dpi=300, bbox_inches='tight')
    plt.show()

def plot_cluster_heatmap(df, save_path):
    """Plot cluster similarity heatmap"""
    print("Plotting cluster similarity heatmap...")
    
    try:
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        print("scikit-learn not available, skip similarity heatmap...")
        return
    
    # Compute mean vector per cluster
    cluster_centers = {}
    for cluster_id in df['cluster_id'].unique():
        cluster_vectors = df[df['cluster_id'] == cluster_id]['vector'].tolist()
        cluster_centers[cluster_id] = np.mean(cluster_vectors, axis=0)
    
    # Compute cosine similarity between cluster centers
    cluster_ids = sorted(cluster_centers.keys())
    similarity_matrix = np.zeros((len(cluster_ids), len(cluster_ids)))
    
    for i, id1 in enumerate(cluster_ids):
        for j, id2 in enumerate(cluster_ids):
            sim = cosine_similarity([cluster_centers[id1]], [cluster_centers[id2]])[0][0]
            similarity_matrix[i][j] = sim
    
    # Plot heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(similarity_matrix, 
                xticklabels=[f'Cluster {i}' for i in cluster_ids],
                yticklabels=[f'Cluster {i}' for i in cluster_ids],
                annot=True, fmt='.3f', cmap='coolwarm',
                center=0, square=True)
    
    plt.title('Cluster similarity heatmap', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path / "cluster_similarity_heatmap.png", dpi=300, bbox_inches='tight')
    plt.show()

def analyze_cluster_keywords(df, save_path):
    """Analyze top keywords per cluster"""
    print("Analyzing cluster keywords...")
    
    # Collect all texts per cluster
    cluster_texts = {}
    for cluster_id in df['cluster_id'].unique():
        cluster_df = df[df['cluster_id'] == cluster_id]
        all_text = ' '.join(cluster_df['paper_name'].tolist())
        cluster_texts[cluster_id] = all_text
    
    # Simple frequency-based keyword extraction (Chinese tokens will remain as-is)
    import re
    from collections import Counter
    
    cluster_keywords = {}
    for cluster_id, text in cluster_texts.items():
        # 提取中文词汇
        chinese_words = re.findall(r'[\u4e00-\u9fff]+', text)
        # 过滤掉长度小于2的词
        chinese_words = [word for word in chinese_words if len(word) >= 2]
        # 统计词频
        word_counts = Counter(chinese_words)
        # 获取前10个高频词
        top_words = word_counts.most_common(10)
        cluster_keywords[cluster_id] = top_words
    
    # Save keyword analysis result
    keywords_file = save_path / "cluster_keywords.json"
    with open(keywords_file, 'w', encoding='utf-8') as f:
        json.dump(cluster_keywords, f, ensure_ascii=False, indent=2)
    
    # Plot keywords
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, (cluster_id, keywords) in enumerate(cluster_keywords.items()):
        if i >= 6:  # Show at most 6 clusters
            break
            
        if keywords:
            words, counts = zip(*keywords)
            ax = axes[i]
            bars = ax.bar(range(len(words)), counts, color=plt.cm.Set3(i/len(cluster_keywords)))
            ax.set_title(f'Cluster {cluster_id} - Keywords', fontweight='bold')
            ax.set_xticks(range(len(words)))
            ax.set_xticklabels(words, rotation=45, ha='right')
            ax.set_ylabel('Frequency')
            
            # Value labels
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                       f'{count}', ha='center', va='bottom', fontsize=9)
    
    # Hide unused subplots
    for i in range(len(cluster_keywords), len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle('Keyword distribution across clusters', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path / "cluster_keywords_distribution.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Keyword analysis finished. Saved to: {keywords_file}")

def generate_cluster_report(df, save_path):
    """Generate cluster analysis report"""
    print("Generating cluster report...")
    
    report_lines = []
    report_lines.append("# PHM Papers Cluster Analysis Report")
    report_lines.append(f"Generated at: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Overall statistics
    report_lines.append("## Overall statistics")
    report_lines.append(f"- Total samples: {len(df)}")
    report_lines.append(f"- Number of clusters: {len(df['cluster_id'].unique())}")
    report_lines.append(f"- Avg samples per cluster: {len(df) / len(df['cluster_id'].unique()):.1f}")
    report_lines.append("")
    
    # Details per cluster
    report_lines.append("## Cluster details")
    for cluster_id in sorted(df['cluster_id'].unique()):
        cluster_df = df[df['cluster_id'] == cluster_id]
        report_lines.append(f"### Cluster {cluster_id}")
        report_lines.append(f"- Samples: {len(cluster_df)}")
        report_lines.append("- Representative papers:")
        
        for i, paper in enumerate(cluster_df['title_short'].head(5)):
            report_lines.append(f"  {i+1}. {paper}")
        
        if len(cluster_df) > 5:
            report_lines.append(f"  ... and {len(cluster_df) - 5} more papers")
        report_lines.append("")
    
    # Save report
    report_file = save_path / "cluster_analysis_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Cluster report saved to: {report_file}")

def main():
    """Main"""
    print("Starting cluster visualization analysis...")
    
    # 创建输出目录
    output_dir = BASE_DIR / "可视化结果"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Load data
        cluster_data, vector_data = load_cluster_data()
        df = prepare_dataframe(cluster_data, vector_data)
        
        if len(df) == 0:
            print("Error: no valid cluster data found")
            return
        
        # Generate plots
        plot_cluster_distribution(df, output_dir)
        plot_2d_clusters(df, output_dir)
        plot_cluster_heatmap(df, output_dir)
        analyze_cluster_keywords(df, output_dir)
        generate_cluster_report(df, output_dir)
        
        print(f"\n✅ Visualization complete! All results saved to: {output_dir}")
        print("Generated files:")
        for file in output_dir.glob("*"):
            print(f"  - {file.name}")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()