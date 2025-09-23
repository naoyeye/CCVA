#!/usr/bin/env python3
"""
CCVA (Command-line Clip Video Audio) 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README_zh.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "CCVA - 命令行视频音频剪辑工具"

# 读取 requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return ["yt-dlp>=2024.3.10"]

setup(
    name="ccva",
    version="1.0.0",
    author="CCVA Team",
    author_email="",
    description="命令行视频音频剪辑工具 - 从 YouTube、Bilibili 等网站下载并剪辑视频音频",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/CCVA",  # 替换为你的实际仓库地址
    py_modules=["index", "podcast_helper"],
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "CCVA=index:cli",
            "CCVA-Podcast=podcast_helper:main",
        ],
    },
    keywords="video audio clip youtube bilibili ffmpeg yt-dlp",
    project_urls={
        "Bug Reports": "https://github.com/your-username/CCVA/issues",  # 替换为你的实际仓库地址
        "Source": "https://github.com/your-username/CCVA",  # 替换为你的实际仓库地址
    },
)
