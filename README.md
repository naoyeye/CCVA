# CCVA

Clip-and-Convert-Video-to-Audio

A small **Python 3** utility that can download a video from YouTube, Bilibili (bilibili.com), or any site supported by yt-dlp, cut out a specific segment and convert it into an audio file (MP3 / WAV / AIFF).

## Features

* Downloads the best available audio stream with [yt-dlp](https://github.com/yt-dlp/yt-dlp).
* Uses **FFmpeg** under the hood – no quality loss when cutting.
* Supports flexible time formats (`SS`, `MM:SS`, `HH:MM:SS[.ms]`).
* Automatically builds a sensible output filename if you pass a directory.

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

## Usage

```bash
python index.py --url <video_url> --format <format> --output <output_path>
# Or specify start and end time:
python index.py --url <video_url> --start <start_time> --end <end_time> --format <format> --output <output_path>
```

Arguments:

| Name          | Description                                                                                   | Example                         |
| ------------- | --------------------------------------------------------------------------------------------- | -------------------------------- |
| `--url` / `-u` | Full video link (YouTube, Bilibili, or any format accepted by yt-dlp) | `https://youtu.be/dQw4w9WgXcQ` / `https://www.bilibili.com/video/BV1xxxxxxx` |
| `--start` / `-s`  | [Optional] Clip **start** time. Accepts `SS`, `MM:SS`, `HH:MM:SS` or `HH:MM:SS.mmm`. Default: `00:00:00` (video start) | `90` / `01:30` / `00:01:30.500` / *leave blank for start* |
| `--end` / `-e`    | [Optional] Clip **end** time (must be greater than `start_time`). Default: video end | `120` / `02:00` / *leave blank for end* |
| `--format` / `-f`      | [Optional] Output audio format. One of: `mp3`, `wav`, `aiff`. Default: `mp3`                                             | `mp3`                           |
| `--output` / `-o` | [Optional] Destination **directory** _or_ full file path for the resulting audio. Directories are safer. Default: system Downloads directory. | `/home/user/Music/`             |

If you pass a directory, the script will create a filename like:

```
<video_id>_<start>-<end>.<ext>
```

Times are expressed in seconds (without decimals) for the filename. For example:

```bash
python index.py --url https://youtu.be/dQw4w9WgXcQ --start 01:23 --end 01:53 --format mp3 --output ~/Music/
```

The above command downloads the video, extracts the segment from 1 min 23 s to 1 min 53 s, converts it to MP3, and saves it to `~/Music/dQw4w9WgXcQ_83-113.mp3`.

* If `start_time` and `end_time` are not specified, the entire audio will be exported by default.

## Tips

* You can pass any URL supported by yt-dlp (YouTube, Bilibili, playlists, etc.).
* Ensure you respect the terms of service and local copyright laws when downloading content.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
