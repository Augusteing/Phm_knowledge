import os
import json  # <-- 1. 引入 json 库
from pathlib import Path
import joblib
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

# ─── 配置 ─────────────────────────────────────────────────────
# 将路径固定为相对于脚本上级目录（主题聚类根目录）的绝对路径，避免因运行位置不同导致找不到文件
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_SOURCE_DIR = str((ROOT_DIR / "无标注原文").resolve())
CLUSTERS_PATH   = str((ROOT_DIR / "数据结果" / "embedding_clusters_with_paragraph_annots.json").resolve())
UMAP_MODEL_PATH = str((ROOT_DIR / "数据结果" / "umap_model.joblib").resolve())
MODEL_NAME      = "BAAI/bge-large-zh-v1.5"
OUTPUT_DIR      = str((ROOT_DIR / "数据结果" / "s_modules").resolve())
TOP_K           = 3      # 每篇文档的示例数

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ─── 路径存在性检查与打印 ─────────────────────────────────
print("[路径解析] ROOT_DIR:", ROOT_DIR)
print("[路径解析] DATA_SOURCE_DIR:", DATA_SOURCE_DIR)
print("[路径解析] CLUSTERS_PATH:", CLUSTERS_PATH)
print("[路径解析] UMAP_MODEL_PATH:", UMAP_MODEL_PATH)
print("[路径解析] OUTPUT_DIR:", OUTPUT_DIR)

def _ensure_exists(path: str, desc: str):
    if not os.path.exists(path):                          
        raise FileNotFoundError(f"未找到{desc}：{path}")

_ensure_exists(DATA_SOURCE_DIR, "数据源目录")
_ensure_exists(CLUSTERS_PATH, "聚类示例库JSON文件")
_ensure_exists(UMAP_MODEL_PATH, "UMAP模型文件")

# ─── 加载示例库与 UMAP ────────────────────────────────────
with open(CLUSTERS_PATH, "r", encoding="utf-8") as f:
    library = json.load(f)
umap_model = joblib.load(UMAP_MODEL_PATH)

# ─── 加载文本嵌入模型 ──────────────────────────────────────────
tokenizer   = AutoTokenizer.from_pretrained(MODEL_NAME)
embed_model = AutoModel.from_pretrained(MODEL_NAME).to(device).eval()

def embed(text: str) -> np.ndarray:
    inputs = tokenizer("[CLS] " + text, return_tensors="pt",
                       truncation=True, max_length=512).to(device)
    with torch.no_grad():
        out = embed_model(**inputs)
    return out.last_hidden_state[:, 0].squeeze().cpu().numpy()

def to_5d(vec: np.ndarray) -> np.ndarray:
    return umap_model.transform([vec])[0]

# ─── 注释识别与规范化工具 ─────────────────────────────────────
ALT_REL_KEYS = [
    ("head", "tail"),
    ("from", "to"),
    ("subject", "object"),
    ("source", "target"),
]

def is_relation_ann(ann: dict) -> bool:
    if not isinstance(ann, dict):
        return False
    for hk, tk in ALT_REL_KEYS:
        if hk in ann and tk in ann:
            return True
    return False

def extract_relation_norm(ann: dict) -> dict:
    """将多种关系键规范为 {type, head, tail}，缺省值为空串。"""
    rtype = ann.get("type", "") if isinstance(ann, dict) else ""
    head = tail = ""
    if isinstance(ann, dict):
        for hk, tk in ALT_REL_KEYS:
            if hk in ann and tk in ann:
                head = ann.get(hk, "")
                tail = ann.get(tk, "")
                break
    return {"type": rtype, "head": head, "tail": tail}

def is_entity_ann(ann: dict) -> bool:
    return isinstance(ann, dict) and ("text" in ann)

def split_annotations(annotations) -> tuple[list, list]:
    entities, relations = [], []
    if annotations:
        for ann in annotations:
            if is_relation_ann(ann):
                relations.append(extract_relation_norm(ann))
            elif is_entity_ann(ann):
                entities.append({
                    "type": ann.get("type", ""),
                    "text": ann.get("text", ""),
                })
    return entities, relations

# ─── 准备库向量与簇标签 ─────────────────────────────────────
lib_vecs_5d  = np.array([e["embedding_5d"] for e in library])
lib_clusters = np.array([e["cluster"]     for e in library])

# ─── 生成 S 模块 ─────────────────────────────────────────────
os.makedirs(OUTPUT_DIR, exist_ok=True)

for fn in sorted(os.listdir(DATA_SOURCE_DIR)):
    if not fn.endswith(".md"):
        continue

    # 1) 读取全文用于向量化（示例选取）
    path = os.path.join(DATA_SOURCE_DIR, fn)
    with open(path, "r", encoding="utf-8") as f:
        full_text = f.read().strip()

    # 2) 嵌入 + 降维 + 相似度
    vec    = embed(full_text)
    vec5d  = to_5d(vec)
    sims   = cosine_similarity([vec5d], lib_vecs_5d)[0]
    primary_cluster = lib_clusters[sims.argmax()]
    idxs_in_cluster = np.where(lib_clusters == primary_cluster)[0]
    sims_in_cluster = sims[idxs_in_cluster]
    
    # 按相似度排序（同簇内），仅筛选同时具备实体与关系的示例
    sorted_idxs = idxs_in_cluster[np.argsort(sims_in_cluster)[::-1]]
    def has_entities_and_relations(ann_list) -> bool:
        ents, rels = split_annotations(ann_list)
        return bool(ents) and bool(rels)

    selected: list[dict] = []
    used_idx: set[int] = set()

    # 优先从同簇内选择既有实体又有关系的示例
    for idx in sorted_idxs:
        if len(selected) >= TOP_K:
            break
        candidate = library[idx]
        if has_entities_and_relations(candidate.get("annotations")):
            selected.append(candidate)
            used_idx.add(idx)

    # 如果同簇内不足，从全库按相似度补足，仍然要求实体与关系同时存在
    if len(selected) < TOP_K:
        all_sorted_idxs = np.argsort(sims)[::-1]
        for idx in all_sorted_idxs:
            if len(selected) >= TOP_K:
                break
            if idx in used_idx:
                continue
            candidate = library[idx]
            if has_entities_and_relations(candidate.get("annotations")):
                selected.append(candidate)
                used_idx.add(idx)

    # 3) 拼接 S 模块内容  <-- 2. 此处为核心修改区域
    if len(selected) < TOP_K:
        print(f"⚠️  警告：未找到足够的同时包含实体与关系的示例（需要 {TOP_K} 个，实际 {len(selected)} 个），跳过文档：{fn}")
        continue
        
    lines = [
        "【S：Few-Shot动态采样】",
        "以下示例均为与待抽取文本语义最相关的标注（不展示原段落），每个示例同时包含实体与关系字段：",
        ""
    ]
    for i, ex in enumerate(selected, 1):
        entities, relations = split_annotations(ex.get("annotations"))
        # 输出仅包含标注（不展示段落原文），并且强制包含两个字段
        annotation_json = {
            "entities": entities,
            "relations": relations,
        }
        json_string = json.dumps(annotation_json, ensure_ascii=False, indent=2)
        lines.append(f"示例{i}：")
        lines.append(f"```json\n{json_string}\n```")
        lines.append("")

   

    # 4) 保存到文件
    out_fp = os.path.join(OUTPUT_DIR, f"S_module_{fn.replace('.md', '.txt')}")
    with open(out_fp, "w", encoding="utf-8") as fo:
        fo.write("\n".join(lines))

    print(f"✔ 已生成 S 模块：{out_fp}")