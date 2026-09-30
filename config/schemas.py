"""
Schema định nghĩa dữ liệu trung tâm chuẩn Pydantic cho toàn bộ hệ thống BCE-Factory
"""

from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# 1. DISCOVERY SCHEMAS
class DiscoveredVideo(BaseModel):
    video_id: str
    channel_id: Optional[str] = None
    channel_title: str
    channel_url: Optional[str] = None
    title: str
    url: str
    description: str = ""
    published_at: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    duration: int = 0
    keyword_source: str = ""
    discovered_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class OpportunityScoreResult(BaseModel):
    video_id: str
    total_score: float = Field(..., ge=0.0, le=1.0)
    audience_relevance: float = Field(..., ge=0.0, le=1.0)
    freshness: float = Field(..., ge=0.0, le=1.0)
    engagement_velocity: float = Field(..., ge=0.0, le=1.0)
    discussion_activity: float = Field(..., ge=0.0, le=1.0)
    topic_match: float = Field(..., ge=0.0, le=1.0)
    discussion_gap_potential: float = Field(..., ge=0.0, le=1.0)
    recommended_for_research: bool = True
    reasoning: str = ""

# 2. RESEARCH SCHEMAS
class TranscriptSegment(BaseModel):
    text: str
    start: float
    duration: float

class TranscriptResult(BaseModel):
    video_id: str
    has_transcript: bool
    language: Optional[str] = None
    source: Literal["OFFICIAL_CAPTIONS", "AUTO_GENERATED", "FALLBACK_METADATA", "NONE"]
    confidence: float = 1.0
    full_text: str = ""
    segments: List[TranscriptSegment] = []

class VideoKnowledgeCard(BaseModel):
    video_id: str
    core_topic: str
    main_claims: List[str] = []
    key_points: List[str] = []
    questions_raised: List[str] = []
    emotional_themes: List[str] = []
    uncertainties: List[str] = []
    evidence_snippets: List[str] = []
    is_sufficient_context: bool = True

class BuddhistContext(BaseModel):
    tradition: str = "Tập quán chung / Phật giáo ứng dụng" # Bắc tông, Nam tông, Thiền phái, Làng Mai...
    key_concepts: List[str] = [] # Vô thường, Khổ, Vô ngã, Từ bi, Chánh niệm...
    appropriate_tone: str = "Tĩnh lặng, khiêm cung, sẻ chia, kính tín"
    sensitivities_to_avoid: List[str] = []

# 3. COMMENT & GAP SCHEMAS
CommentCategory = Literal[
    "QUESTION", "INSIGHT", "PERSONAL_EXPERIENCE",
    "AGREEMENT", "DISAGREEMENT", "GRATITUDE",
    "CONFUSION", "DISCUSSION", "REPETITION",
    "LOW_VALUE", "SPAM"
]

class ClassifiedComment(BaseModel):
    comment_id: str
    author: str
    text: str
    like_count: int = 0
    published_at: Optional[str] = None
    category: CommentCategory
    extracted_pain_point: Optional[str] = None

class CommentAnalysisReport(BaseModel):
    video_id: str
    total_analyzed: int
    category_distribution: Dict[str, int]
    top_pain_points: List[str]
    recurring_themes: List[str]
    unanswered_questions: List[str]

class DiscussionGapResult(BaseModel):
    video_id: str
    gap_type: Literal["PRACTICAL_INSIGHT", "UNANSWERED_QUESTION", "EMOTIONAL_COMFORT", "PHILOSOPHICAL_CLARIFICATION"]
    description: str
    evidence_comment_ids: List[str] = []
    confidence: float = Field(..., ge=0.0, le=1.0)

# 4. WRITER & QUALITY SCHEMAS
CandidateStyle = Literal["REFLECTIVE", "INSIGHTFUL", "QUESTION_BASED"]

class CommentCandidate(BaseModel):
    candidate_id: str
    video_id: str
    style: CandidateStyle
    hook_angle: str
    content: str
    intended_value: str
    target_channel_ref: str = "@1995lido"

class GateResult(BaseModel):
    gate_id: str # GATE_01 to GATE_10
    gate_name: str
    passed: bool
    score: float = 1.0 # 0.0 to 1.0
    reason: str = ""

class QualityEvaluationResult(BaseModel):
    candidate_id: str
    passed_all: bool
    gate_results: List[GateResult]
    rejection_reason: Optional[str] = None
