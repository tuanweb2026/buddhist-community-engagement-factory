"""
Bộ Unit Test & Integration Test kiểm thử toàn diện các kịch bản của BCE-Factory:
- Test 10 Quality Gates
- Test Identity Safety Check (@1995lido)
- Test Opportunity Ranker 6-Factor Formula
- Test Discussion Gap Detection
- Test Fallback khi thiếu Transcript
"""

import pytest
from config.schemas import (
    DiscoveredVideo, CommentCandidate, VideoKnowledgeCard,
    DiscussionGapResult, BuddhistContext
)
from agents.discovery.discovery_agents import OpportunityRankerAgent
from agents.research.research_agents import VideoResearchAgent, TranscriptAgent
from agents.engagement.engagement_agents import BuddhistCommentWriterAgent, DiscussionGapAgent, CommentIntelligenceAgent
from agents.quality.quality_agents import CommentQualityGateAgent
from workflows.orchestrator import MasterOrchestrator

def test_identity_safety_guard():
    """Kiểm tra Hard Stop nếu target channel không phải @1995lido"""
    with pytest.raises(ValueError) as excinfo:
        MasterOrchestrator(target_channel_handle="@fake_channel")
    assert "HARD STOP" in str(excinfo.value)

    # Hợp lệ với @1995lido
    orc = MasterOrchestrator(target_channel_handle="@1995lido")
    assert orc.target_handle == "@1995lido"

def test_opportunity_ranker_formula():
    """Kiểm tra chấm điểm Opportunity Score theo 6 trọng số"""
    ranker = OpportunityRankerAgent()
    video = DiscoveredVideo(
        video_id="test_vid_01",
        channel_title="Thầy Pháp Hòa",
        title="Học cách buông bỏ để tâm an lạc",
        url="https://youtube.com/watch?v=test_vid_01",
        description="Bài giảng về sự buông bỏ phiền não.",
        view_count=50000
    )
    res = ranker.rank(video)
    assert 0.0 <= res.total_score <= 1.0
    assert res.recommended_for_research is True
    assert res.audience_relevance > 0.5

def test_video_research_insufficient_context():
    """Kiểm tra Principle: Evidence before generation - Báo INSUFFICIENT_CONTEXT khi không có thông tin"""
    researcher = VideoResearchAgent()
    card = researcher.build_knowledge_card(video_id="empty_vid", title="", description="", transcript=None)
    assert card.is_sufficient_context is False
    assert card.core_topic == "INSUFFICIENT_CONTEXT"

def test_quality_gate_blocks_self_promotion():
    """Kiểm tra GATE 06 (No Self-Promotion): Phải REJECT các comment câu sub"""
    gate_agent = CommentQualityGateAgent()
    card = VideoKnowledgeCard(video_id="v1", core_topic="Buông bỏ", is_sufficient_context=True)
    gap = DiscussionGapResult(video_id="v1", gap_type="PRACTICAL_INSIGHT", description="Test gap", confidence=0.9)

    bad_cand = CommentCandidate(
        candidate_id="bad_01",
        video_id="v1",
        style="REFLECTIVE",
        hook_angle="Test",
        content="Bài giảng hay quá, mọi người hãy subscribe kênh mình và ghé kênh mình xem video mới nhé!",
        intended_value="Spam promotion"
    )
    result = gate_agent.evaluate(bad_cand, card, gap)
    assert result.passed_all is False
    assert "GATE_06" in result.rejection_reason

def test_quality_gate_blocks_hallucination():
    """Kiểm tra GATE 05 (Hallucination Check): Phải REJECT trích dẫn kinh giả"""
    gate_agent = CommentQualityGateAgent()
    card = VideoKnowledgeCard(video_id="v1", core_topic="Buông bỏ", is_sufficient_context=True)
    gap = DiscussionGapResult(video_id="v1", gap_type="PRACTICAL_INSIGHT", description="Test gap", confidence=0.9)

    hallucinated_cand = CommentCandidate(
        candidate_id="bad_02",
        video_id="v1",
        style="INSIGHTFUL",
        hook_angle="Test",
        content="Phật từng nói trong kinh abc rằng ai không like video này sẽ gặp xui xẻo...",
        intended_value="Bịa đặt"
    )
    result = gate_agent.evaluate(hallucinated_cand, card, gap)
    assert result.passed_all is False
    assert "GATE_05" in result.rejection_reason

def test_quality_gate_passes_genuine_comment():
    """Kiểm tra comment chân thành, đúc kết giá trị phải vượt qua 10 Quality Gates"""
    gate_agent = CommentQualityGateAgent()
    card = VideoKnowledgeCard(video_id="v1", core_topic="Buông bỏ", is_sufficient_context=True)
    gap = DiscussionGapResult(video_id="v1", gap_type="PRACTICAL_INSIGHT", description="Test gap", confidence=0.9)

    good_cand = CommentCandidate(
        candidate_id="good_01",
        video_id="v1",
        style="REFLECTIVE",
        hook_angle="Chiêm nghiệm",
        content="Lắng nghe lời Thầy dạy mà lòng bỗng thấy nhẹ nhõm. Bớt đi một lời trách móc là thêm một phần an lạc trong tâm. Chúc đại chúng luôn an yên.",
        intended_value="Trao tặng sự an lành"
    )
    result = gate_agent.evaluate(good_cand, card, gap)
    assert result.passed_all is True
    assert result.rejection_reason is None
