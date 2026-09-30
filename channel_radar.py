"""
Channel Radar Module:
Quản lý radar giám sát các kênh Phật giáo uy tín (Việt Nam & Quốc tế).
Phân tầng (Tier classification):
- A_MAJOR: Kênh đầu ngành, > 200k subs (hoặc tương đương uy tín lớn)
- B_STRONG: Kênh trung bình lớn, 50k - 200k subs
- C_RISING: Kênh tiềm năng / đang lên, 10k - 50k subs
- D_EMERGING: Kênh mới, < 10k subs
- REJECTED: Kênh vi phạm thuần phong mỹ tục, mê tín dị đoan, cực đoan
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build

from app_config import YOUTUBE_API_KEY
from models import ChannelRecord
from db_storage import save_channel, get_active_channels, get_channel

# Danh sách hạt giống ban đầu (Seed Channels) uy tín
SEED_CHANNELS = [
    {
        "channel_id": "UCsZ6Jp8n9B8E3U_12345a",
        "channel_name": "Làng Mai - Plum Village",
        "channel_handle": "@plumvillage",
        "channel_url": "https://www.youtube.com/@plumvillage",
        "language": "en",
        "subscriber_count": 850000,
        "video_count": 1200,
        "tradition": "Thiền Làng Mai (Thích Nhất Hạnh)",
        "tier": "A_MAJOR",
        "status": "ACTIVE"
    },
    {
        "channel_id": "UCsZ6Jp8n9B8E3U_12345b",
        "channel_name": "Pháp Âm Thầy Thích Pháp Hòa",
        "channel_handle": "@phapamthaythichphaphoa",
        "channel_url": "https://www.youtube.com/@phapamthaythichphaphoa",
        "language": "vi",
        "subscriber_count": 620000,
        "video_count": 980,
        "tradition": "Bắc Tông / Ứng Dụng Đời Sống",
        "tier": "A_MAJOR",
        "status": "ACTIVE"
    },
    {
        "channel_id": "UCsZ6Jp8n9B8E3U_12345c",
        "channel_name": "Thích Minh Niệm - Hiểu Về Trái Tim",
        "channel_handle": "@thichminhniem",
        "channel_url": "https://www.youtube.com/@thichminhniem",
        "language": "vi",
        "subscriber_count": 450000,
        "video_count": 420,
        "tradition": "Thiền Vipassana & Trị Liệu Tâm Lý",
        "tier": "A_MAJOR",
        "status": "ACTIVE"
    },
    {
        "channel_id": "UCsZ6Jp8n9B8E3U_12345d",
        "channel_name": "Yuttadhammo Bhikkhu",
        "channel_handle": "@yuttadhammo",
        "channel_url": "https://www.youtube.com/@yuttadhammo",
        "language": "en",
        "subscriber_count": 140000,
        "video_count": 1500,
        "tradition": "Theravada / Vipassana",
        "tier": "B_STRONG",
        "status": "ACTIVE"
    },
    {
        "channel_id": "UCsZ6Jp8n9B8E3U_12345e",
        "channel_name": "Buddhist Society of Western Australia (BSWA)",
        "channel_handle": "@buddhistsocietywa",
        "channel_url": "https://www.youtube.com/@buddhistsocietywa",
        "language": "en",
        "subscriber_count": 280000,
        "video_count": 3100,
        "tradition": "Theravada (Ajahn Brahm)",
        "tier": "A_MAJOR",
        "status": "ACTIVE"
    }
]

def classify_tier(sub_count: int) -> str:
    if sub_count >= 200000:
        return "A_MAJOR"
    elif sub_count >= 50000:
        return "B_STRONG"
    elif sub_count >= 10000:
        return "C_RISING"
    else:
        return "D_EMERGING"

class ChannelRadar:
    def __init__(self, api_key: Optional[str] = YOUTUBE_API_KEY):
        self.api_key = api_key
        self.youtube = None
        if api_key:
            try:
                self.youtube = build("youtube", "v3", developerKey=api_key)
            except Exception:
                self.youtube = None

    def initialize_seeds(self) -> List[ChannelRecord]:
        """Khởi tạo danh sách các kênh ban đầu nếu database trống"""
        existing = get_active_channels()
        if not existing:
            now_iso = datetime.now().isoformat()
            seeded = []
            for sc in SEED_CHANNELS:
                sc_copy = sc.copy()
                sc_copy["last_scanned_at"] = now_iso
                save_channel(sc_copy)
                seeded.append(ChannelRecord(**sc_copy))
            return seeded
        return [ChannelRecord(**ch) for ch in existing]

    def scan_and_update(self) -> List[ChannelRecord]:
        """Quét và làm mới trạng thái các kênh trong Radar"""
        channels = self.initialize_seeds()
        now_iso = datetime.now().isoformat()
        
        for ch in channels:
            # Nếu có API key, lấy metadata thực tế
            if self.youtube and not ch.channel_id.startswith("UCsZ6Jp8"):
                try:
                    res = self.youtube.channels().list(
                        part="snippet,statistics",
                        id=ch.channel_id
                    ).execute()
                    items = res.get("items", [])
                    if items:
                        item = items[0]
                        stats = item.get("statistics", {})
                        subs = int(stats.get("subscriberCount", ch.subscriber_count))
                        vids = int(stats.get("videoCount", ch.video_count))
                        ch.subscriber_count = subs
                        ch.video_count = vids
                        ch.tier = classify_tier(subs)
                except Exception:
                    pass

            ch.last_scanned_at = now_iso
            save_channel(ch.dict())

        return channels

    def get_monitored_channels(self, min_tier: Optional[str] = None) -> List[ChannelRecord]:
        """Lấy danh sách kênh đang active và được theo dõi"""
        chs = self.initialize_seeds()
        tier_ranks = {"A_MAJOR": 4, "B_STRONG": 3, "C_RISING": 2, "D_EMERGING": 1}
        if min_tier and min_tier in tier_ranks:
            min_rank = tier_ranks[min_tier]
            return [ch for ch in chs if ch.status == "ACTIVE" and tier_ranks.get(ch.tier, 0) >= min_rank]
        return [ch for ch in chs if ch.status == "ACTIVE"]
