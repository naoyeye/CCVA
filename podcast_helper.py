#!/usr/bin/env python3
"""
播客下载助手
提供多种方法来下载播客音频
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import platform
import requests
import xml.etree.ElementTree as ET

try:
    import yt_dlp  # type: ignore
except ImportError:
    sys.stderr.write("Error: The 'yt-dlp' package is required. Install it with 'pip install yt-dlp'.\n")
    sys.exit(1)


def search_podcast_by_name(podcast_name: str) -> list:
    """通过播客名称搜索播客"""
    try:
        api_url = f"https://itunes.apple.com/search?term={podcast_name}&entity=podcast&limit=10"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        results = []
        if data.get('resultCount', 0) > 0:
            for item in data['results']:
                results.append({
                    'name': item.get('collectionName', 'Unknown'),
                    'artist': item.get('artistName', 'Unknown'),
                    'feed_url': item.get('feedUrl', ''),
                    'id': item.get('collectionId', ''),
                    'description': item.get('description', '')[:200] + '...' if item.get('description') else ''
                })
        return results
    except Exception as e:
        print(f"搜索失败: {e}", file=sys.stderr)
        return []


def get_latest_episodes(rss_url: str, limit: int = 10) -> list:
    """获取播客的最新几集"""
    try:
        response = requests.get(rss_url, timeout=10)
        root = ET.fromstring(response.content)
        
        episodes = []
        for i, item in enumerate(root.findall('.//item')):
            if i >= limit:
                break
                
            title_elem = item.find('title')
            title = title_elem.text if title_elem is not None else f"Episode {i+1}"
            
            enclosure = item.find('enclosure')
            audio_url = enclosure.get('url') if enclosure is not None else None
            
            if audio_url:
                episodes.append({
                    'title': title,
                    'audio_url': audio_url,
                    'description': item.find('description').text if item.find('description') is not None else ''
                })
        
        return episodes
    except Exception as download_audio_with_yt_dlp:
        print(f"解析 RSS Feed 失败: {e}", file=sys.stderr)
        return []


def download_audio_with_yt_dlp(audio_url: str, output_path: Path, format: str = "mp3"):
    """使用 yt-dlp 下载音频"""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_path),
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([audio_url])


def convert_audio(input_file: str, output_file: Path, format: str):
    """使用 ffmpeg 转换音频格式"""
    if format == "mp3":
        codec = "libmp3lame"
        extra = ["-b:a", "192k"]
    elif format == "wav":
        codec = "pcm_s16le"
        extra = ["-ac", "2", "-ar", "44100"]
    elif format == "aiff":
        codec = "pcm_s16be"
        extra = ["-ac", "2", "-ar", "44100"]
    else:
        raise ValueError(f"Unsupported format: {format}")

    cmd = [
        "ffmpeg",
        "-loglevel", "error",
        "-y",
        "-i", input_file,
        "-acodec", codec,
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


def extract_podcast_id_from_url(url: str) -> Optional[Tuple[str, str]]:
    """从 Apple Podcasts URL 提取 podcast ID 和 episode ID"""
    # 匹配 Apple Podcasts URL 格式
    # https://podcasts.apple.com/ua/podcast/xxx/id1751418168?i=1000679962434
    pattern = r'podcasts\.apple\.com/[^/]+/podcast/[^/]+/id(\d+).*[?&]i=(\d+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None


def get_podcast_rss_url(podcast_id: str) -> Optional[str]:
    """通过 podcast ID 获取 RSS Feed URL"""
    try:
        # 使用 iTunes API 获取 podcast 信息
        api_url = f"https://itunes.apple.com/lookup?id={podcast_id}&entity=podcast"
        print(f"正在查询 iTunes API: {api_url}", file=sys.stderr)
        response = requests.get(api_url, timeout=10)
        print(f"API 响应状态: {response.status_code}", file=sys.stderr)
        data = response.json()
        
        if data.get('resultCount', 0) > 0:
            podcast_info = data['results'][0]
            feed_url = podcast_info.get('feedUrl')
            print(f"找到 RSS Feed: {feed_url}", file=sys.stderr)
            return feed_url
        else:
            print("iTunes API 返回空结果", file=sys.stderr)
    except Exception as e:
        print(f"获取 RSS Feed 失败: {e}", file=sys.stderr)
    
    return None


def find_episode_in_rss(rss_url: str, episode_id: str) -> Optional[dict]:
    """在 RSS Feed 中查找特定 episode"""
    try:
        response = requests.get(rss_url, timeout=10)
        root = ET.fromstring(response.content)
        
        # 查找所有 item
        for item in root.findall('.//item'):
            # 查找 enclosure 标签获取音频链接
            enclosure = item.find('enclosure')
            if enclosure is not None:
                audio_url = enclosure.get('url')
                if audio_url:
                    # 检查是否匹配 episode ID（通过 URL 或 GUID）
                    guid = item.find('guid')
                    if guid is not None and episode_id in guid.text:
                        return {
                            'title': item.find('title').text if item.find('title') is not None else 'Unknown',
                            'audio_url': audio_url,
                            'description': item.find('description').text if item.find('description') is not None else ''
                        }
    except Exception as e:
        print(f"解析 RSS Feed 失败: {e}", file=sys.stderr)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="播客下载助手 - 支持多种播客平台，包括 Apple Podcasts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--episode", "-e", type=int, default=0, help="选择第几集 (从0开始)")
    parser.add_argument("--format", "-f", default="mp3", choices=["mp3", "wav", "aiff"], help="输出音频格式")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    parser.add_argument("--list", "-l", action="store_true", help="列出可用的播客或集数")
    
    # 让 --search、--rss 和 --url 成为互斥的必需参数之一
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--search", "-s", help="搜索播客名称")
    group.add_argument("--rss", "-r", help="直接提供 RSS Feed URL")
    group.add_argument("--url", "-u", help="Apple Podcasts URL 或任何播客 URL")
    
    args = parser.parse_args()
    
    if args.search:
        # 搜索模式
        print(f"正在搜索播客: {args.search}")
        results = search_podcast_by_name(args.search)
        
        if not results:
            print("未找到匹配的播客")
            return
        
        print(f"\n找到 {len(results)} 个播客:")
        for i, podcast in enumerate(results):
            print(f"{i+1}. {podcast['name']} - {podcast['artist']}")
            print(f"   ID: {podcast['id']}")
            print(f"   RSS: {podcast['feed_url']}")
            print(f"   描述: {podcast['description']}")
            print()
        
        if args.list:
            return
        
        # 让用户选择
        try:
            choice = int(input("请选择播客 (输入数字): ")) - 1
            if 0 <= choice < len(results):
                selected_podcast = results[choice]
                rss_url = selected_podcast['feed_url']
            else:
                print("无效选择")
                return
        except (ValueError, KeyboardInterrupt):
            print("操作取消")
            return
    
    elif args.rss:
        # 直接 RSS 模式
        rss_url = args.rss
        print(f"使用 RSS Feed: {rss_url}")
    
    elif args.url:
        # URL 模式 - 支持 Apple Podcasts 和其他播客 URL
        url = args.url
        print(f"处理 URL: {url}")
        
        # 检查是否是 Apple Podcasts URL
        if "podcasts.apple.com" in url:
            print("检测到 Apple Podcasts URL，尝试获取 RSS Feed...")
            ids = extract_podcast_id_from_url(url)
            if not ids:
                print("错误: 无法从 Apple Podcasts URL 中提取 podcast ID 和 episode ID", file=sys.stderr)
                sys.exit(1)
            
            podcast_id, episode_id = ids
            print(f"Podcast ID: {podcast_id}, Episode ID: {episode_id}")
            
            # 获取 RSS Feed URL
            rss_url = get_podcast_rss_url(podcast_id)
            if not rss_url:
                print("错误: 无法获取 RSS Feed URL。这可能是付费播客，需要订阅才能访问。", file=sys.stderr)
                print("建议：", file=sys.stderr)
                print("1. 使用 --search 搜索其他免费播客", file=sys.stderr)
                print("2. 使用 --rss 直接提供 RSS Feed URL", file=sys.stderr)
                print("3. 考虑通过官方渠道订阅该播客", file=sys.stderr)
                sys.exit(1)
            
            # 在 RSS Feed 中查找特定 episode
            print("正在查找音频链接...", file=sys.stderr)
            episode_info = find_episode_in_rss(rss_url, episode_id)
            if not episode_info:
                print("错误: 在 RSS Feed 中找不到指定的 episode", file=sys.stderr)
                print("尝试下载最新一集...", file=sys.stderr)
                # 如果找不到特定 episode，就下载最新一集
                episodes = get_latest_episodes(rss_url, 1)
                if episodes:
                    episode_info = episodes[0]
                else:
                    print("错误: 无法获取任何播客内容", file=sys.stderr)
                    sys.exit(1)
            
            print(f"找到 episode: {episode_info['title']}")
            print(f"音频链接: {episode_info['audio_url']}")
            
            # 处理输出路径
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
            else:
                home = str(Path.home())
                sys_name = platform.system()
                if sys_name == "Windows":
                    downloads = os.path.join(home, "Downloads")
                elif sys_name == "Darwin":
                    downloads = os.path.join(home, "Downloads")
                else:
                    downloads = os.path.join(home, "Downloads")
                    if not os.path.exists(downloads):
                        downloads = os.path.join(home, "下载")
                
                # 生成文件名
                safe_title = re.sub(r'[^\w\s-]', '', episode_info['title']).strip()
                safe_title = re.sub(r'[-\s]+', '-', safe_title)
                filename = f"{safe_title}.{args.format}"
                output_path = Path(downloads) / filename
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 下载音频
            print("正在下载音频...", file=sys.stderr)
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_file = Path(tmp_dir) / "audio"
                download_audio_with_yt_dlp(episode_info['audio_url'], tmp_file)
                
                # 如果下载的文件不是目标格式，进行转换
                if tmp_file.suffix != f".{args.format}":
                    print("正在转换音频格式...", file=sys.stderr)
                    convert_audio(str(tmp_file), output_path, args.format)
                else:
                    # 直接移动文件
                    tmp_file.rename(output_path)
            
            print(f"\n完成! 音频已保存到: {output_path}")
            return
        else:
            # 其他类型的 URL，尝试直接下载
            print("尝试直接下载...")
            try:
                # 处理输出路径
                if args.output:
                    output_path = Path(args.output).expanduser().resolve()
                else:
                    home = str(Path.home())
                    sys_name = platform.system()
                    if sys_name == "Windows":
                        downloads = os.path.join(home, "Downloads")
                    elif sys_name == "Darwin":
                        downloads = os.path.join(home, "Downloads")
                    else:
                        downloads = os.path.join(home, "Downloads")
                        if not os.path.exists(downloads):
                            downloads = os.path.join(home, "下载")
                    
                    filename = f"podcast.{args.format}"
                    output_path = Path(downloads) / filename
                
                # 确保输出目录存在
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 下载音频
                print("正在下载音频...", file=sys.stderr)
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_file = Path(tmp_dir) / "audio"
                    download_audio_with_yt_dlp(url, tmp_file)
                    
                    # 如果下载的文件不是目标格式，进行转换
                    if tmp_file.suffix != f".{args.format}":
                        print("正在转换音频格式...", file=sys.stderr)
                        convert_audio(str(tmp_file), output_path, args.format)
                    else:
                        # 直接移动文件
                        tmp_file.rename(output_path)
                
                print(f"\n完成! 音频已保存到: {output_path}")
                return
            except Exception as e:
                print(f"直接下载失败: {e}", file=sys.stderr)
                print("请尝试使用 --search 搜索播客或 --rss 提供 RSS Feed URL", file=sys.stderr)
                sys.exit(1)
    
    else:
        print("请使用 --search 搜索播客、--rss 提供 RSS Feed URL 或 --url 提供播客 URL")
        return
    
    # 获取播客集数
    print("正在获取播客集数...")
    episodes = get_latest_episodes(rss_url, 20)
    
    if not episodes:
        print("无法获取播客集数")
        return
    
    print(f"\n找到 {len(episodes)} 集:")
    for i, episode in enumerate(episodes):
        print(f"{i}. {episode['title']}")
        if episode['description']:
            print(f"   {episode['description'][:100]}...")
        print()
    
    if args.list:
        return
    
    # 选择集数
    if args.episode < 0 or args.episode >= len(episodes):
        try:
            episode_choice = int(input(f"请选择集数 (0-{len(episodes)-1}): "))
            if 0 <= episode_choice < len(episodes):
                selected_episode = episodes[episode_choice]
            else:
                print("无效选择")
                return
        except (ValueError, KeyboardInterrupt):
            print("操作取消")
            return
    else:
        selected_episode = episodes[args.episode]
    
    print(f"\n选择集数: {selected_episode['title']}")
    print(f"音频链接: {selected_episode['audio_url']}")
    
    # 处理输出路径
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
    else:
        home = str(Path.home())
        sys_name = platform.system()
        if sys_name == "Windows":
            downloads = os.path.join(home, "Downloads")
        elif sys_name == "Darwin":
            downloads = os.path.join(home, "Downloads")
        else:
            downloads = os.path.join(home, "Downloads")
            if not os.path.exists(downloads):
                downloads = os.path.join(home, "下载")
        
        # 生成文件名
        safe_title = re.sub(r'[^\w\s-]', '', selected_episode['title']).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = f"{safe_title}.{args.format}"
        output_path = Path(downloads) / filename
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 下载音频
    print("正在下载音频...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "audio"
        download_audio_with_yt_dlp(selected_episode['audio_url'], tmp_file)
        
        # 如果下载的文件不是目标格式，进行转换
        if tmp_file.suffix != f".{args.format}":
            print("正在转换音频格式...")
            convert_audio(str(tmp_file), output_path, args.format)
        else:
            # 直接移动文件
            tmp_file.rename(output_path)
    
    print(f"\n完成! 音频已保存到: {output_path}")


if __name__ == "__main__":
    main()
