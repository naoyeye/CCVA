# CCVA

一个基于 **Python 3** 的小工具，用于下载 YouTube、Bilibili（哔哩哔哩）等网站的视频，剪辑指定时段，并转换为音频文件（支持 MP3 / WAV / AIFF）。

## 功能特点

* 借助 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 下载最佳音频/视频流；
* 基于 **FFmpeg** 进行剪辑与转码，音质无损；
* 支持灵活的时间格式（`SS`、`MM:SS`、`HH:MM:SS[.ms]`）；
* 支持批量处理多个视频 URL；
* 支持多种输出格式：音频格式（MP3、WAV、AIFF）和视频格式（MP4）；
* 如果输出路径为目录，则自动基于视频标题生成易读的文件名；
* 自动从浏览器提取 cookies，解决 YouTube 身份验证问题。

## 环境依赖

1. **Python 3.7+**；
2. 系统已安装 **FFmpeg** 且可通过 `PATH` 调用；
3. Python 包 **yt-dlp**（通过 `requirements.txt` 自动安装）。

在 Ubuntu / Debian 系统上，可通过以下命令安装 FFmpeg：

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

## 安装

### 方法一：安装为全局命令行工具（推荐）

使用提供的安装脚本，将 CCVA 安装为全局命令行工具，这样你就可以在任意目录下使用 `CCVA` 命令：

**macOS / Linux:**
```bash
# 克隆仓库（或直接下载代码）
$ git clone https://github.com/yourname/CCVA.git
$ cd CCVA

# 运行安装脚本
$ ./install.sh
```

**Windows:**
```cmd
# 克隆仓库（或直接下载代码）
> git clone https://github.com/yourname/CCVA.git
> cd CCVA

# 运行安装脚本
> install.bat
```

**手动安装:**
```bash
# 进入项目目录
$ cd CCVA

# 安装为全局工具
$ pip install -e .
```

安装完成后，你就可以在任意目录下使用 `CCVA` 命令了！

### 方法二：本地运行

如果你不想安装为全局工具，也可以直接运行：

```bash
# 克隆仓库（或直接下载代码）
$ git clone https://github.com/yourname/CCVA.git
$ cd CCVA

# 安装 Python 依赖
$ python -m pip install -r requirements.txt

# 直接运行
$ python index.py --url <video_url>
```

## 使用方法

### 全局命令使用（推荐）

安装完成后，你可以在任意目录下使用 `CCVA` 命令：

```bash
# 基本用法（下载整个视频并转换为 MP3）
CCVA --url <video_url>

# 指定格式和输出路径
CCVA --url <video_url> --format <format> --output <output_path>

# 指定开始和结束时间（剪辑片段）
CCVA --url <video_url> --start <start_time> --end <end_time> --format <format> --output <output_path>

# 批量处理多个视频
CCVA --list "[url1, url2, url3]" --format <format> --output <output_path>

# 查看帮助
CCVA --help
```

### 本地运行

如果你选择本地运行方式：

```bash
python index.py --url <video_url> --format <format> --output <output_path>
# 或指定开始和结束时间：
python index.py --url <video_url> --start <start_time> --end <end_time> --format <format> --output <output_path>
```

参数说明：

| 名称            | 描述                                                                                       | 示例                               |
| --------------- | ------------------------------------------------------------------------------------------ | ---------------------------------- |
| `--url` / `-u`   | 视频链接（YouTube、Bilibili 或 yt-dlp 支持的任意格式） | `https://youtu.be/dQw4w9WgXcQ` / `https://www.bilibili.com/video/BV1xxxxxxx` |
| `--list` / `-l`  | [可选] 批量处理多个视频 URL，格式：`[url1, url2, url3, ...]` | `[https://youtu.be/xxx, https://youtu.be/yyy]` |
| `--start` / `-s`    | [可选] 剪辑 **开始** 时间，支持 `SS`、`MM:SS`、`HH:MM:SS` 或 `HH:MM:SS.mmm` 格式，默认 `00:00:00`（视频开头） | `90` / `01:30` / `00:01:30.500` / *留空则为开头* |
| `--end` / `-e`      | [可选] 剪辑 **结束** 时间（需大于 `start_time`），默认视频结尾 | `120` / `02:00` / *留空则为结尾* |
| `--format` / `-f`        | [可选] 输出格式，可选：`mp3`、`wav`、`aiff`、`mp4`，默认 `mp3`。注意：`mp4` 为视频格式，其他为音频格式                                                    | `mp3` / `mp4`                              |
| `--output` / `-o`   | [可选] 输出 **目录** 或完整文件路径。若为目录，脚本会自动生成基于视频标题的文件名，默认系统下载目录                                  | `/home/user/Music/`                |
| `--cookies-from-browser` | [可选] 从指定浏览器提取 cookies 以解决 YouTube 身份验证问题，默认 `chrome` | `chrome`, `firefox`, `safari`, `edge` |

**注意：**
- `--url` 和 `--list` 参数必须至少提供一个
- 当 `output_path` 为目录时，脚本会基于视频标题自动生成文件名，格式为：`<视频标题>.<扩展名>`
- 如果输出路径是文件路径，脚本会使用该路径但会根据视频标题更新文件名
- 对于 `mp4` 格式，如果没有指定时间范围，会直接复制整个视频文件（不进行剪辑）

使用示例：

```bash
# 下载单个视频并转换为 MP3
CCVA --url https://youtu.be/dQw4w9WgXcQ --format mp3 --output ~/Music/

# 剪辑视频片段并转换为 MP3
CCVA --url https://youtu.be/dQw4w9WgXcQ --start 01:23 --end 01:53 --format mp3 --output ~/Music/

# 下载视频并转换为 MP4（视频格式）
CCVA --url https://youtu.be/dQw4w9WgXcQ --format mp4 --output ~/Videos/

# 批量处理多个视频
CCVA --list "[https://youtu.be/xxx, https://youtu.be/yyy]" --format mp3 --output ~/Music/

# 使用 Firefox 浏览器的 cookies（解决身份验证问题）
CCVA --url https://youtu.be/dQw4w9WgXcQ --cookies-from-browser firefox
```

* 如未指定 `start_time` 和 `end_time`，则自动导出全段音频/视频。

## 播客下载功能

CCVA 还包含强大的播客下载功能：

### 搜索和下载播客

```bash
# 搜索播客
CCVA-Podcast --search "忽左忽右" --list

# 下载播客（使用 RSS Feed）
CCVA-Podcast --rss "https://justpodmedia.com/rss/left-right.xml" --episode 0

# 下载 Apple Podcasts（付费内容会提示）
CCVA-Podcast --url "https://podcasts.apple.com/ua/podcast/xxx"

# 下载任何播客 URL
CCVA-Podcast --url "https://example.com/podcast.mp3"
```

### 播客下载参数

| 参数 | 描述 | 示例 |
|------|------|------|
| `--search` / `-s` | 搜索播客名称 | `--search "忽左忽右"` |
| `--rss` / `-r` | 直接提供 RSS Feed URL | `--rss "https://example.com/feed.xml"` |
| `--url` / `-u` | Apple Podcasts URL 或任何播客 URL | `--url "https://podcasts.apple.com/xxx"` |
| `--episode` / `-e` | 选择第几集（从0开始） | `--episode 0` |
| `--format` / `-f` | 输出音频格式 | `--format mp3` |
| `--output` / `-o` | 输出文件路径 | `--output ~/Music/` |
| `--list` / `-l` | 列出可用的播客或集数 | `--list` |

## 故障排除

### YouTube 身份验证问题

如果遇到 "Sign in to confirm you're not a bot" 错误，CCVA 会自动从你的浏览器提取 cookies 来解决这个问题。默认使用 Chrome 浏览器，你也可以指定其他浏览器：

```bash
# 使用 Firefox
CCVA --url <video_url> --cookies-from-browser firefox

# 使用 Safari
CCVA --url <video_url> --cookies-from-browser safari

# 使用 Edge
CCVA --url <video_url> --cookies-from-browser edge
```

### 播客下载问题

* **Apple Podcasts 付费内容**：付费播客无法直接下载，建议通过官方渠道订阅
* **RSS Feed 无效**：检查 RSS Feed URL 是否正确
* **网络连接问题**：确保网络连接正常

### 其他常见问题

* **FFmpeg 未找到**：确保 FFmpeg 已安装并在系统 PATH 中
* **网络连接问题**：CCVA 会自动重试下载，如果仍然失败请检查网络连接
* **权限问题**：确保对输出目录有写入权限

## 小贴士

* 大文件下载时间较长，yt-dlp 支持的视频地址包括短视频、播放列表等；
* 使用本工具请遵守各视频网站服务条款以及当地版权法规。

## 许可证

本项目基于 MIT License 开源，详见 [LICENSE](LICENSE)。