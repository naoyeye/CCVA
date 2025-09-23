# CCVA 安装指南

## 快速开始

### 1. 安装为全局命令行工具

**macOS / Linux:**
```bash
git clone https://github.com/your-username/CCVA.git
cd CCVA
./install.sh
```

**Windows:**
```cmd
git clone https://github.com/your-username/CCVA.git
cd CCVA
install.bat
```

**手动安装:**
```bash
cd CCVA
pip install -e .
```

### 2. 验证安装

安装完成后，在任意目录下运行：
```bash
CCVA --help
```

如果看到帮助信息，说明安装成功！

### 3. 开始使用

```bash
# 基本用法
CCVA --url https://youtu.be/dQw4w9WgXcQ

# 指定时间范围
CCVA --url https://youtu.be/dQw4w9WgXcQ --start 01:23 --end 01:53

# 指定输出格式和路径
CCVA --url https://youtu.be/dQw4w9WgXcQ --format mp3 --output ~/Music/
```

## 卸载

**macOS / Linux:**
```bash
./uninstall.sh
```

**Windows:**
```cmd
uninstall.bat
```

**手动卸载:**
```bash
pip uninstall ccva
```

## 系统要求

- Python 3.8+
- FFmpeg（必须安装在系统 PATH 中）
- pip

## 故障排除

### 问题：命令未找到
**解决方案：** 确保 Python 的 Scripts 目录在系统 PATH 中。

### 问题：FFmpeg 未找到
**解决方案：** 安装 FFmpeg 并确保在 PATH 中：
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`
- Windows: 从 https://ffmpeg.org/download.html 下载

### 问题：权限错误
**解决方案：** 在 macOS/Linux 上，确保安装脚本有执行权限：
```bash
chmod +x install.sh
```
