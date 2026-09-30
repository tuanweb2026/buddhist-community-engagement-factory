"""
Data Models (Pydantic) cho Phase 2 — Real Publishing + Performance Tracking
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class VideoMetadata(BaseModel):
    video_id: str
    channel_id: Optional[str] = None
    channel_name: str
    channel_handle: Optional[str] = None
    title: str
    url: str
    description: str = ""
    published_at: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    language: str = "vi" # 'vi' hoặc 'en'

class VideoResearch(BaseModel):
    video_id: str
    main_topic: str
    summary: str = ""
    video_summary: Optional[str] = None # Cho tương thích Phase 1
    key_points: List[str] = []
    buddhist_context: str = ""
    important_concepts: List[str] = []
    discussion_questions: List[str] = []
    interesting_insights: List[str] = []
    discussion_gap: str = ""
    evidence_points: List[str] = [] # Điểm chứng cứ từ transcript / nội dung video
    confidence: float = 1.0

class RawComment(BaseModel):
    comment_id: str
    author: str
    text: str
    like_count: int = 0
    published_at: Optional[str] = None

class CommentCandidate(BaseModel):
    candidate_id: str
    video_id: str
    style: str # Cho phép "Reflective", "Insightful", "Thoughtful Question" hoặc "REFLECTIVE"
    language: str = "vi" # 'vi' hoặc 'en'
    content: str
    insight_summary: str = ""
    evidence_points: List[str] = [] # Chứng cứ ngữ cảnh gắn liền với comment
    research_confidence: str = "HIGH" # 'HIGH', 'MEDIUM', 'LOW'



class QualityResult(BaseModel):
    passed: bool
    rejection_reason: Optional[str] = None

class PublishResult(BaseModel):
    video_id: str
    video_url: str
    channel_name: str
    channel_id: Optional[str] = None
    comment_id: Optional[str] = None
    comment_text: str
    language: str
    published_at: str
    status: Literal["PUBLISHED", "FAILED", "SKIPPED", "DRY_RUN"]
    error_message: Optional[str] = None

class PerformanceMetric(BaseModel):
    comment_id: str
    video_id: str
    likes_24h: int = 0
    replies_24h: int = 0
    likes_48h: int = 0
    replies_48h: int = 0
    last_checked: str = ""

# --- Phase 2 Upgrade Models ---

class ChannelRecord(BaseModel):
    channel_id: str
    channel_name: str
    channel_handle: Optional[str] = None
    channel_url: str = ""
    language: str = "vi" # 'vi' or 'en'
    subscriber_count: int = 0
    video_count: int = 0
    tradition: str = "General Buddhism"
    tier: str = "D_EMERGING" # 'A_MAJOR', 'B_STRONG', 'C_RISING', 'D_EMERGING', 'REJECTED'
    status: str = "ACTIVE" # 'ACTIVE', 'PAUSED', 'EXCLUDED'
    last_scanned_at: Optional[str] = None
    created_at: Optional[str] = None

class ChannelIntelligenceCard(BaseModel):
    channel_id: str
    channel_name: str = ""
    content_strengths: List[str] = []
    audience_engagement_level: str = "Moderate" # High, Moderate, Low
    top_performing_topics: List[str] = []
    comment_community_vibe: str = ""
    recurring_questions: List[str] = []
    lido_learnings: List[str] = []
    updated_at: Optional[str] = None

class CommunityIntelligenceReport(BaseModel):
    video_id: str
    channel_id: Optional[str] = None
    audience_pain_points: List[str] = []
    core_needs: List[str] = []
    desired_emotions: List[str] = [] # e.g. An yên, Buông xả, Sáng tỏ
    recurring_questions: List[str] = []
    sentiment_distribution: Dict[str, float] = {}

class LidoInsight(BaseModel):
    insight_id: str
    date: str
    category: str # 'content_gap', 'format_opportunity', 'audience_need', 'discussion_trend'
    observation: str
    interpretation: str
    opportunity_for_lido: str
    priority: str = "MEDIUM" # 'HIGH', 'MEDIUM', 'LOW'
    created_at: Optional[str] = None

