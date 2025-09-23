import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple, List
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


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除或替换不安全的字符"""
    # 移除或替换文件名中不允许的字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除多余的空格和点
    filename = re.sub(r'\s+', ' ', filename).strip()
    filename = filename.strip('.')
    # 限制文件名长度
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def derive_output_path(output: str, video_title: str, ext: str) -> Path:
    """根据视频标题生成输出文件路径"""
    output_path = Path(output).expanduser().resolve()
    
    # 清理视频标题
    safe_title = sanitize_filename(video_title)
    filename = f"{safe_title}.{ext}"
    
    # 如果用户提供的是目录，在目录中创建文件
    if output_path.is_dir() or not output_path.suffix:
        output_path = output_path / filename
    else:
        # 如果用户提供的是文件路径，使用该路径但更新扩展名
        output_path = output_path.with_suffix(f'.{ext}')
        # 如果文件名不是基于视频标题的，则更新为基于标题的
        if not any(char in str(output_path.stem) for char in ['_', '-']):
            output_path = output_path.parent / filename

    # 确保父目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def download_video(url: str, tmp_dir: Path) -> Tuple[str, str, str]:
    """下载视频并返回 (文件路径, 视频ID, 视频标题)"""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(tmp_dir / "%(_id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id") or "video"
        video_title = info.get("title") or "Unknown Title"
        downloaded_file = ydl.prepare_filename(info)
    if not os.path.exists(downloaded_file):
        raise RuntimeError("yt-dlp failed to download the requested video.")
    return downloaded_file, video_id, video_title


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


def get_video_title_with_ytdlp(url: str) -> str:
    """使用yt-dlp命令行获取视频标题"""
    try:
        result = subprocess.run([
            'yt-dlp', '--get-title', '--no-warnings', url
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            title = result.stdout.strip()
            if title and 'youtube video #' not in title.lower():
                return title
        return None
    except Exception as e:
        print(f"yt-dlp获取标题失败: {e}", file=sys.stderr)
        return None


def get_video_info(url: str, cookies_from_browser: str) -> dict:
    """获取视频信息而不下载"""
    # 首先尝试使用yt-dlp命令行获取标题
    title_from_cmd = get_video_title_with_ytdlp(url)
    
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "cookiesfrombrowser": (cookies_from_browser,),
        "extractor_retries": 3,
        "fragment_retries": 3,
        "retries": 3,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # 如果命令行获取到了更好的标题，使用它
        if title_from_cmd:
            info['title'] = title_from_cmd
        
        return info


def process_single_video(url: str, start: float, end: float, format_ext: str, output_dir: str, cookies_from_browser: str) -> Path:
    """处理单个视频的下载和转换"""
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)

        # Step 1: 先获取视频信息
        print(f"正在获取视频信息: {url}", file=sys.stderr)
        info = get_video_info(url, cookies_from_browser)
        video_title = info.get("title") or "Unknown Title"
        duration_total = info.get("duration")
        
        print(f"视频标题: {video_title}", file=sys.stderr)

        # Step 2: 处理 start/end 默认值
        try:
            start_sec = start
            if end is not None:
                end_sec = end
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

        # Step 3: 根据视频标题生成输出路径
        output_path = derive_output_path(output_dir, video_title, format_ext)

        # Step 4: 下载视频/音频
        print(f"正在下载视频: {url}", file=sys.stderr)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(tmp_dir / "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "cookiesfrombrowser": (cookies_from_browser,),
            "extractor_retries": 3,
            "fragment_retries": 3,
            "retries": 3,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            # 获取下载后的文件路径
            video_id = info.get("id") or "video"
            # 查找下载的文件
            downloaded_files = list(tmp_dir.glob(f"{video_id}.*"))
            if not downloaded_files:
                raise RuntimeError("yt-dlp failed to download the requested video.")
            downloaded_file = str(downloaded_files[0])

        # Step 5: Cut and convert using ffmpeg
        print(f"正在处理音频: {video_title}", file=sys.stderr)
        run_ffmpeg(downloaded_file, start_sec, duration, output_path, format_ext)

        return output_path


def parse_url_list(url_list_str: str) -> List[str]:
    """解析URL列表字符串"""
    # 移除方括号
    url_list_str = url_list_str.strip('[]')
    # 按逗号分割并清理每个URL
    urls = [url.strip() for url in url_list_str.split(',')]
    return [url for url in urls if url]  # 过滤空字符串


def main():
    parser = argparse.ArgumentParser(
        description="Clip a segment from a YouTube or Bilibili video (or any site supported by yt-dlp) and convert it to the desired audio format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--url", "-u", help="Video URL (YouTube, Bilibili, or any site supported by yt-dlp)")
    parser.add_argument("--list", "-l", help="List of video URLs in format [url1, url2, url3, ...]")
    parser.add_argument("--start", "-s", default=None, help="Clip start time (HH:MM:SS or MM:SS or SS[.ms]), default: 00:00:00")
    parser.add_argument("--end", "-e", default=None, help="Clip end time (HH:MM:SS or MM:SS or SS[.ms]), default: video end")
    parser.add_argument("--format", "-f", default="mp3", choices=sorted(ALLOWED_FORMATS), help="Output audio format, default: mp3")
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to the output directory or full file path where the audio will be stored. Default: system Downloads directory.",
    )
    parser.add_argument(
        "--cookies-from-browser", 
        default="chrome", 
        help="Browser to extract cookies from (chrome, firefox, safari, edge, etc.). Default: chrome"
    )

    args = parser.parse_args()

    # 检查是否提供了URL或列表
    if not args.url and not args.list:
        parser.error("必须提供 --url 或 --list 参数")

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

    # 处理时间参数
    try:
        start_sec = parse_time(args.start) if args.start is not None else 0.0
        end_sec = parse_time(args.end) if args.end is not None else None
    except ValueError as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)

    # 确定要处理的URL列表
    urls_to_process = []
    if args.url:
        urls_to_process.append(args.url)
    if args.list:
        urls_to_process.extend(parse_url_list(args.list))

    # 处理每个URL
    successful_downloads = []
    failed_downloads = []

    for i, url in enumerate(urls_to_process, 1):
        try:
            print(f"\n处理第 {i}/{len(urls_to_process)} 个视频...", file=sys.stderr)
            output_path = process_single_video(url, start_sec, end_sec, args.format, output_path_arg, args.cookies_from_browser)
            successful_downloads.append(output_path)
            print(f"✓ 成功: {output_path}")
        except Exception as e:
            print(f"✗ 失败: {url} - {str(e)}", file=sys.stderr)
            failed_downloads.append((url, str(e)))

    # 输出总结
    print(f"\n处理完成!")
    print(f"成功下载: {len(successful_downloads)} 个文件")
    if failed_downloads:
        print(f"失败: {len(failed_downloads)} 个文件")
        for url, error in failed_downloads:
            print(f"  - {url}: {error}")


def cli():
    """命令行入口点函数"""
    main()


if __name__ == "__main__":
    main()