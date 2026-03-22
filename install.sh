#!/bin/bash

# CCVA 安装脚本
# 此脚本将 CCVA 安装为全局命令行工具

set -e  # 遇到错误时退出

echo "🚀 开始安装 CCVA..."

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3。请先安装 Python 3.8 或更高版本。"
    exit 1
fi

# 检查 pip 是否安装
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到 pip3。请先安装 pip。"
    exit 1
fi

# 检查 ffmpeg 是否安装
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  警告: 未找到 ffmpeg。CCVA 需要 ffmpeg 来处理音频。"
    echo "请安装 ffmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  Windows: 从 https://ffmpeg.org/download.html 下载"
    echo ""
    read -p "是否继续安装 CCVA？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安装已取消。"
        exit 1
    fi
fi

# 进入脚本所在目录
cd "$(dirname "$0")"

# 安装 CCVA
echo "📦 正在安装 CCVA..."
# 尝试使用官方 PyPI 源，如果失败则使用默认源
pip3 install -e . --index-url https://pypi.org/simple/ || pip3 install -e .

if [ $? -eq 0 ]; then
    echo "✅ CCVA 安装成功！"
    echo ""
    echo "现在你可以在任意目录下使用以下命令："
    echo "  CCVA --url <视频链接>"
    echo "  CCVA --url <视频链接> --start <开始时间> --end <结束时间>"
    echo "  CCVA --url <视频链接> --format mp3 --output <输出路径>"
    echo ""
    echo "使用 'CCVA --help' 查看所有可用选项。"
else
    echo "❌ 安装失败。请检查错误信息并重试。"
    exit 1
fi
