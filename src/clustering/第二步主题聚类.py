import json
import os
import numpy as np
import umap
import hdbscan
import joblib

# ─── 路径配置 ─────────────────────────────────────────────────────
BASE_DIR = r"E:\知识图谱构建\9.15之前的实验\EXP-4\主题聚类"
EMBEDDING_PATH      = os.path.join(BASE_DIR, "数据结果", "embedding_vectors.json")
ANNOTATIONS_DIR     = os.path.join(BASE_DIR, "聚类论文标注结果")
OUTPUT_PATH         = os.path.join(BASE_DIR, "数据结果", "embedding_clusters_with_paragraph_annots.json")
UMAP_MODEL_PATH     = os.path.join(BASE_DIR, "数据结果", "umap_model.joblib")

# ─── 1. 读取第一步生成的向量库 ─────────────────────────────────────────
with open(EMBEDDING_PATH, "r", encoding="utf-8") as f:
    paragraphs = json.load(f)
# paragraphs 是列表，每项包含 "file", "paragraph_index", "text", "embedding"

# ─── 2. 加载并扁平化标注文件 ───────────────────────────────────────────
annotations_map = {}
for fname in os.listdir(ANNOTATIONS_DIR):
    if not fname.endswith(".json"):
        continue
    md_name = fname.replace(".json", ".md")
    with open(os.path.join(ANNOTATIONS_DIR, fname), "r", encoding="utf-8") as fa:
        raw = json.load(fa)
    # 扁平化：合并 entities 与 relations 两个列表
    ents = raw.get("entities", []) if isinstance(raw, dict) else []
    rels = raw.get("relations", []) if isinstance(raw, dict) else []
    annotations_map[md_name] = ents + rels

# ─── 3. 提取向量用于降维 ────────────────────────────────────────────
embeddings = np.array([p["embedding"] for p in paragraphs])

# ─── 4. UMAP 降维 ───────────────────────────────────────────────────
print("UMAP 降维中...")
reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=5, random_state=42)
embeddings_5d = reducer.fit_transform(embeddings)

# 保存 UMAP 模型
os.makedirs(os.path.dirname(UMAP_MODEL_PATH), exist_ok=True)
joblib.dump(reducer, UMAP_MODEL_PATH)
print(f"✅ UMAP 模型已保存至 {UMAP_MODEL_PATH}")

# ─── 5. HDBSCAN 聚类 ─────────────────────────────────────────────────
print("HDBSCAN 聚类中...")
clusterer = hdbscan.HDBSCAN(min_cluster_size=3, metric='euclidean')
labels = clusterer.fit_predict(embeddings_5d)

# ─── 6. 合并聚类标签、降维向量、段落级过滤与去重 ────────────────────────
for idx, para in enumerate(paragraphs):
    para["cluster"]      = int(labels[idx])
    para["embedding_5d"] = embeddings_5d[idx].tolist()

    md_name = para["file"]
    text    = para["text"]
    raw_anns= annotations_map.get(md_name, [])

    # ① 段落级过滤
    filtered = []
    for ann in raw_anns:
        # 实体标注包含 "text" 字段
        if ann.get("text") and ann["text"] in text:
            filtered.append(ann)
        # 关系标注包含 "head" 与 "tail"
        elif ann.get("head") and ann.get("tail") and ann["head"] in text and ann["tail"] in text:
            filtered.append(ann)

    # ② 去重：确保同一(type, text)或(type, head, tail)只保留一次
    seen = set()
    unique_anns = []
    for ann in filtered:
        if "text" in ann:
            key = (ann["type"], ann["text"])
        else:
            key = (ann["type"], ann["head"], ann["tail"])
        if key not in seen:
            seen.add(key)
            unique_anns.append(ann)

    para["annotations"] = unique_anns

# ─── 7. 保存结果 ─────────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as fo:
    json.dump(paragraphs, fo, indent=2, ensure_ascii=False)

print(f"✅ 第二步完成，已生成文件：{OUTPUT_PATH}")
