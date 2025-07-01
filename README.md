# clip-youtube-video-to-audio

A small **Python 3** utility that can download a YouTube video, cut out a specific segment and convert it into an audio file (MP3 / WAV / AIFF).

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
$ git clone https://github.com/yourname/clip-youtube-video-to-audio.git
$ cd clip-youtube-video-to-audio

# Install Python dependencies
$ python -m pip install -r requirements.txt
```

## Usage

```bash
python index.py <youtube_url> <start_time> <end_time> <format> <output_path>
```

Arguments:

| Name          | Description                                                                                   | Example                         |
| ------------- | --------------------------------------------------------------------------------------------- | -------------------------------- |
| `youtube_url` | Full YouTube video link (any format accepted by yt-dlp)                                       | `https://youtu.be/dQw4w9WgXcQ`  |
| `start_time`  | Clip **start** time. Accepts `SS`, `MM:SS`, `HH:MM:SS` or `HH:MM:SS.mmm`                      | `90` / `01:30` / `00:01:30.500` |
| `end_time`    | Clip **end** time (must be greater than `start_time`)                                         | `120` / `02:00`                 |
| `format`      | Output audio format. One of: `mp3`, `wav`, `aiff`                                             | `mp3`                           |
| `output_path` | Destination **directory** _or_ full file path for the resulting audio. Directories are safer. | `/home/user/Music/`             |

If you pass a directory, the script will create a filename like:

```
<video_id>_<start>-<end>.<ext>
```

Times are expressed in seconds (without decimals) for the filename. For example:

```bash
python index.py \
  "https://youtu.be/dQw4w9WgXcQ" \
  00:01:23 \
  00:01:53 \
  mp3 \
  ~/Music/
```

The above command downloads the video, extracts the segment from 1 min 23 s to 1 min 53 s, converts it to MP3, and saves it to `~/Music/dQw4w9WgXcQ_83-113.mp3`.

## Tips

* Large videos may take some time to download; you can pass any URL supported by yt-dlp (YouTube Shorts, playlists, etc.).
* Ensure you respect YouTube's terms of service and local copyright laws when downloading content.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
