"""
Discovery Module (Phase 2):
Tìm kiếm và lọc video Phật giáo (tiếng Việt & tiếng Anh),
đồng thời tích hợp language_detector để gán ngôn ngữ chính xác.
"""

from typing import List
from models import VideoMetadata
from app_config import YOUTUBE_API_KEY, DISCOVERY_KEYWORDS
from db_storage import is_video_processed
from language_detector import detect_community_language

def discover_videos(target_count: int = 5) -> List[VideoMetadata]:
    discovered = []
    seen_ids = set()

    # 1. Thử YouTube Data API v3
    if YOUTUBE_API_KEY and len(YOUTUBE_API_KEY.strip()) > 10:
        try:
            import requests
            for kw in DISCOVERY_KEYWORDS:
                if len(discovered) >= target_count:
                    break
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": kw,
                    "maxResults": 3,
                    "type": "video",
                    "key": YOUTUBE_API_KEY
                }
                res = requests.get(url, params=params, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    for item in data.get("items", []):
                        vid = item["id"]["videoId"]
                        if vid in seen_ids or is_video_processed(vid):
                            continue
                        seen_ids.add(vid)
                        snip = item["snippet"]
                        title = snip.get("title", "")
                        desc = snip.get("description", "")
                        channel = snip.get("channelTitle", "")

                        lang = detect_community_language(title, desc, channel)
                        discovered.append(VideoMetadata(
                            video_id=vid,
                            channel_id=snip.get("channelId"),
                            channel_name=channel or "Kênh Phật Giáo",
                            title=title or "Video Phật giáo",
                            url=f"https://www.youtube.com/watch?v={vid}",
                            description=desc,
                            published_at=snip.get("publishedAt"),
                            language=lang
                        ))
                        if len(discovered) >= target_count:
                            break
            if discovered:
                return discovered
        except Exception as e:
            print(f"[!] YouTube API gặp sự cố ({e}), chuyển sang fallback yt-dlp.")

    # 2. Fallback yt-dlp
    import yt_dlp
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for kw in DISCOVERY_KEYWORDS:
                if len(discovered) >= target_count:
                    break
                res = ydl.extract_info(f"ytsearch3:{kw}", download=False)
                for entry in res.get("entries", []):
                    if not entry:
                        continue
                    vid = entry.get("id")
                    if not vid or vid in seen_ids or is_video_processed(vid):
                        continue
                    seen_ids.add(vid)
                    title = entry.get("title") or "Bài giảng Phật giáo"
                    desc = entry.get("description", "") or ""
                    channel = entry.get("uploader") or entry.get("channel") or "Kênh Phật Giáo"

                    lang = detect_community_language(title, desc, channel)
                    discovered.append(VideoMetadata(
                        video_id=vid,
                        channel_id=entry.get("channel_id") or entry.get("uploader_id"),
                        channel_name=channel,
                        channel_handle=f"@{channel.lower().replace(' ', '')}",
                        title=title,
                        url=entry.get("url") if entry.get("url") and "http" in entry.get("url") else f"https://www.youtube.com/watch?v={vid}",
                        description=desc,
                        published_at=entry.get("upload_date"),
                        view_count=entry.get("view_count", 0) or 0,
                        language=lang
                    ))
                    if len(discovered) >= target_count:
                        break
    except Exception as e:
        print(f"[!] Lỗi discovery yt-dlp: {e}")

    return discovered[:target_count]
