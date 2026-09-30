"""
Quality & Duplicate Check Module (Phase 2):
1. Duplicate Protection:
   - Video duplicate (Skip if commented)
   - Exact duplicate (Reject)
   - Semantic / Near duplicate (Similarity > 0.82)
   - Same channel frequency limit (Max 1-2 comments/day/channel)
2. Quality Check:
   - Relevance, Context, Originality, Value
   - No Promotion (@1995lido, subscribe, links)
   - No Fabrication / No Fake Personal Experience ("When I was a monk...")
   - Natural Language, Buddhist Respect
"""

import re
from typing import Tuple
from difflib import SequenceMatcher
from models import CommentCandidate, VideoResearch, QualityResult
from db_storage import get_all_past_comments, get_channel_published_count_today

def check_duplicate(candidate: CommentCandidate, channel_id: str, date_str: str) -> Tuple[bool, str]:
    # 1. Same channel frequency limit (Không comment quá 1-2 video của cùng 1 kênh trong ngày)
    if channel_id:
        count_today = get_channel_published_count_today(channel_id, date_str)
        if count_today >= 2:
            return True, f"Kênh {channel_id} đã có {count_today} bình luận trong ngày hôm nay."

    # 2. Text similarity với các comment trong lịch sử
    past_comments = get_all_past_comments()
    cand_clean = candidate.content.strip().lower()

    for past in past_comments:
        past_clean = past.strip().lower()
        if cand_clean == past_clean:
            return True, "Trùng lặp 100% với một comment đã tồn tại trong lịch sử."
        
        ratio = SequenceMatcher(None, cand_clean, past_clean).ratio()
        if ratio > 0.82:
            return True, f"Độ tương đồng quá cao ({ratio:.2f}) với comment cũ."

    return False, ""

def validate_quality(candidate: CommentCandidate, research: VideoResearch) -> QualityResult:
    text = candidate.content
    text_lower = text.lower()

    # 1. NO PROMOTION CHECK (CRITICAL)
    promo_keywords = [
        "@1995lido", "subscribe", "đăng ký kênh", "ghé kênh", "qua kênh", "xem kênh",
        "kênh của mình", "kênh tôi", "my channel", "check my channel", "visit my channel",
        "my video", "link", "http", ".com"
    ]
    if any(k in text_lower for k in promo_keywords):
        return QualityResult(passed=False, rejection_reason="Chứa từ khóa quảng bá kênh hoặc đường dẫn liên kết.")

    # 2. NO FABRICATION / FAKE PERSONAL EXPERIENCE (CRITICAL)
    fake_identity_keywords = [
        "hồi tôi đi tu", "khi tôi còn là nhà sư", "suốt 20 năm thiền định của tôi",
        "thầy tôi luôn bảo tôi rằng", "tôi từng chứng đắc",
        "when i was a monk", "in my 20 years of meditation", "my teacher always told me"
    ]
    if any(k in text_lower for k in fake_identity_keywords):
        return QualityResult(passed=False, rejection_reason="Bịa đặt danh tính cá nhân / trải nghiệm tu tập giả.")

    # 3. RELEVANCE & LENGTH CHECK
    if len(text.strip()) < 35:
        return QualityResult(passed=False, rejection_reason="Bình luận quá ngắn, thiếu chiều sâu.")

    # 4. BUDDHIST RESPECT & SENSITIVITY
    disrespect_keywords = ["mê tín", "tà đạo", "sai bét", "nhảm nhí", "cult", "fake guru"]
    for k in disrespect_keywords:
        if re.search(r'\b' + re.escape(k) + r'\b', text_lower):
            return QualityResult(passed=False, rejection_reason="Vi phạm văn phong tôn trọng đạo Phật.")

    # 5. NATURAL LANGUAGE (Không rập khuôn máy móc)
    cliche_openings = ["beautiful video...", "amazing...", "thank you...", "this is so profound..."]
    if any(text_lower.startswith(c) for c in cliche_openings) or text.endswith("🙏🙏🙏"):
        return QualityResult(passed=False, rejection_reason="Văn mẫu rập khuôn / spam emoji.")

    # 6. EVIDENCE & CONTEXT GROUNDING CHECK (Phase 2.5 Requirement)
    # Bình luận phải gắn liền với ít nhất 1 điểm chứng cứ hoặc chủ đề cốt lõi từ video research
    if hasattr(candidate, 'evidence_points') and candidate.evidence_points:
        has_evidence_match = True
    elif hasattr(research, 'evidence_points') and research.evidence_points:
        # Kiểm tra xem từ khóa chứng cứ hoặc chủ đề có xuất hiện/liên quan trong bình luận không
        research_terms = [t.lower() for t in research.evidence_points] + [research.main_topic.lower()]
        has_evidence_match = any(any(w in text_lower for w in term.split() if len(w) > 3) for term in research_terms)
    else:
        has_evidence_match = True

    if not has_evidence_match:
        return QualityResult(passed=False, rejection_reason="Bình luận không liên kết được với bất kỳ bằng chứng (evidence point) nào của video.")

    return QualityResult(passed=True)

def check_diversity_against_batch(
    candidate: CommentCandidate,
    selected_batch: list,
    opening_counter: dict = None,
    closing_counter: dict = None,
    max_opening_repeat: int = 1
) -> Tuple[bool, str]:
    """
    Kiểm tra tính đa dạng ngữ nghĩa, mở đầu và kết bài trong cùng một phiên xử lý
    """
    cand_text = candidate.content.strip()
    cand_lower = cand_text.lower()
    sentences = [s.strip() for s in re.split(r'[.!?]', cand_text) if s.strip()]
    cand_opening = sentences[0].lower() if sentences else ""
    cand_closing = sentences[-1].lower() if sentences else ""

    # 1. Kiểm tra lặp opening trong phiên
    if opening_counter is not None and cand_opening:
        if opening_counter.get(cand_opening, 0) >= max_opening_repeat:
            return True, f"Cấu trúc mở đầu bị lặp lại ('{cand_opening[:40]}...')."

    # 2. Kiểm tra lặp closing trong phiên
    if closing_counter is not None and cand_closing:
        if closing_counter.get(cand_closing, 0) >= max_opening_repeat:
            return True, f"Cấu trúc kết bài bị lặp lại ('{cand_closing[:40]}...')."

    # 3. Kiểm tra semantic similarity với các comment đã được chọn trong batch
    for sel in selected_batch:
        sel_text = sel.content.strip().lower()
        if cand_lower == sel_text:
            return True, "Trùng lặp 100% với một bình luận vừa được chọn trong phiên."
        ratio = SequenceMatcher(None, cand_lower, sel_text).ratio()
        if ratio > 0.70:
            return True, f"Độ tương đồng ngữ nghĩa quá cao ({ratio:.2f}) với bình luận khác trong phiên."

    return False, ""

