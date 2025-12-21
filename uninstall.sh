#!/bin/bash

# CCVA 卸载脚本

echo "🗑️  开始卸载 CCVA..."

# 检查是否已安装
if ! command -v CCVA &> /dev/null; then
    echo "⚠️  CCVA 似乎未安装或不在 PATH 中。"
    read -p "是否继续卸载？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "卸载已取消。"
        exit 0
    fi
fi

# 卸载 CCVA
echo "📦 正在卸载 CCVA..."
pip3 uninstall ccva -y

if [ $? -eq 0 ]; then
    echo "✅ CCVA 卸载成功！"
else
    echo "❌ 卸载失败。请检查错误信息。"
    exit 1
fi
