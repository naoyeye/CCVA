# YouTube 视频音频剪辑工具

一个用于从 YouTube 视频中剪辑指定片段并转换为音频格式的 Python 脚本。

## 功能特性

- 从 YouTube 视频下载音频
- 精确剪辑指定时间段的内容
- 支持多种音频格式输出（MP3、WAV、AIFF）
- 自动生成文件名或支持自定义输出路径
- 支持多种时间格式输入

## 系统要求

- Python 3.6+
- FFmpeg（必须安装并添加到系统 PATH）
- 网络连接

## 安装

1. 克隆或下载此项目
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

3. 安装 FFmpeg：
   - **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: 从 [FFmpeg 官网](https://ffmpeg.org/download.html) 下载并添加到 PATH

## 使用方法

### 基本语法

```bash
python index.py <YouTube_URL> <开始时间> <结束时间> <音频格式> <输出路径>
```

### 参数说明

1. **YouTube_URL**: YouTube 视频的完整链接
2. **开始时间**: 剪辑开始时间，支持格式：
   - `SS` - 秒数（如：30）
   - `MM:SS` - 分:秒（如：1:30）
   - `HH:MM:SS` - 时:分:秒（如：0:1:30）
   - 支持小数点（如：30.5）
3. **结束时间**: 剪辑结束时间，格式同开始时间
4. **音频格式**: 输出格式，可选：
   - `mp3` - MP3 格式（192k 比特率）
   - `wav` - WAV 格式（16位，44.1kHz，立体声）
   - `aiff` - AIFF 格式（16位，44.1kHz，立体声）
5. **输出路径**: 
   - 指定目录：脚本会自动生成文件名
   - 指定完整文件路径：使用指定的文件名

### 使用示例

#### 示例 1：剪辑并保存到指定目录
```bash
python index.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "1:30" "2:45" mp3 "./output/"
```
- 剪辑从 1分30秒 到 2分45秒 的片段
- 输出为 MP3 格式
- 保存到 `./output/` 目录，文件名自动生成

#### 示例 2：指定完整输出路径
```bash
python index.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "30" "90" wav "~/Music/my_clip.wav"
```
- 剪辑从 30秒 到 90秒 的片段
- 输出为 WAV 格式
- 保存为 `~/Music/my_clip.wav`

#### 示例 3：使用小数点时间
```bash
python index.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "1:30.5" "2:15.8" aiff "./clips/"
```
- 剪辑从 1分30.5秒 到 2分15.8秒 的片段
- 输出为 AIFF 格式
- 保存到 `./clips/` 目录

## 输出文件命名规则

当指定输出目录时，文件名格式为：
```
<视频ID>_<开始时间>-<结束时间>.<格式>
```

例如：`dQw4w9WgXcQ_90-135.mp3`

## 错误处理

脚本会自动处理以下情况：
- 无效的 YouTube URL
- 时间格式错误
- 结束时间早于开始时间
- 网络连接问题
- FFmpeg 未安装或配置错误

## 注意事项

1. 确保有稳定的网络连接用于下载视频
2. 剪辑较长的片段可能需要更多时间
3. 输出目录会自动创建（如果不存在）
4. 脚本会覆盖同名的输出文件
5. 临时文件会自动清理

## 故障排除

### FFmpeg 相关错误
如果遇到 "ffmpeg executable not found" 错误：
1. 确认 FFmpeg 已正确安装
2. 检查 FFmpeg 是否在系统 PATH 中
3. 尝试在终端中运行 `ffmpeg -version` 验证安装

### yt-dlp 相关错误
如果遇到下载问题：
1. 确认网络连接正常
2. 检查 YouTube URL 是否有效
3. 尝试更新 yt-dlp：`pip install --upgrade yt-dlp`

## 许可证

此项目仅供学习和个人使用。请遵守 YouTube 服务条款和相关版权法律。
