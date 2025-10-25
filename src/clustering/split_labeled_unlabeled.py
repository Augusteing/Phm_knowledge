#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分离有标注和无标注的论文原文
将聚类论文原文中的文件根据是否有对应的标注结果进行分类
"""

import os
import shutil
from pathlib import Path

def get_base_filename(filename):
    """
    提取文件的基础名称，用于匹配
    例如: "论文标题_MinerU__20250913053949.json" -> "论文标题_MinerU__20250913053949"
    """
    # 移除文件扩展名
    base_name = os.path.splitext(filename)[0]
    return base_name

def split_labeled_unlabeled():
    """
    主要功能函数：分离有标注和无标注的论文原文
    """
    # 定义路径
    base_dir = Path(r"E:\知识图谱构建\9.15之前的实验\EXP-4\主题聚类")
    labeled_results_dir = base_dir / "聚类论文标注结果"
    original_papers_dir = base_dir / "聚类论文原文"
    labeled_output_dir = base_dir / "有标注原文"
    unlabeled_output_dir = base_dir / "无标注原文"
    
    # 创建输出目录
    labeled_output_dir.mkdir(exist_ok=True)
    unlabeled_output_dir.mkdir(exist_ok=True)
    
    print(f"标注结果目录: {labeled_results_dir}")
    print(f"原文目录: {original_papers_dir}")
    print(f"有标注输出目录: {labeled_output_dir}")
    print(f"无标注输出目录: {unlabeled_output_dir}")
    
    # 获取所有标注结果文件的基础名称
    labeled_base_names = set()
    if labeled_results_dir.exists():
        for file in labeled_results_dir.glob("*.json"):
            base_name = get_base_filename(file.name)
            labeled_base_names.add(base_name)
    
    print(f"\n找到 {len(labeled_base_names)} 个标注结果文件")
    
    # 分类原文文件
    labeled_count = 0
    unlabeled_count = 0
    total_original_files = 0
    
    if original_papers_dir.exists():
        for file in original_papers_dir.glob("*.md"):
            total_original_files += 1
            base_name = get_base_filename(file.name)
            
            if base_name in labeled_base_names:
                # 有标注的文件
                destination = labeled_output_dir / file.name
                shutil.copy2(file, destination)
                labeled_count += 1
                print(f"有标注: {file.name}")
            else:
                # 无标注的文件
                destination = unlabeled_output_dir / file.name
                shutil.copy2(file, destination)
                unlabeled_count += 1
                print(f"无标注: {file.name}")
    
    # 输出统计结果
    print(f"\n=== 分类统计 ===")
    print(f"原文总数: {total_original_files}")
    print(f"标注结果总数: {len(labeled_base_names)}")
    print(f"有标注原文: {labeled_count}")
    print(f"无标注原文: {unlabeled_count}")
    
    # 验证
    if labeled_count + unlabeled_count == total_original_files:
        print("✓ 分类完成，数量校验通过")
    else:
        print("✗ 数量校验失败，请检查")
    
    # 显示缺失的标注文件（如果有的话）
    if labeled_count != len(labeled_base_names):
        print(f"\n注意: 有 {len(labeled_base_names) - labeled_count} 个标注结果没有对应的原文文件")
        
        # 找出没有对应原文的标注文件
        original_base_names = set()
        for file in original_papers_dir.glob("*.md"):
            base_name = get_base_filename(file.name)
            original_base_names.add(base_name)
        
        missing_originals = labeled_base_names - original_base_names
        if missing_originals:
            print("缺失原文的标注文件:")
            for missing in missing_originals:
                print(f"  - {missing}")

def main():
    """主函数"""
    try:
        print("开始分离有标注和无标注的论文原文...")
        split_labeled_unlabeled()
        print("\n分离任务完成！")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()