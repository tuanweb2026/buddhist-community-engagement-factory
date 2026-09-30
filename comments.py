"""
Comments Module: Thu thập một tập nhỏ bình luận hiện có để hiểu cuộc thảo luận
"""

from typing import List
from models import RawComment

def get_recent_comments(video_id: str, max_comments: int = 15) -> List[RawComment]:
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
            raw = info.get("comments", []) or []
            sorted_raw = sorted(raw, key=lambda x: x.get("like_count", 0), reverse=True)
            for c in sorted_raw[:max_comments]:
                comments.append(RawComment(
                    comment_id=str(c.get("id", "")),
                    author=c.get("author") or "Ẩn danh",
                    text=c.get("text", "").strip(),
                    like_count=c.get("like_count", 0) or 0,
                    published_at=str(c.get("timestamp") or "")
                ))
    except Exception as e:
        print(f"[!] Lấy comment video {video_id} gặp lỗi nhẹ: {e}")
    return comments
