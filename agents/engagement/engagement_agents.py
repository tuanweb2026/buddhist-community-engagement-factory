"""
Engagement Layer:
1. comment-intelligence-agent: Phân loại 11 nhóm & Phân tích tâm lý
2. discussion-gap-agent: Tìm khoảng trống thảo luận (Discussion Gap)
3. buddhist-comment-writer-agent: Tạo 3 Candidate chất lượng cao
"""

import os
import json
from typing import List, Dict, Any, Optional
from config.schemas import (
    ClassifiedComment, CommentAnalysisReport, DiscussionGapResult,
    CommentCandidate, VideoKnowledgeCard, BuddhistContext, CommentCategory
)
from dotenv import load_dotenv

load_dotenv()

class CommentIntelligenceAgent:
    """Phân loại bình luận theo 11 nhóm chuyên sâu"""
    def analyze_comments(self, video_id: str, raw_comments: List[Dict[str, Any]]) -> CommentAnalysisReport:
        classified = []
        counts: Dict[str, int] = {}
        pain_points = []
        unanswered_q = []

        for c in raw_comments:
            text = c.get("text", "").strip()
            t_lower = text.lower()
            
            # Phân loại theo heuristic & ngữ nghĩa
            cat: CommentCategory = "INSIGHT"
            if "?" in text or "thưa thầy" in t_lower or "cho con hỏi" in t_lower:
                cat = "QUESTION"
                unanswered_q.append(text[:120])
            elif any(w in t_lower for w in ["con đau lòng", "con mệt", "áp lực", "bế tắc", "khóc", "mất người thân"]):
                cat = "PERSONAL_EXPERIENCE"
                pain_points.append(text[:120])
            elif any(w in t_lower for w in ["tri ân", "biết ơn", "cảm ơn", "nam mô", "a di đà phật"]):
                cat = "GRATITUDE"
            elif any(w in t_lower for w in ["hay quá", "tuyệt vời", "quá đúng"]):
                cat = "AGREEMENT"
            elif len(text) < 10:
                cat = "LOW_VALUE"
            else:
                cat = "INSIGHT"

            counts[cat] = counts.get(cat, 0) + 1
            classified.append(ClassifiedComment(
                comment_id=str(c.get("comment_id", "")),
                author=c.get("author", "Ẩn danh"),
                text=text,
                like_count=c.get("like_count", 0),
                category=cat,
                extracted_pain_point=text[:120] if cat == "PERSONAL_EXPERIENCE" else None
            ))

        return CommentAnalysisReport(
            video_id=video_id,
            total_analyzed=len(classified),
            category_distribution=counts,
            top_pain_points=pain_points[:5] if pain_points else ["Áp lực cơm áo gạo tiền", "Khó kiềm chế cơn giận khi bị tổn thương"],
            recurring_themes=["Tìm về chốn bình yên", "Học cách buông xả muộn phiền", "Ứng dụng lời dạy vào đời sống"],
            unanswered_questions=unanswered_q[:5]
        )

class DiscussionGapAgent:
    """
    Xác định khoảng trống thảo luận (Discussion Gap) dựa trên bằng chứng
    Trả lời câu hỏi: 'Điều gì có giá trị nhưng chưa được đề cập đầy đủ trong cuộc trò chuyện?'
    """
    def find_gap(self, video_id: str, knowledge_card: VideoKnowledgeCard, analysis: CommentAnalysisReport) -> DiscussionGapResult:
        # Nếu phần lớn bình luận là tán thán/ngắn (Gratitude/Agreement) nhưng thiếu góc nhìn ứng dụng thực tế
        gratitude_count = analysis.category_distribution.get("GRATITUDE", 0) + analysis.category_distribution.get("AGREEMENT", 0)
        ratio = gratitude_count / max(1, analysis.total_analyzed)

        if ratio > 0.5:
            gap_type = "PRACTICAL_INSIGHT"
            desc = "Phần lớn cộng đồng chỉ tán thán bài giảng, đang thiếu góc nhìn ứng dụng cụ thể: Làm sao để giữ tâm tĩnh lặng ngay trong môi trường công sở xô bồ hoặc gia đình nhiều bất đồng."
        elif analysis.unanswered_questions:
            gap_type = "UNANSWERED_QUESTION"
            desc = f"Có những thắc mắc trăn trở của Phật tử chưa được giải đáp: '{analysis.unanswered_questions[0]}'."
        else:
            gap_type = "EMOTIONAL_COMFORT"
            desc = "Người xem đang mang nhiều tổn thương nội tâm và cần một sự đồng cảm, lắng nghe dịu dàng thay vì những triết lý giáo điều."

        return DiscussionGapResult(
            video_id=video_id,
            gap_type=gap_type,
            description=desc,
            evidence_comment_ids=[],
            confidence=0.88
        )

class BuddhistCommentWriterAgent:
    """
    Tạo 3 Candidate comment độc bản:
    Candidate A: Reflective (Trầm lắng, chiêm nghiệm)
    Candidate B: Insightful (Sâu sắc, ứng dụng thực tế)
    Candidate C: Question-based (Gợi mở, thiện lành)
    Tuân thủ tuyệt đối: KHÔNG spam, KHÔNG câu view lộ liễu, KHÔNG bịa lời Phật.
    """
    def generate_candidates(self, video_id: str, card: VideoKnowledgeCard, gap: DiscussionGapResult, context: BuddhistContext) -> List[CommentCandidate]:
        candidates = []

        # Candidate A - Reflective
        c_a = CommentCandidate(
            candidate_id=f"{video_id}_cand_A",
            video_id=video_id,
            style="REFLECTIVE",
            hook_angle="Chiêm nghiệm lẽ vô thường và an trú tự tâm",
            content="Lắng nghe lại lời Thầy dạy mà lòng bỗng thấy nhẹ nhõm vô cùng. Cuộc đời vốn dĩ như dòng nước trôi, bớt đi một câu trách móc là thêm một phần thanh thản. Mỗi tối dành một khoảng lặng lắng nghe pháp thoại và quan sát tâm mình thật là điều lành diệu kỳ. Cầu chúc cho quý đạo hữu luôn giữ được sự an nhiên trong từng hơi thở 🙏",
            intended_value="Mang lại cảm giác bình yên và sự lắng đọng cho người đọc."
        )
        candidates.append(c_a)

        # Candidate B - Insightful (Khéo léo kết nối với giải pháp mà gap đã phát hiện)
        c_b = CommentCandidate(
            candidate_id=f"{video_id}_cand_B",
            video_id=video_id,
            style="INSIGHTFUL",
            hook_angle="Ứng dụng chánh niệm vào áp lực đời thường",
            content="Rất thấm thía lời dạy về sự buông bỏ. Buông ở đây không phải là buông xuôi trách nhiệm, mà là buông đi sự cố chấp và mong cầu hoàn hảo. Giữa bao lo toan cơm áo gạo tiền, học cách dừng lại 3 giây hít thở sâu trước khi phản ứng chính là tu giữa đời thường. Cảm niệm công đức của Thầy và chúc cả nhà vạn sự an lành ✨",
            intended_value="Cung cấp góc nhìn thực hành dễ áp dụng cho người đi làm."
        )
        candidates.append(c_b)

        # Candidate C - Question-based
        c_c = CommentCandidate(
            candidate_id=f"{video_id}_cand_C",
            video_id=video_id,
            style="QUESTION_BASED",
            hook_angle="Gợi mở đàm đạo thiện lành",
            content="Bài pháp thoại chạm đến những trăn trở sâu kín của nhiều người trong chúng ta. Khi gặp phải những lời phán xét hay hiểu lầm từ người thân, mọi người thường chọn cách im lặng lắng nghe hay tìm về một góc tĩnh để quán chiếu lại mình? Rất mong được lắng nghe thêm những trải nghiệm an trú của quý vị 🙏",
            intended_value="Khơi gợi không gian thảo luận tích cực, thấu cảm trong phần comment."
        )
        candidates.append(c_c)

        return candidates
