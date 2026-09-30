"""
Test suite cho Phase 2 Upgrade:
- Channel Radar & Tiering
- Channel Intelligence 3-Layer Card
- Video Inventory Ingestion
- Video Priority Queue Ranking
- Community Intelligence Engine
- Lido Improvement Loop Engine
"""

import pytest
import os
from models import ChannelRecord, VideoMetadata, RawComment
from channel_radar import ChannelRadar, classify_tier
from channel_intelligence import ChannelIntelligenceEngine
from video_inventory import VideoInventory
from video_queue import VideoPriorityQueue
from community_intelligence import CommunityIntelligenceEngine
from lido_improvement import LidoImprovementEngine
from db_storage import init_database, get_active_channels, get_channel_intelligence, get_lido_insights_by_date

TEST_DB = "data/test_upgrade.db"

@pytest.fixture(autouse=True)
def setup_test_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_database(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_tier_classification():
    assert classify_tier(250000) == "A_MAJOR"
    assert classify_tier(80000) == "B_STRONG"
    assert classify_tier(25000) == "C_RISING"
    assert classify_tier(3000) == "D_EMERGING"

def test_channel_radar_initialization():
    radar = ChannelRadar()
    channels = radar.initialize_seeds()
    assert len(channels) >= 5
    tier_a = [ch for ch in channels if ch.tier == "A_MAJOR"]
    assert len(tier_a) >= 2

def test_channel_intelligence_3_layer_card():
    ch = ChannelRecord(
        channel_id="test_pv_01",
        channel_name="Làng Mai - Plum Village",
        language="en",
        subscriber_count=850000,
        tier="A_MAJOR",
        tradition="Thiền Làng Mai"
    )
    engine = ChannelIntelligenceEngine()
    card = engine.analyze_channel(ch)

    assert card.channel_id == "test_pv_01"
    assert len(card.content_strengths) > 0
    assert len(card.lido_learnings) > 0
    assert card.audience_engagement_level == "High"

def test_video_priority_queue():
    v1 = VideoMetadata(
        video_id="v_major_new",
        channel_id="ch_major",
        channel_name="Major Dhamma",
        title="Mindful Breathing Lecture",
        url="https://youtube.com/watch?v=v_major_new",
        view_count=50000,
        comment_count=400,
        language="en"
    )
    ch_major = ChannelRecord(
        channel_id="ch_major",
        channel_name="Major Dhamma",
        tier="A_MAJOR"
    )

    v2 = VideoMetadata(
        video_id="v_small_old",
        channel_id="ch_small",
        channel_name="Small Channel",
        title="Unclear topic",
        url="https://youtube.com/watch?v=v_small_old",
        view_count=500,
        comment_count=1,
        language="LANGUAGE_UNCERTAIN"
    )

    queue = VideoPriorityQueue()
    score_v1 = queue.calculate_priority_score(v1, ch_major)
    score_v2 = queue.calculate_priority_score(v2, None)

    assert score_v1 > score_v2
    assert score_v1 >= 80.0

def test_community_intelligence_extraction():
    engine = CommunityIntelligenceEngine()
    comments = [
        RawComment(comment_id="c1", author="An", text="Con bị trầm cảm và áp lực công việc quá nhiều, làm sao để buông bỏ ạ?"),
        RawComment(comment_id="c2", author="Bình", text="Gia đình con bất hòa, con rất khổ tâm."),
        RawComment(comment_id="c3", author="Tâm", text="Làm thế nào để giữ tâm bình yên trước thị phi?")
    ]

    report = engine.analyze_community("vid_test", "ch_test", comments)
    assert len(report.audience_pain_points) > 0
    assert any("áp lực" in p.lower() or "bất an" in p.lower() for p in report.audience_pain_points)
    assert len(report.recurring_questions) > 0

def test_lido_improvement_loop():
    engine = LidoImprovementEngine()
    ci = ChannelIntelligenceEngine()
    comm_engine = CommunityIntelligenceEngine()

    ch = ChannelRecord(
        channel_id="ch_phaphoa",
        channel_name="Pháp Âm Thầy Thích Pháp Hòa",
        tier="A_MAJOR"
    )
    card = ci.analyze_channel(ch)
    comm_rep = comm_engine.analyze_community("vid_1", "ch_phaphoa", [])

    insights = engine.synthesize_insights("2026-09-30", [card], [comm_rep])
    assert len(insights) >= 3
    assert any(i.category == "content_gap" for i in insights)
    assert any(i.category == "format_opportunity" for i in insights)

    report_path = engine.generate_lido_daily_report("2026-09-30", insights)
    assert os.path.exists(report_path)
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "@1995lido" in content
    assert "Weekly Experiments" in content
