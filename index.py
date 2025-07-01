# 写一个 python 脚本,用来从youtube视频中剪辑指定的一段内容,然后转成音频格式。

# 这个脚本接收的参数：

# 1. youtube 的视频链接地址
# 2. 要剪辑的内容的开始时间和结束时间
# 3. 要转换成的音频格式，mp3、wav、aiff
# 4. 最终转成的音频的存储位置（指定本地电脑的某个目录）

"""
写一个 python 脚本，用来从youtube视频中剪辑指定的一段内容，然后转成音频格式。

脚本接收的参数：

1. youtube 的视频链接地址
2. 要剪辑的内容的开始时间和结束时间
3. 要转换成的音频格式，mp3、wav、aiff
4. 最终转成的音频的存储位置（指定本地电脑的某个目录）
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple

try:
    import yt_dlp  # type: ignore
except ImportError:
    sys.stderr.write("Error: The 'yt-dlp' package is required. Install it with 'pip install yt-dlp'.\n")
    sys.exit(1)


ALLOWED_FORMATS = {"mp3", "wav", "aiff"}


def parse_time(timestr: str) -> float:
    """Convert a HH:MM:SS[.mmm] or MM:SS or SS string into seconds (float)."""
    parts = timestr.strip().split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"Invalid time format: '{timestr}'")

    try:
        parts = [float(p) for p in parts]
    except ValueError as e:
        raise ValueError(f"Invalid numeric value in time '{timestr}': {e}") from e

    if len(parts) == 1:  # SS
        seconds = parts[0]
    elif len(parts) == 2:  # MM:SS
        minutes, seconds = parts
        seconds = minutes * 60 + seconds
    else:  # HH:MM:SS
        hours, minutes, seconds = parts
        seconds = hours * 3600 + minutes * 60 + seconds
    return seconds


def derive_output_path(output: str, video_id: str, start: float, end: float, ext: str) -> Path:
    """Return a Path object for the final audio file."""
    output_path = Path(output).expanduser().resolve()

    # If the user supplied a directory, construct a filename inside that directory
    if output_path.is_dir() or not output_path.suffix:
        start_tag = str(int(start)).replace(".", "_")
        end_tag = str(int(end)).replace(".", "_")
        safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", video_id)
        filename = f"{safe_id}_{start_tag}-{end_tag}.{ext}"
        output_path = output_path / filename

    # Ensure parent dir exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def download_video(url: str, tmp_dir: Path) -> Tuple[str, str]:
    """Download the best audio/video stream using yt_dlp and return (file_path, video_id)."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(tmp_dir / "%(_id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id") or "video"
        downloaded_file = ydl.prepare_filename(info)
    if not os.path.exists(downloaded_file):
        raise RuntimeError("yt-dlp failed to download the requested video.")
    return downloaded_file, video_id


def run_ffmpeg(input_file: str, start: float, duration: float, output_file: Path, fmt: str):
    """Invoke ffmpeg to cut the segment and convert to the requested format."""

    if fmt == "mp3":
        codec = "libmp3lame"
        extra = ["-b:a", "192k"]
    elif fmt == "wav":
        codec = "pcm_s16le"
        extra = ["-ac", "2", "-ar", "44100"]
    elif fmt == "aiff":
        codec = "pcm_s16be"
        extra = ["-ac", "2", "-ar", "44100"]
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    cmd = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-y",  # overwrite without asking
        "-ss",
        str(start),
        "-t",
        str(duration),
        "-i",
        input_file,
        "-vn",  # no video
        "-acodec",
        codec,
        *extra,
        str(output_file),
    ]

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        sys.stderr.write("Error: ffmpeg executable not found. Please install ffmpeg and ensure it is in your PATH.\n")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"ffmpeg failed with exit code {e.returncode}.\n")
        sys.exit(e.returncode)



def main():
    parser = argparse.ArgumentParser(
        description="Clip a segment from a YouTube video and convert it to the desired audio format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("start", help="Clip start time (HH:MM:SS or MM:SS or SS[.ms])")
    parser.add_argument("end", help="Clip end time (HH:MM:SS or MM:SS or SS[.ms])")
    parser.add_argument("format", choices=sorted(ALLOWED_FORMATS), help="Output audio format")
    parser.add_argument(
        "output",
        help="Path to the output directory or full file path where the audio will be stored.",
    )

    args = parser.parse_args()

    # Validate and parse times
    try:
        start_sec = parse_time(args.start)
        end_sec = parse_time(args.end)
    except ValueError as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)

    if end_sec <= start_sec:
        sys.stderr.write("Error: end time must be greater than start time.\n")
        sys.exit(1)

    duration = end_sec - start_sec

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)

        # Step 1: Download video/audio
        print("Downloading video…", file=sys.stderr)
        source_file, video_id = download_video(args.url, tmp_dir)

        # Step 2: Derive output path
        output_path = derive_output_path(args.output, video_id, start_sec, end_sec, args.format)

        # Step 3: Cut and convert using ffmpeg
        print("Processing with ffmpeg…", file=sys.stderr)
        run_ffmpeg(source_file, start_sec, duration, output_path, args.format)

        print(f"\nDone! Audio saved to: {output_path}")


if __name__ == "__main__":
    main()