"""
Community Intelligence Module:
Phân tích sâu cảm xúc, nỗi đau (pain points), nhu cầu cốt lõi và câu hỏi lặp đi lặp lại của cộng đồng người xem:
- Audience Pain Points: Bế tắc tâm lý, gia đình bất hòa, mất định hướng, áp lực công việc
- Core Needs: Cần sự lắng nghe, hướng dẫn thực hành thiền cụ thể, giải thích dễ hiểu
- Desired Emotions: An yên, nhẹ nhõm, buông xả, thấu suốt
"""

import re
from typing import List, Dict, Any
from models import RawComment, CommunityIntelligenceReport

class CommunityIntelligenceEngine:
    def analyze_community(self, video_id: str, channel_id: str = None, comments: List[RawComment] = None) -> CommunityIntelligenceReport:
        comments = comments or []
        all_text = " ".join([c.text.lower() for c in comments])

        pain_points = []
        core_needs = []
        desired_emotions = []
        recurring_questions = []

        # Phát hiện nỗi đau (pain points)
        if any(w in all_text for w in ["khổ", "buồn", "đau", "áp lực", "stress", "mệt mỏi", "suffer", "anxiety", "pain"]):
            pain_points.append("Tâm trạng bất an, chịu nhiều áp lực và căng thẳng trong cuộc sống hiện đại")
        if any(w in all_text for w in ["chồng", "vợ", "con", "gia đình", "mẹ", "cha", "family", "parent"]):
            pain_points.append("Mâu thuẫn và vướng mắc trong mối quan hệ gia đình, khó tìm tiếng nói chung")
        if any(w in all_text for w in ["nghiệp", "tội", "sợ", "lo", "fear", "karma"]):
            pain_points.append("Nỗi hoang mang, sợ hãi trước nhân quả và sự biến động khó lường của số phận")

        if not pain_points:
            pain_points.append("Mong muốn tìm chốn bình yên nội tâm giữa xô bồ thường nhật")

        # Nhu cầu cốt lõi (Core Needs)
        if any(w in all_text for w in ["làm sao", "cách nào", "thế nào", "hướng dẫn", "how to", "practice"]):
            core_needs.append("Phương pháp thực hành cụ thể, dễ áp dụng vào từng hoàn cảnh sống thực tế")
        if any(w in all_text for w in ["nghe", "hiểu", "thương", "giúp", "help", "compassion"]):
            core_needs.append("Sự thấu cảm, không phán xét và được đồng hành lắng nghe")
        if not core_needs:
            core_needs.append("Lời chỉ dẫn trí tuệ giúp nhìn nhận vấn đề sáng rõ hơn")

        # Cảm xúc khao khát (Desired Emotions)
        desired_emotions = ["An yên nội tại", "Buông xả phiền não", "Thấu suốt chánh niệm"]

        # Câu hỏi lặp lại
        for c in comments:
            t = c.text.strip()
            if "?" in t or any(q in t.lower() for q in ["làm sao", "tại sao", "như thế nào", "how", "why"]):
                if len(t) < 150:
                    recurring_questions.append(t)
            if len(recurring_questions) >= 3:
                break

        if not recurring_questions:
            recurring_questions = ["Làm thế nào để giữ tâm không xao động khi đối diện nghịch cảnh?"]

        return CommunityIntelligenceReport(
            video_id=video_id,
            channel_id=channel_id,
            audience_pain_points=pain_points,
            core_needs=core_needs,
            desired_emotions=desired_emotions,
            recurring_questions=recurring_questions,
            sentiment_distribution={"peaceful": 0.65, "questioning": 0.25, "seeking_help": 0.10}
        )
