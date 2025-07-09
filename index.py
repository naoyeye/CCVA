import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple
import platform

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
        description="Clip a segment from a YouTube or Bilibili video (or any site supported by yt-dlp) and convert it to the desired audio format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--url", "-u", required=True, help="Video URL (YouTube, Bilibili, or any site supported by yt-dlp)")
    parser.add_argument("--start", "-s", default=None, help="Clip start time (HH:MM:SS or MM:SS or SS[.ms]), default: 00:00:00")
    parser.add_argument("--end", "-e", default=None, help="Clip end time (HH:MM:SS or MM:SS or SS[.ms]), default: video end")
    parser.add_argument("--format", "-f", default="mp3", choices=sorted(ALLOWED_FORMATS), help="Output audio format, default: mp3")
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to the output directory or full file path where the audio will be stored. Default: system Downloads directory.",
    )

    args = parser.parse_args()

    # 处理 output 默认值
    if args.output is not None:
        output_path_arg = args.output
    else:
        home = str(Path.home())
        sys_name = platform.system()
        if sys_name == "Windows":
            downloads = os.path.join(home, "Downloads")
        elif sys_name == "Darwin":
            downloads = os.path.join(home, "Downloads")
        else:
            # Linux: 兼容部分中文系统
            downloads = os.path.join(home, "Downloads")
            if not os.path.exists(downloads):
                downloads = os.path.join(home, "下载")
        output_path_arg = downloads

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)

        # Step 1: Download video/audio and get info
        print("Downloading video…", file=sys.stderr)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(tmp_dir / "%(_id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(args.url, download=True)
            video_id = info.get("id") or "video"
            downloaded_file = ydl.prepare_filename(info)
            duration_total = info.get("duration")
        if not os.path.exists(downloaded_file):
            raise RuntimeError("yt-dlp failed to download the requested video.")

        # Step 2: 处理 start/end 默认值
        try:
            start_sec = parse_time(args.start) if args.start is not None else 0.0
            if args.end is not None:
                end_sec = parse_time(args.end)
            else:
                if duration_total is None:
                    sys.stderr.write("Error: Could not determine video duration. Please specify end time.\n")
                    sys.exit(1)
                end_sec = float(duration_total)
        except ValueError as e:
            sys.stderr.write(str(e) + "\n")
            sys.exit(1)

        if end_sec <= start_sec:
            sys.stderr.write("Error: end time must be greater than start time.\n")
            sys.exit(1)

        duration = end_sec - start_sec

        # Step 3: Derive output path
        output_path = derive_output_path(output_path_arg, video_id, start_sec, end_sec, args.format)

        # Step 4: Cut and convert using ffmpeg
        print("Processing with ffmpeg…", file=sys.stderr)
        run_ffmpeg(downloaded_file, start_sec, duration, output_path, args.format)

        print(f"\nDone! Audio saved to: {output_path}")


if __name__ == "__main__":
    main()