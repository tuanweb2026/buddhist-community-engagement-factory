"""
Video Inventory Module:
Quản lý danh mục video của các kênh trong Channel Radar:
- Quét và cập nhật video mới từ các kênh theo dõi
- Lưu trữ vào bảng videos với tracking: first_seen_at, view_count, comment_count
- Không bao giờ trùng lặp video đã có trong kho
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build

from app_config import YOUTUBE_API_KEY
from models import VideoMetadata, ChannelRecord
from db_storage import save_video, is_video_processed, get_connection
from language_detector import detect_language

class VideoInventory:
    def __init__(self, api_key: Optional[str] = YOUTUBE_API_KEY):
        self.api_key = api_key
        self.youtube = None
        if api_key:
            try:
                self.youtube = build("youtube", "v3", developerKey=api_key)
            except Exception:
                self.youtube = None

    def fetch_channel_recent_videos(self, channel: ChannelRecord, max_results: int = 5) -> List[VideoMetadata]:
        """Lấy các video mới nhất từ một kênh cụ thể"""
        discovered_videos: List[VideoMetadata] = []

        if self.youtube and not channel.channel_id.startswith("UCsZ6Jp8"):
            try:
                res = self.youtube.search().list(
                    part="snippet",
                    channelId=channel.channel_id,
                    maxResults=max_results,
                    order="date",
                    type="video"
                ).execute()

                video_ids = [item["id"]["videoId"] for item in res.get("items", []) if "videoId" in item.get("id", {})]
                if video_ids:
                    # Lấy thống kê chi tiết
                    v_res = self.youtube.videos().list(
                        part="snippet,statistics",
                        id=",".join(video_ids)
                    ).execute()

                    for v_item in v_res.get("items", []):
                        vid = v_item["id"]
                        snippet = v_item.get("snippet", {})
                        stats = v_item.get("statistics", {})

                        title = snippet.get("title", "")
                        desc = snippet.get("description", "")
                        lang_code, _ = detect_language(title, desc)

                        v = VideoMetadata(
                            video_id=vid,
                            channel_id=channel.channel_id,
                            channel_name=channel.channel_name,
                            channel_handle=channel.channel_handle,
                            title=title,
                            url=f"https://www.youtube.com/watch?v={vid}",
                            description=desc,
                            published_at=snippet.get("publishedAt"),
                            view_count=int(stats.get("viewCount", 0)),
                            like_count=int(stats.get("likeCount", 0)),
                            comment_count=int(stats.get("commentCount", 0)),
                            language=lang_code
                        )
                        discovered_videos.append(v)
            except Exception as e:
                pass

        return discovered_videos

    def ingest_videos(self, videos: List[VideoMetadata]) -> int:
        """Đưa video vào kho dữ liệu nếu chưa có"""
        ingested = 0
        for v in videos:
            if not is_video_processed(v.video_id):
                save_video(v)
                ingested += 1
        return ingested
