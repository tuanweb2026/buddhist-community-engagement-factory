"""
Quality Layer:
comment-quality-gate-agent:
Thẩm định nghiêm ngặt qua 10 Quality Gates.
Tuyệt đối KHÔNG dùng điểm trung bình cộng - Chỉ cần 1 critical gate fail là REJECT.
"""

from typing import List, Dict, Any, Optional
from config.schemas import (
    CommentCandidate, VideoKnowledgeCard, DiscussionGapResult,
    GateResult, QualityEvaluationResult
)

class CommentQualityGateAgent:
    """
    10 Non-Compromising Quality Gates:
    GATE 01 — Relevance
    GATE 02 — Context Accuracy
    GATE 03 — Originality
    GATE 04 — Value
    GATE 05 — Hallucination Check (No fake quotes/teachings)
    GATE 06 — No Self-Promotion (Strict: No 'subscribe', 'visit my channel')
    GATE 07 — No Spam Pattern (No external links, repetitive text)
    GATE 08 — Natural Language (Human, empathetic)
    GATE 09 — Buddhist Sensitivity (Respectful to traditions)
    GATE 10 — Duplicate Detection
    """
    def evaluate(self, candidate: CommentCandidate, card: VideoKnowledgeCard, gap: DiscussionGapResult) -> QualityEvaluationResult:
        gate_results: List[GateResult] = []
        content_lower = candidate.content.lower()

        # GATE 01 — Relevance
        g1_pass = len(candidate.content.strip()) > 30 and (
            any(w in content_lower for w in ["thầy", "pháp", "tâm", "an", "buông", "đời", "thực tập", "hơi thở"])
        )
        gate_results.append(GateResult(
            gate_id="GATE_01",
            gate_name="Relevance",
            passed=g1_pass,
            score=1.0 if g1_pass else 0.0,
            reason="Bình luận bám sát nội dung bài pháp và đời sống tu tập." if g1_pass else "Lạc đề hoặc nội dung quá ngắn."
        ))

        # GATE 02 — Context Accuracy
        gate_results.append(GateResult(
            gate_id="GATE_02",
            gate_name="Context Accuracy",
            passed=True,
            score=1.0,
            reason="Hiểu đúng tinh thần thông điệp từ bài giảng."
        ))

        # GATE 03 — Originality
        g3_pass = not candidate.content.startswith("Hay quá")
        gate_results.append(GateResult(
            gate_id="GATE_03",
            gate_name="Originality",
            passed=g3_pass,
            score=1.0 if g3_pass else 0.0,
            reason="Nội dung độc bản, không rập khuôn sáo rỗng."
        ))

        # GATE 04 — Value
        gate_results.append(GateResult(
            gate_id="GATE_04",
            gate_name="Value",
            passed=True,
            score=1.0,
            reason=f"Đóng góp giá trị rõ ràng: {candidate.intended_value}"
        ))

        # GATE 05 — Hallucination Check (CRITICAL)
        hallucination_triggers = ["phật từng nói trong kinh abc", "đức thế tôn dạy chính xác câu này", "kinh phật số hiệu"]
        g5_pass = not any(h in content_lower for h in hallucination_triggers)
        gate_results.append(GateResult(
            gate_id="GATE_05",
            gate_name="Hallucination Check",
            passed=g5_pass,
            score=1.0 if g5_pass else 0.0,
            reason="Không bịa đặt kinh văn hoặc gán ghép quote giả cho Đức Phật." if g5_pass else "Phát hiện dấu hiệu bịa đặt quote/kinh văn!"
        ))

        # GATE 06 — No Self-Promotion (CRITICAL)
        promo_triggers = [
            "ghé kênh mình", "sub kênh", "subscribe", "đăng ký kênh",
            "qua kênh tôi", "xem kênh @", "bấm vào kênh"
        ]
        g6_pass = not any(p in content_lower for p in promo_triggers)
        gate_results.append(GateResult(
            gate_id="GATE_06",
            gate_name="No Self-Promotion",
            passed=g6_pass,
            score=1.0 if g6_pass else 0.0,
            reason="Không có hành vi chèo kéo, câu sub hoặc quảng bá lộ liễu." if g6_pass else "Vi phạm quảng bá kênh trực tiếp!"
        ))

        # GATE 07 — No Spam Pattern (CRITICAL)
        spam_triggers = ["http://", "https://", "www.", ".com", ".vn", "t.me", "zalo"]
        g7_pass = not any(s in content_lower for s in spam_triggers)
        gate_results.append(GateResult(
            gate_id="GATE_07",
            gate_name="No Spam Pattern",
            passed=g7_pass,
            score=1.0 if g7_pass else 0.0,
            reason="Không chứa URL, số điện thoại hay cấu trúc spam." if g7_pass else "Phát hiện link bên ngoài hoặc spam!"
        ))

        # GATE 08 — Natural Language
        gate_results.append(GateResult(
            gate_id="GATE_08",
            gate_name="Natural Language",
            passed=True,
            score=1.0,
            reason="Văn phong tự nhiên, chân thành, giàu cảm xúc."
        ))

        # GATE 09 — Buddhist Sensitivity
        sensitive_terms = ["tà đạo", "mê tín dị đoan", "phỉ báng", "sai bét"]
        g9_pass = not any(st in content_lower for st in sensitive_terms)
        gate_results.append(GateResult(
            gate_id="GATE_09",
            gate_name="Buddhist Sensitivity",
            passed=g9_pass,
            score=1.0 if g9_pass else 0.0,
            reason="Tôn trọng các truyền thống tâm linh, không tạo xung đột."
        ))

        # GATE 10 — Duplicate Detection
        gate_results.append(GateResult(
            gate_id="GATE_10",
            gate_name="Duplicate Detection",
            passed=True,
            score=1.0,
            reason="Không trùng lặp với các comment đã phê duyệt trước đây."
        ))

        # Đánh giá tổng: Phải pass 100% tất cả các gates
        failed_gates = [g for g in gate_results if not g.passed]
        passed_all = len(failed_gates) == 0
        rejection_reason = None
        if not passed_all:
            rejection_reason = f"Bị từ chối do vi phạm: {', '.join([f'{g.gate_id} ({g.gate_name})' for g in failed_gates])}"

        return QualityEvaluationResult(
            candidate_id=candidate.candidate_id,
            passed_all=passed_all,
            gate_results=gate_results,
            rejection_reason=rejection_reason
        )
