import os
import json
import torch
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm

# =============================
# 设置模型（bge-large-zh-v1.5）
# =============================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "BAAI/bge-large-zh-v1.5"

print("🔄 正在加载模型，请稍候...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to(device).eval()
print("✅ 模型加载完成！")

# =============================
# 嵌入函数（取 CLS 向量）
# =============================
def embed_text(text: str):
    try:
        # bge模型建议在文本前添加 "[CLS]" 以提升效果
        text = "[CLS] " + text
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        # CLS token 表征
        embedding = outputs.last_hidden_state[:, 0].squeeze().cpu().numpy()
        return embedding.tolist()
    except Exception as e:
        print(f"[⚠️ 错误] 嵌入失败：{e}")
        return None

# =============================
# 主处理函数
# =============================
def process_markdown_files(md_folder: str, output_path: str):
    all_embeddings = []
    md_files = [f for f in os.listdir(md_folder) if f.endswith(".md")]
    
    for filename in tqdm(md_files, desc="📄 正在处理文档"):
        filepath = os.path.join(md_folder, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 按段落切分（以空行为段落分界）
            paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 10]
            for idx, para in enumerate(paragraphs):
                vector = embed_text(para)
                if vector:
                    all_embeddings.append({
                        "file": filename,
                        "paragraph_index": idx,
                        "text": para,
                        "embedding": vector
                    })
        except Exception as e:
            print(f"[⚠️ 错误] 无法处理 {filename}：{e}")

    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_embeddings, f, indent=2, ensure_ascii=False)
    print(f"✅ 向量库已保存到：{output_path}")

# =============================
# 执行主程序
# =============================
if __name__ == "__main__":
    input_folder = r"E:\知识图谱构建\9.15之前的实验\EXP-4\主题聚类\有标注原文"
    # 保存到主题聚类目录下的 数据结果 文件夹（使用绝对路径，便于在不同工作目录运行）
    output_file = r"E:\知识图谱构建\9.15之前的实验\EXP-4\主题聚类\数据结果\embedding_vectors.json"
    process_markdown_files(input_folder, output_file)
