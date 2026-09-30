"""
Video Priority Queue Module:
Sắp xếp độ ưu tiên của video để chọn ra 3-5 video tốt nhất mỗi ngày:
Các yếu tố chấm điểm:
1. Kênh thuộc Tier cao (A_MAJOR: +40, B_STRONG: +30, C_RISING: +20)
2. Độ mới của video (vừa đăng trong 24h-7 ngày: +30)
3. Tỷ lệ tương tác thảo luận (comment count / view count)
4. Mức độ liên quan đến giáo lý / chánh niệm ứng dụng
"""

from typing import List, Tuple
from datetime import datetime
from models import VideoMetadata, ChannelRecord

class VideoPriorityQueue:
    def calculate_priority_score(self, video: VideoMetadata, channel: ChannelRecord = None) -> float:
        score = 50.0 # Base score

        # 1. Tier score
        if channel:
            tier_weights = {
                "A_MAJOR": 35.0,
                "B_STRONG": 25.0,
                "C_RISING": 15.0,
                "D_EMERGING": 5.0
            }
            score += tier_weights.get(channel.tier, 10.0)

        # 2. Velocity / Engagement signal
        if video.view_count > 0:
            comment_ratio = video.comment_count / max(video.view_count, 1)
            # Thảo luận sôi nổi
            if comment_ratio > 0.01:
                score += 15.0
            elif comment_ratio > 0.005:
                score += 10.0
            elif comment_ratio > 0.001:
                score += 5.0

        # 3. View sweet spot (5k - 500k views là tối ưu nhất cho engagement)
        if 5000 <= video.view_count <= 500000:
            score += 10.0
        elif video.view_count > 500000:
            score += 5.0

        # 4. Ngôn ngữ rõ ràng (VI hoặc EN)
        if video.language in ("vi", "en"):
            score += 10.0
        else:
            score -= 50.0 # Ngôn ngữ không chắc chắn bị trừ điểm nặng

        return min(score, 100.0)

    def rank_and_select(self, videos: List[VideoMetadata], channel_map: dict = None, top_k: int = 5) -> List[Tuple[VideoMetadata, float]]:
        channel_map = channel_map or {}
        scored_videos = []
        for v in videos:
            ch = channel_map.get(v.channel_id)
            score = self.calculate_priority_score(v, ch)
            scored_videos.append((v, score))

        scored_videos.sort(key=lambda x: x[1], reverse=True)
        return scored_videos[:top_k]
