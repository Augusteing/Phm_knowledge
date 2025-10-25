import os
import re
from pathlib import Path

def find_missing_md_files():
    """
    找出还没有转换为MD格式的PDF文件
    比较paper文件夹中的PDF文件和markdown文件夹中的MD文件
    """
    
    # 定义文件夹路径
    paper_folder = Path("E:\知识图谱构建\9.15之前的实验\文献处理\paper")
    markdown_folder = Path("E:\知识图谱构建\9.15之前的实验\文献处理\markdown")
    
    # 检查文件夹是否存在
    if not paper_folder.exists():
        print(f"错误: {paper_folder} 文件夹不存在")
        return
    
    if not markdown_folder.exists():
        print(f"错误: {markdown_folder} 文件夹不存在")
        return
    
    # 获取所有PDF文件的基础文件名（不包含扩展名）
    pdf_files = set()
    for pdf_file in paper_folder.glob("*.pdf"):
        # 移除.pdf扩展名
        base_name = pdf_file.stem
        pdf_files.add(base_name)
    
    # 获取所有MD文件对应的原始文献名称
    md_files = set()
    for md_file in markdown_folder.glob("*.md"):
        # 从MD文件名中提取原始文献名称
        # 格式: 文献名称_MinerU__时间戳.md
        md_name = md_file.stem
        
        # 使用正则表达式提取文献名称（去掉_MinerU__时间戳部分）
        match = re.match(r'^(.+?)_MinerU__\d+$', md_name)
        if match:
            original_name = match.group(1)
            md_files.add(original_name)
        else:
            # 如果不匹配预期格式，保留原文件名用于调试
            print(f"警告: MD文件名格式不符合预期: {md_file.name}")
            md_files.add(md_name)
    
    # 找出还没有转换的PDF文件
    missing_files = pdf_files - md_files
    
    # 输出结果
    print(f"PDF文件总数: {len(pdf_files)}")
    print(f"已转换的MD文件数: {len(md_files)}")
    print(f"遗漏的文献数量: {len(missing_files)}")
    print("\n" + "="*50)
    
    if missing_files:
        print("以下PDF文件还没有转换为MD格式:")
        print("-" * 50)
        for i, filename in enumerate(sorted(missing_files), 1):
            print(f"{i:2d}. {filename}.pdf")
    else:
        print("✅ 所有PDF文件都已转换为MD格式！")
    
    return missing_files

def save_missing_list(missing_files, output_file="missing_files.txt"):
    """
    将遗漏的文件列表保存到文本文件中
    """
    if missing_files:
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"遗漏的文献列表 (生成时间: {os.getcwd()})\n")
            f.write("="*50 + "\n")
            f.write(f"总共遗漏 {len(missing_files)} 个文献:\n\n")
            
            for i, filename in enumerate(sorted(missing_files), 1):
                f.write(f"{i:2d}. {filename}.pdf\n")
        
        print(f"\n📝 遗漏文件列表已保存到: {output_path.absolute()}")

if __name__ == "__main__":
    print("🔍 正在检查遗漏的文献...")
    print("="*50)
    
    missing = find_missing_md_files()
    
    if missing:
        save_missing_list(missing)
        print(f"\n💡 建议: 可以使用MinerU对这 {len(missing)} 个PDF文件进行转换")
    else:
        print("\n🎉 太好了！没有遗漏的文献需要转换。")