"""
YouTube Official API and Smart Scraper Connector
Tuân thủ Nguyên tắc Kiến trúc: API First (YouTube Data API v3 -> yt-dlp Fallback)
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class YouTubeConnector:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.has_official_api = bool(self.api_key and len(self.api_key.strip()) > 10)
        
    def search(self, keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Tìm kiếm video theo từ khóa (API First, fallback sang yt-dlp)
        """
        if self.has_official_api:
            try:
                import requests
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": keyword,
                    "maxResults": max_results,
                    "type": "video",
                    "key": self.api_key
                }
                res = requests.get(url, params=params, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    results = []
                    for item in data.get("items", []):
                        vid = item["id"]["videoId"]
                        snip = item["snippet"]
                        results.append({
                            "video_id": vid,
                            "title": snip.get("title"),
                            "channel_id": snip.get("channelId"),
                            "channel_title": snip.get("channelTitle"),
                            "description": snip.get("description"),
                            "published_at": snip.get("publishedAt"),
                            "url": f"https://www.youtube.com/watch?v={vid}",
                            "view_count": 0,
                            "like_count": 0,
                            "comment_count": 0
                        })
                    return results
            except Exception as e:
                print(f"[!] YouTube Official API gặp lỗi ({e}), chuyển sang fallback yt-dlp.")

        # Fallback yt-dlp
        return self._search_via_ytdlp(keyword, max_results)

    def _search_via_ytdlp(self, keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
        import yt_dlp
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'skip_download': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        }
        results = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(f"ytsearch{max_results}:{keyword}", download=False)
                for entry in res.get("entries", []):
                    if not entry:
                        continue
                    vid = entry.get("id")
                    results.append({
                        "video_id": vid,
                        "title": entry.get("title") or "Video Phật giáo",
                        "channel_id": entry.get("channel_id") or "",
                        "channel_title": entry.get("uploader") or entry.get("channel") or "Kênh Phật Giáo",
                        "description": entry.get("description", ""),
                        "published_at": entry.get("upload_date"),
                        "url": entry.get("url") if entry.get("url") and "http" in entry.get("url") else f"https://www.youtube.com/watch?v={vid}",
                        "view_count": entry.get("view_count", 0) or 0,
                        "like_count": entry.get("like_count", 0) or 0,
                        "comment_count": entry.get("comment_count", 0) or 0
                    })
        except Exception as e:
            print(f"[!] Lỗi yt-dlp search: {e}")
        return results

    def get_comments(self, video_id: str, max_comments: int = 25) -> List[Dict[str, Any]]:
        """Lấy top comments có likes cao nhất"""
        import yt_dlp
        opts = {
            'quiet': True,
            'skip_download': True,
            'getcomments': True,
            'no_warnings': True,
            'max_comments': max_comments,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'extractor_args': {'youtube': {'player_client': ['web', 'android']}}
        }
        url = f"https://www.youtube.com/watch?v={video_id}"
        comments = []
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                raw_c = info.get("comments", [])
                if raw_c:
                    sorted_c = sorted(raw_c, key=lambda x: x.get("like_count", 0), reverse=True)
                    for c in sorted_c[:max_comments]:
                        comments.append({
                            "comment_id": c.get("id"),
                            "author": c.get("author", "Ẩn danh"),
                            "text": c.get("text", "").strip(),
                            "like_count": c.get("like_count", 0),
                            "published_at": c.get("timestamp")
                        })
        except Exception as e:
            print(f"[!] Lỗi lấy comments của {video_id}: {e}")
        return comments
