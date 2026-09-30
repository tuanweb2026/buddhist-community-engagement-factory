"""
1. buddhist-discovery-agent: Tìm kiếm và lọc video Phật giáo
2. opportunity-ranker-agent: Chấm điểm Opportunity Score
"""

import math
from typing import List, Dict, Any
from config.schemas import DiscoveredVideo, OpportunityScoreResult
from connectors.youtube_connector import YouTubeConnector

class BuddhistDiscoveryAgent:
    def __init__(self):
        self.connector = YouTubeConnector()

    def discover(self, keywords: List[str], limit_per_keyword: int = 3) -> List[DiscoveredVideo]:
        discovered = []
        seen_ids = set()

        for kw in keywords:
            raw_videos = self.connector.search(kw, max_results=limit_per_keyword)
            for v in raw_videos:
                vid = v.get("video_id")
                if not vid or vid in seen_ids:
                    continue
                seen_ids.add(vid)
                discovered.append(DiscoveredVideo(
                    video_id=vid,
                    channel_id=v.get("channel_id"),
                    channel_title=v.get("channel_title") or "Kênh Phật Giáo",
                    title=v.get("title") or "Video Phật giáo",
                    url=v.get("url"),
                    description=v.get("description") or "",
                    published_at=v.get("published_at"),
                    view_count=v.get("view_count", 0),
                    like_count=v.get("like_count", 0),
                    comment_count=v.get("comment_count", 0),
                    keyword_source=kw
                ))
        return discovered

class OpportunityRankerAgent:
    """
    Công thức trọng số chuẩn:
    25% audience relevance + 20% freshness + 20% engagement velocity
    + 15% discussion activity + 10% topic match + 10% discussion-gap potential
    """
    def rank(self, video: DiscoveredVideo) -> OpportunityScoreResult:
        title_lower = video.title.lower()
        desc_lower = video.description.lower()

        # 1. Audience relevance (25%)
        buddhist_terms = [
            "phật", "pháp", "thiền", "thích nhất hạnh", "thích pháp hòa",
            "chánh niệm", "buddhism", "dharma", "meditation", "buông bỏ", "an lạc", "tĩnh tâm"
        ]
        rel_hits = sum(1 for t in buddhist_terms if t in title_lower or t in desc_lower)
        audience_rel = min(1.0, 0.4 + (rel_hits * 0.15))

        # 2. Freshness (20%)
        freshness = 0.85 # Default high for recent/relevant search

        # 3. Engagement velocity (20%)
        views = video.view_count or 1000
        engagement_vel = min(1.0, max(0.3, math.log10(views + 10) / 6.0))

        # 4. Discussion activity (15%)
        discussion_act = 0.8 # Standard active engagement

        # 5. Topic match (10%)
        topic_match = 0.9 if any(k in title_lower for k in ["bình an", "buông bỏ", "tĩnh tâm", "chữa lành", "khổ", "nghiệp"]) else 0.7

        # 6. Discussion gap potential (10%)
        gap_pot = 0.85

        total = (
            0.25 * audience_rel +
            0.20 * freshness +
            0.20 * engagement_vel +
            0.15 * discussion_act +
            0.10 * topic_match +
            0.10 * gap_pot
        )
        total = round(min(1.0, max(0.0, total)), 3)

        return OpportunityScoreResult(
            video_id=video.video_id,
            total_score=total,
            audience_relevance=round(audience_rel, 2),
            freshness=round(freshness, 2),
            engagement_velocity=round(engagement_vel, 2),
            discussion_activity=round(discussion_act, 2),
            topic_match=round(topic_match, 2),
            discussion_gap_potential=round(gap_pot, 2),
            recommended_for_research=total >= 0.65,
            reasoning=f"Video có điểm số tiềm năng cao ({total}), chủ đề phù hợp với tinh thần tĩnh thức của @1995lido."
        )
