# Scraper lấy video và comment từ YouTube mà không bắt buộc có API Key
import yt_dlp
from typing import List, Dict, Any, Optional

class YouTubeScraper:
    def __init__(self):
        self.ydl_opts_search = {
            'quiet': True,
            'extract_flat': True,
            'skip_download': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

    def search_videos(self, keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Tìm kiếm video theo từ khóa trên YouTube
        """
        query = f"ytsearch{max_results}:{keyword}"
        videos = []
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts_search) as ydl:
                result = ydl.extract_info(query, download=False)
                if 'entries' in result:
                    for entry in result['entries']:
                        if not entry:
                            continue
                        vid_id = entry.get("id")
                        videos.append({
                            "id": vid_id,
                            "title": entry.get("title") or "Video Phật giáo",
                            "channel": entry.get("uploader") or entry.get("channel") or "Kênh Phật Giáo",
                            "channel_url": entry.get("uploader_url") or entry.get("channel_url") or "",
                            "view_count": entry.get("view_count", 0),
                            "duration": entry.get("duration", 0),
                            "webpage_url": entry.get("url") if entry.get("url") and "http" in entry.get("url") else f"https://www.youtube.com/watch?v={vid_id}",
                            "description": entry.get("description", "")
                        })
        except Exception as e:
            print(f"[!] Lỗi khi tìm kiếm video với từ khóa '{keyword}': {e}")
        return videos

    def get_video_details_and_comments(self, video_url: str, max_comments: int = 25) -> Dict[str, Any]:
        """
        Lấy chi tiết video và danh sách top bình luận
        """
        opts = {
            'quiet': True,
            'skip_download': True,
            'getcomments': True,
            'no_warnings': True,
            'max_comments': max_comments,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'extractor_args': {'youtube': {'player_client': ['web', 'android']}}
        }
        details = {
            "info": {},
            "comments": []
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                details["info"] = {
                    "id": info.get("id"),
                    "title": info.get("title"),
                    "channel": info.get("uploader") or info.get("channel"),
                    "channel_url": info.get("uploader_url") or info.get("channel_url"),
                    "view_count": info.get("view_count", 0),
                    "like_count": info.get("like_count", 0),
                    "comment_count": info.get("comment_count", 0),
                    "duration": info.get("duration", 0),
                    "upload_date": info.get("upload_date"),
                    "webpage_url": info.get("webpage_url", video_url),
                    "description": info.get("description", "")
                }
                
                raw_comments = info.get("comments", [])
                if raw_comments:
                    # Sắp xếp comment có nhiều like nhất
                    sorted_comments = sorted(raw_comments, key=lambda x: x.get("like_count", 0), reverse=True)
                    for c in sorted_comments[:max_comments]:
                        details["comments"].append({
                            "id": c.get("id"),
                            "author": c.get("author", "Ẩn danh"),
                            "text": c.get("text", "").strip(),
                            "like_count": c.get("like_count", 0),
                            "timestamp": c.get("timestamp")
                        })
        except Exception as e:
            print(f"[!] Lỗi khi lấy thông tin/comment của {video_url}: {e}")
            
        return details

if __name__ == "__main__":
    scraper = YouTubeScraper()
    print("Testing search...")
    res = scraper.search_videos("thuyết pháp Thích Pháp Hòa", max_results=2)
    print(f"Found {len(res)} videos:")
    for v in res:
        print(f"- {v['title']} ({v['webpage_url']})")
