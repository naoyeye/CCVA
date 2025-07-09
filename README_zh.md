# CCVA

一个基于 **Python 3** 的小工具，用于下载 YouTube、Bilibili（哔哩哔哩）等网站的视频，剪辑指定时段，并转换为音频文件（支持 MP3 / WAV / AIFF）。

## 功能特点

* 借助 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 下载最佳音频流；
* 基于 **FFmpeg** 进行剪辑与转码，音质无损；
* 支持灵活的时间格式（`SS`、`MM:SS`、`HH:MM:SS[.ms]`）；
* 如果输出路径为目录，则自动生成易读的文件名。

## 环境依赖

1. **Python 3.7+**；
2. 系统已安装 **FFmpeg** 且可通过 `PATH` 调用；
3. Python 包 **yt-dlp**（通过 `requirements.txt` 自动安装）。

在 Ubuntu / Debian 系统上，可通过以下命令安装 FFmpeg：

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

## 安装

```bash
# 克隆仓库（或直接下载代码）
$ git clone https://github.com/yourname/CCVA.git
$ cd CCVA

# 安装 Python 依赖
$ python -m pip install -r requirements.txt
```

## 使用方法

```bash
python index.py --url <video_url> --format <format> --output <output_path>
# 或指定开始和结束时间：
python index.py --url <video_url> --start <start_time> --end <end_time> --format <format> --output <output_path>
```

参数说明：

| 名称            | 描述                                                                                       | 示例                               |
| --------------- | ------------------------------------------------------------------------------------------ | ---------------------------------- |
| `--url` / `-u`   | 视频链接（YouTube、Bilibili 或 yt-dlp 支持的任意格式） | `https://youtu.be/dQw4w9WgXcQ` / `https://www.bilibili.com/video/BV1xxxxxxx` |
| `--start` / `-s`    | [可选] 剪辑 **开始** 时间，支持 `SS`、`MM:SS`、`HH:MM:SS` 或 `HH:MM:SS.mmm` 格式，默认 `00:00:00`（视频开头） | `90` / `01:30` / `00:01:30.500` / *留空则为开头* |
| `--end` / `-e`      | [可选] 剪辑 **结束** 时间（需大于 `start_time`），默认视频结尾 | `120` / `02:00` / *留空则为结尾* |
| `--format` / `-f`        | [可选] 输出音频格式，可选：`mp3`、`wav`、`aiff`，默认 `mp3`                                                    | `mp3`                              |
| `--output` / `-o`   | [可选] 输出 **目录** 或完整文件路径。若为目录，脚本会自动生成文件名，默认系统下载目录                                  | `/home/user/Music/`                |

当 `output_path` 为目录时，脚本会生成如下文件名：

```
<video_id>_<start>-<end>.<ext>
```

其中 `<start>` 与 `<end>` 取秒数的整数部分。例如：

```bash
python index.py --url https://youtu.be/dQw4w9WgXcQ --start 01:23 --end 01:53 --format mp3 --output ~/Music/
```

上述命令会下载该视频，截取 1 分 23 秒到 1 分 53 秒的片段，转为 MP3，并保存为 `~/Music/dQw4w9WgXcQ_83-113.mp3`。

* 如未指定 `start_time` 和 `end_time`，则自动导出全段音频。

## 小贴士

* 大文件下载时间较长，yt-dlp 支持的视频地址包括短视频、播放列表等；
* 使用本工具请遵守各视频网站服务条款以及当地版权法规。

## 许可证

本项目基于 MIT License 开源，详见 [LICENSE](LICENSE)。