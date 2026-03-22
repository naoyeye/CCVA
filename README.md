# CCVA

Clip-and-Convert-Video-to-Audio

A small **Python 3** utility that can download a video from YouTube, Bilibili (bilibili.com), or any site supported by yt-dlp, cut out a specific segment and convert it into an audio file (MP3 / WAV / AIFF).

## Features

* Downloads the best available audio/video stream with [yt-dlp](https://github.com/yt-dlp/yt-dlp).
* Uses **FFmpeg** under the hood – no quality loss when cutting.
* Supports flexible time formats (`SS`, `MM:SS`, `HH:MM:SS[.ms]`).
* Supports batch processing multiple video URLs.
* Supports multiple output formats: audio formats (MP3, WAV, AIFF) and video format (MP4).
* Automatically builds a sensible output filename based on video title if you pass a directory.
* Automatically extracts cookies from browser to solve YouTube authentication issues.

## Requirements

1. **Python 3.7+**
2. **FFmpeg** installed and accessible from your `PATH`
3. Python package **yt-dlp** (installed automatically via `requirements.txt`)

On Ubuntu / Debian you can install the native FFmpeg package with:

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

## Installation

```bash
# Clone the repository (or download the code)
$ git clone https://github.com/yourname/CCVA.git
$ cd CCVA

# Install Python dependencies
$ python -m pip install -r requirements.txt
```

## Installation

### Method 1: Install as Global Command (Recommended)

Use the provided installation script to install CCVA as a global command-line tool:

**macOS / Linux:**
```bash
$ git clone https://github.com/yourname/CCVA.git
$ cd CCVA
$ ./install.sh
```

**Windows:**
```cmd
> git clone https://github.com/yourname/CCVA.git
> cd CCVA
> install.bat
```

**Manual Installation:**
```bash
$ cd CCVA
$ pip install -e .
```

After installation, you can use the `CCVA` command from any directory!

### Method 2: Local Run

If you don't want to install as a global tool, you can run directly:

```bash
$ git clone https://github.com/yourname/CCVA.git
$ cd CCVA
$ python -m pip install -r requirements.txt
$ python index.py --url <video_url>
```

## Usage

### Global Command Usage (Recommended)

After installation, you can use the `CCVA` command from any directory:

```bash
# Basic usage (download entire video and convert to MP3)
CCVA --url <video_url>

# Specify format and output path
CCVA --url <video_url> --format <format> --output <output_path>

# Specify start and end time (clip segment)
CCVA --url <video_url> --start <start_time> --end <end_time> --format <format> --output <output_path>

# Batch process multiple videos
CCVA --list "[url1, url2, url3]" --format <format> --output <output_path>

# View help
CCVA --help
```

### Local Run

If you choose to run locally:

```bash
python index.py --url <video_url> --format <format> --output <output_path>
# Or specify start and end time:
python index.py --url <video_url> --start <start_time> --end <end_time> --format <format> --output <output_path>
```

Arguments:

| Name          | Description                                                                                   | Example                         |
| ------------- | --------------------------------------------------------------------------------------------- | -------------------------------- |
| `--url` / `-u` | Full video link (YouTube, Bilibili, or any format accepted by yt-dlp) | `https://youtu.be/dQw4w9WgXcQ` / `https://www.bilibili.com/video/BV1xxxxxxx` |
| `--list` / `-l` | [Optional] Batch process multiple video URLs, format: `[url1, url2, url3, ...]` | `[https://youtu.be/xxx, https://youtu.be/yyy]` |
| `--start` / `-s`  | [Optional] Clip **start** time. Accepts `SS`, `MM:SS`, `HH:MM:SS` or `HH:MM:SS.mmm`. Default: `00:00:00` (video start) | `90` / `01:30` / `00:01:30.500` / *leave blank for start* |
| `--end` / `-e`    | [Optional] Clip **end** time (must be greater than `start_time`). Default: video end | `120` / `02:00` / *leave blank for end* |
| `--format` / `-f`      | [Optional] Output format. One of: `mp3`, `wav`, `aiff`, `mp4`. Default: `mp3`. Note: `mp4` is video format, others are audio formats                                             | `mp3` / `mp4`                           |
| `--output` / `-o` | [Optional] Destination **directory** _or_ full file path for the resulting audio/video. If directory, script will auto-generate filename based on video title. Default: system Downloads directory. | `/home/user/Music/`             |
| `--cookies-from-browser` | [Optional] Extract cookies from specified browser to solve YouTube authentication issues. Default: `chrome` | `chrome`, `firefox`, `safari`, `edge` |

**Notes:**
- Either `--url` or `--list` must be provided
- If you pass a directory, the script will create a filename based on video title: `<video_title>.<ext>`
- If output path is a file path, script will use that path but update filename based on video title
- For `mp4` format, if no time range is specified, the entire video will be copied directly (no clipping)

Examples:

```bash
# Download single video and convert to MP3
CCVA --url https://youtu.be/dQw4w9WgXcQ --format mp3 --output ~/Music/

# Clip video segment and convert to MP3
CCVA --url https://youtu.be/dQw4w9WgXcQ --start 01:23 --end 01:53 --format mp3 --output ~/Music/

# Download video and convert to MP4 (video format)
CCVA --url https://youtu.be/dQw4w9WgXcQ --format mp4 --output ~/Videos/

# Batch process multiple videos
CCVA --list "[https://youtu.be/xxx, https://youtu.be/yyy]" --format mp3 --output ~/Music/

# Use Firefox browser cookies (solve authentication issues)
CCVA --url https://youtu.be/dQw4w9WgXcQ --cookies-from-browser firefox
```

* If `start_time` and `end_time` are not specified, the entire audio/video will be exported by default.

## Podcast Download Feature

CCVA also includes a powerful podcast download feature:

### Search and Download Podcasts

```bash
# Search podcasts
CCVA-Podcast --search "podcast name" --list

# Download podcast (using RSS Feed)
CCVA-Podcast --rss "https://example.com/feed.xml" --episode 0

# Download Apple Podcasts (paid content will be prompted)
CCVA-Podcast --url "https://podcasts.apple.com/ua/podcast/xxx"

# Download any podcast URL
CCVA-Podcast --url "https://example.com/podcast.mp3"
```

### Podcast Download Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--search` / `-s` | Search podcast by name | `--search "podcast name"` |
| `--rss` / `-r` | Directly provide RSS Feed URL | `--rss "https://example.com/feed.xml"` |
| `--url` / `-u` | Apple Podcasts URL or any podcast URL | `--url "https://podcasts.apple.com/xxx"` |
| `--episode` / `-e` | Select episode number (0-indexed) | `--episode 0` |
| `--format` / `-f` | Output audio format | `--format mp3` |
| `--output` / `-o` | Output file path | `--output ~/Music/` |
| `--list` / `-l` | List available podcasts or episodes | `--list` |

## Troubleshooting

### YouTube Authentication Issues

If you encounter "Sign in to confirm you're not a bot" error, CCVA will automatically extract cookies from your browser to solve this. Default is Chrome browser, you can also specify other browsers:

```bash
# Use Firefox
CCVA --url <video_url> --cookies-from-browser firefox

# Use Safari
CCVA --url <video_url> --cookies-from-browser safari

# Use Edge
CCVA --url <video_url> --cookies-from-browser edge
```

### Podcast Download Issues

* **Apple Podcasts Paid Content**: Paid podcasts cannot be downloaded directly, suggest subscribing through official channels
* **Invalid RSS Feed**: Check if RSS Feed URL is correct
* **Network Connection Issues**: Ensure network connection is normal

### Other Common Issues

* **FFmpeg Not Found**: Ensure FFmpeg is installed and in system PATH
* **Network Connection Issues**: CCVA will automatically retry downloads, if still fails please check network connection
* **Permission Issues**: Ensure write permissions for output directory

## Tips

* You can pass any URL supported by yt-dlp (YouTube, Bilibili, playlists, etc.).
* Ensure you respect the terms of service and local copyright laws when downloading content.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
