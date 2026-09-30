"""
Bộ kiểm thử tự động toàn diện cho Phase 1 MVP:
1. Test Quality Check (Chặn quảng cáo @1995lido, chặn danh tính giả)
2. Test Duplicate Check (Chặn comment giống nhau, chặn quá tải 1 kênh trong ngày)
3. Test Database Persistence & Memory
4. Test Video Research Fallback
"""

import os
import pytest
from models import VideoMetadata, VideoResearch, CommentCandidate
from quality import validate_quality, check_duplicate
from db_storage import init_database, is_video_processed, save_video, save_comment

TEST_DB = "data/test_bce.db"

@pytest.fixture(autouse=True)
def setup_test_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_database(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_quality_blocks_self_promotion():
    """Kiểm tra Quality Gate chặn đứng từ khóa tự quảng bá kênh @1995lido"""
    research = VideoResearch(
        video_id="v1", video_summary="Tóm tắt", main_topic="An lạc"
    )
    bad_candidate = CommentCandidate(
        candidate_id="c1",
        video_id="v1",
        style="REFLECTIVE",
        content="Bài giảng hay quá, mọi người ghé qua @1995lido và subscribe kênh nhé!",
        insight_summary="Spam"
    )
    res = validate_quality(bad_candidate, research)
    assert res.passed is False
    assert "quảng bá" in res.rejection_reason

def test_quality_blocks_fake_biography():
    """Kiểm tra Quality Gate chặn đứng việc bịa đặt trải nghiệm cá nhân / danh tính giả"""
    research = VideoResearch(
        video_id="v1", video_summary="Tóm tắt", main_topic="An lạc"
    )
    bad_candidate = CommentCandidate(
        candidate_id="c2",
        video_id="v1",
        style="INSIGHTFUL",
        content="Hồi tôi đi tu 20 năm thiền định của tôi, thầy tôi luôn bảo tôi rằng...",
        insight_summary="Fake bio"
    )
    res = validate_quality(bad_candidate, research)
    assert res.passed is False
    assert "danh tính cá nhân" in res.rejection_reason

def test_quality_passes_natural_respectful_comment():
    """Kiểm tra Quality Gate cho phép bình luận chân thành, khiêm cung"""
    research = VideoResearch(
        video_id="v1", video_summary="Tóm tắt", main_topic="An lạc"
    )
    good_candidate = CommentCandidate(
        candidate_id="c3",
        video_id="v1",
        style="REFLECTIVE",
        content="Lắng nghe lời Thầy dạy mà lòng bỗng thấy nhẹ nhõm. Bớt đi một lời trách móc là thêm một phần an lạc trong tâm. Biết ơn bài pháp thoại thật nhiều.",
        insight_summary="Chân thành"
    )
    res = validate_quality(good_candidate, research)
    assert res.passed is True
    assert res.rejection_reason is None

def test_duplicate_checker_blocks_same_video():
    """Kiểm tra Database Memory chặn xử lý lại video đã có trong cơ sở dữ liệu"""
    video = VideoMetadata(
        video_id="vid_123",
        channel_name="Kênh Pháp Thoại",
        title="Thuyết pháp hay",
        url="https://youtube.com/watch?v=vid_123"
    )
    assert is_video_processed("vid_123", db_path=TEST_DB) is False
    save_video(video, db_path=TEST_DB)
    assert is_video_processed("vid_123", db_path=TEST_DB) is True
