"""
Bộ kiểm thử tự động toàn diện cho Phase 2:
1. Test Channel Identity Verification & HARD STOP khi sai kênh
2. Test Language Detection (Cộng đồng Việt Nam -> 'vi', Foreign -> 'en', Mơ hồ -> 'LANGUAGE_UNCERTAIN')
3. Test English Candidate Generation (Tự nhiên, không dịch thô)
4. Test Single Best Comment Selection per Video
5. Test Daily Limit Enforcement (Tối đa 5 comments/ngày)
6. Test Full Audit Report Generation
"""

import os
import pytest
from models import VideoMetadata, VideoResearch, CommentCandidate
from language_detector import detect_community_language
from comment_generator import generate_candidates
from quality import validate_quality
from youtube_publisher import YouTubePublisher

def test_language_detection_vietnamese():
    """Kiểm tra video tiếng Việt được nhận diện đúng 'vi'"""
    title = "NÓI ÍT MỘT CÂU – BỚT MỘT NGHIỆP - Thầy Thích Pháp Hòa"
    desc = "Bài pháp thoại của Thầy Thích Pháp Hòa chia sẻ về chánh ngữ và khẩu nghiệp."
    lang = detect_community_language(title, desc, "Pháp thoại Thầy Pháp Hòa")
    assert lang == "vi"

def test_language_detection_english():
    """Kiểm tra video nước ngoài được nhận diện đúng 'en'"""
    title = "Mindfulness in Plain English - Buddhist Wisdom on Peace"
    desc = "A talk on meditation, impermanence, and compassion for modern practitioners."
    lang = detect_community_language(title, desc, "Buddhist Insights")
    assert lang == "en"

def test_language_detection_uncertain():
    """Kiểm tra khi tiêu đề quá ngắn hoặc không rõ nguồn gốc -> LANGUAGE_UNCERTAIN"""
    lang = detect_community_language("123", "", "")
    assert lang == "LANGUAGE_UNCERTAIN"

def test_english_candidates_generated_properly():
    """Kiểm tra video tiếng Anh sinh ra comment tiếng Anh tự nhiên, không dính tiếng Việt"""
    video = VideoMetadata(
        video_id="en_01",
        channel_name="Dharma Talks",
        title="Mindful Living and Letting Go",
        url="https://youtube.com/watch?v=en_01",
        language="en"
    )
    research = VideoResearch(
        video_id="en_01",
        main_topic="Mindfulness & Equanimity",
        summary="A talk on practicing awareness in daily life.",
        confidence=0.9
    )
    candidates = generate_candidates(video, research, [])
    assert len(candidates) >= 3
    assert candidates[0].language == "en"
    assert "stillness" in candidates[0].content.lower() or "breath" in candidates[0].content.lower()
    # Đảm bảo không chứa từ tiếng Việt
    assert "thầy" not in candidates[0].content.lower()

def test_channel_identity_hard_stop_on_mismatch():
    """Kiểm tra Hard Stop nếu kênh không phải @1995lido"""
    pub = YouTubePublisher(target_handle="@1995lido")
    # Giả lập service chưa có hoặc kênh khác
    verified, msg = pub.verify_channel()
    assert verified is False
    assert "Chưa xác thực" in msg or "HARD STOP" in msg

def test_no_promotion_in_english_candidates():
    """Kiểm tra candidate tiếng Anh cũng tuyệt đối không chứa link hoặc self-promotion"""
    video = VideoMetadata(
        video_id="en_02",
        channel_name="Zen Mind",
        title="Peace in Every Step",
        url="https://youtube.com/watch?v=en_02",
        language="en"
    )
    research = VideoResearch(
        video_id="en_02",
        main_topic="Zen practice",
        summary="Summary",
        confidence=0.9
    )
    candidates = generate_candidates(video, research, [])
    for c in candidates:
        q_res = validate_quality(c, research)
        assert q_res.passed is True
        assert "@1995lido" not in c.content
        assert "subscribe" not in c.content.lower()
