"""
知识图谱构建项目安装脚本
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取README内容
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# 读取requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, encoding="utf-8") as f:
        requirements = [
            line.strip() for line in f 
            if line.strip() and not line.startswith('#') and not line.startswith('python')
        ]
else:
    requirements = []

setup(
    name="kg-construction",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="基于大语言模型的知识图谱构建系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Augusteing/entities",
    project_urls={
        "Bug Tracker": "https://github.com/Augusteing/entities/issues",
        "Documentation": "https://github.com/Augusteing/entities/docs",
        "Source Code": "https://github.com/Augusteing/entities",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
        "ml": [
            "scikit-learn>=1.3.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
        ],
        "nlp": [
            "spacy>=3.5.0",
            "networkx>=3.1",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "ipykernel>=6.23.0",
            "notebook>=6.5.4",
        ],
    },
    entry_points={
        "console_scripts": [
            "kg-extract=scripts.run_extraction:main",
            "kg-evaluate=scripts.run_evaluation:main",
            "kg-cluster=scripts.run_clustering:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
