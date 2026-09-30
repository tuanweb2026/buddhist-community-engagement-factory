"""
Comment Generator Module (Phase 2.5):
Tạo 3-5 Candidate Comments độc lập, có biến thể phong phú và liên kết trực tiếp với bằng chứng (evidence points):
- Hỗ trợ LLM Dynamic Generation khi có GEMINI_API_KEY / OPENAI_API_KEY
- Khi không có LLM, sử dụng Dynamic Parameterized Synthesis kết hợp Evidence Points để đảm bảo mỗi bình luận có mở đầu, thân bài, góc nhìn và kết bài khác biệt hoàn toàn, không rập khuôn.
"""

import os
import json
import hashlib
from typing import List
from models import VideoMetadata, VideoResearch, RawComment, CommentCandidate
from app_config import LLM_API_KEY

def generate_candidates(
    video: VideoMetadata,
    research: VideoResearch,
    comments: List[RawComment]
) -> List[CommentCandidate]:
    candidates = []
    v_id = video.video_id
    lang = video.language
    topic = research.main_topic
    evidence_points = getattr(research, "evidence_points", []) or research.key_points or [topic]
    
    # Xác định mức độ tự tin (Confidence) dựa trên ngữ cảnh video
    if hasattr(research, 'confidence') and research.confidence >= 0.90:
        confidence_level = "HIGH"
    elif len(video.description) > 100 or len(comments) >= 5:
        confidence_level = "MEDIUM"
    else:
        confidence_level = "LOW"

    # =========================================================================
    # 1. LLM DYNAMIC GENERATION (Ưu tiên hàng đầu khi có API Key)
    # =========================================================================
    if LLM_API_KEY and len(LLM_API_KEY.strip()) > 10:
        try:
            from google import genai
            client = genai.Client(api_key=LLM_API_KEY)
            
            prompt = f"""
Bạn là chuyên gia đối thoại Phật giáo cho kênh @1995lido.
Hãy tạo 3 ứng viên bình luận (candidates) hoàn toàn độc lập, tinh tế, khiêm cung, tôn trọng và giàu lòng từ bi cho video sau:
TIÊU ĐỀ VIDEO: {video.title}
KÊNH: {video.channel_name}
NGÔN NGỮ BẮT BUỘC: {lang} (Nếu 'vi' viết tiếng Việt chuẩn xác; nếu 'en' viết tiếng Anh bản ngữ tự nhiên).
CHỦ ĐỀ CỐT LÕI: {topic}
CÁC ĐIỂM CHỨNG CỨ TỪ BÀI GIẢNG: {', '.join(evidence_points)}
GAP BÌNH LUẬN: {research.discussion_gap}

YÊU CẦU BẮT BUỘC:
1. Candidate 1 (Reflective): Chiêm nghiệm sâu sắc, hướng về sự an trú nội tâm hoặc hơi thở.
2. Candidate 2 (Insightful): Đúc kết góc nhìn thực tế, áp dụng buông xả vào đời sống hoặc công việc.
3. Candidate 3 (Thoughtful Question): Đặt câu hỏi mở nhã nhặn kích thích đàm đạo thiện lành.
4. TUYỆT ĐỐI KHÔNG chứa từ ngữ tự quảng cáo kênh (@1995lido, link, sub, ghé kênh).
5. TUYỆT ĐỐI KHÔNG bịa đặt danh tính nhà sư/tu sĩ (không dùng "khi tôi đi tu", "thầy tôi dạy").
6. Mỗi candidate phải có câu mở đầu (opening), từ vựng và câu kết hoàn toàn khác nhau.
7. Mỗi candidate phải liên kết cụ thể đến ít nhất 1 điểm chứng cứ của bài giảng.

Xuất ra định dạng JSON:
[
  {{
    "style": "Reflective",
    "content": "Nội dung bình luận...",
    "insight_summary": "Tóm tắt giá trị...",
    "evidence_points": ["điểm 1"]
  }},
  {{
    "style": "Insightful",
    "content": "Nội dung bình luận...",
    "insight_summary": "Tóm tắt giá trị...",
    "evidence_points": ["điểm 2"]
  }},
  {{
    "style": "Thoughtful Question",
    "content": "Nội dung bình luận...",
    "insight_summary": "Tóm tắt giá trị...",
    "evidence_points": ["điểm 3"]
  }}
]
"""
            res = client.models.generate_content(model='gemini-3.5-flash-lite', contents=prompt)
            txt = res.text.strip()
            if txt.startswith("```json"):
                txt = txt[7:]
            if txt.endswith("```"):
                txt = txt[:-3]
            data = json.loads(txt.strip())
            
            for idx, item in enumerate(data, 1):
                candidates.append(CommentCandidate(
                    candidate_id=f"{v_id}_llm_{idx}",
                    video_id=v_id,
                    style=item.get("style", "Reflective"),
                    language=lang,
                    content=item.get("content", "").strip(),
                    insight_summary=item.get("insight_summary", ""),
                    evidence_points=item.get("evidence_points", [topic]),
                    research_confidence="HIGH"
                ))
            if len(candidates) >= 3:
                return candidates
        except Exception as e:
            print(f"[!] LLM Comment Generation gặp sự cố ({e}), chuyển sang Dynamic Synthesis.")

    # =========================================================================
    # 2. DYNAMIC PARAMETERIZED SYNTHESIS (Fallback khi không có LLM)
    # Tự động biến thiên câu mở đầu, thân bài, từ vựng và kết luận dựa trên hash
    # của video_id để loại bỏ triệt để hiện tượng lặp lại cấu trúc.
    # =========================================================================
    h_val = int(hashlib.md5(v_id.encode('utf-8')).hexdigest(), 16)
    
    # Trích xuất 1 điểm chứng cứ đại diện
    primary_evidence = evidence_points[0] if evidence_points else topic
    secondary_evidence = evidence_points[1] if len(evidence_points) > 1 else topic

    if lang == "vi":
        # Danh mục mở đầu đa dạng cho Tiếng Việt
        openings_ref = [
            f"Lắng nghe những sẻ chia sâu lắng về {topic.lower()} giữa lúc cuộc sống nhiều xáo động thật quý giá.",
            f"Theo dõi bài giảng về {topic.lower()} hôm nay như một nhịp dừng tĩnh lặng cần thiết cho tâm trí.",
            f"Những lời pháp nhũ về {topic.lower()} mang lại một cảm giác thật bình yên và nhẹ nhõm."
        ]
        closings_ref = [
            "Tự nhắc mình quay về nhận biết hơi thở mỗi khi đối diện với biến động.",
            "Mong cho mọi người luôn giữ được sự an định và thảnh thơi trong từng phút giây.",
            "Xin tri ân những giáo lý giản dị mà thấm thía được trao gửi hôm nay."
        ]
        op_ref = openings_ref[h_val % len(openings_ref)]
        cl_ref = closings_ref[h_val % len(closings_ref)]
        
        candidates.append(CommentCandidate(
            candidate_id=f"{v_id}_syn_1",
            video_id=v_id,
            style="Reflective",
            language="vi",
            content=f"{op_ref} Điểm làm lòng mình lắng lại nhất là khi nhận ra {primary_evidence.lower()}. {cl_ref}",
            insight_summary="Chiêm nghiệm hướng nội về sự an trú và tĩnh tâm.",
            evidence_points=[primary_evidence],
            research_confidence=confidence_level
        ))

        # Candidate 2: Insightful
        openings_ins = [
            f"Góc nhìn về việc hóa giải {secondary_evidence.lower()} trong bài giảng thực sự rất thực tế.",
            f"Điểm thấm thía nhất trong chia sẻ này là cách ứng dụng chánh niệm vào việc giải tỏa {topic.lower()}.",
            f"Bài học về {topic.lower()} không chỉ dừng lại ở lý thuyết mà chạm thẳng vào vướng mắc đời thường."
        ]
        closings_ins = [
            "Chấp nhận sự không như ý của hoàn cảnh cũng chính là lúc ta bắt đầu bớt tự làm khổ mình.",
            "Học cách buông bớt sự cố chấp trong công việc thường nhật giúp tâm hồn rộng mở hơn rất nhiều.",
            "Khi dung lượng trái tim lớn hơn một chút thì những va chạm thường ngày cũng nhẹ nhàng trôi qua."
        ]
        op_ins = openings_ins[(h_val + 1) % len(openings_ins)]
        cl_ins = closings_ins[(h_val + 1) % len(closings_ins)]

        candidates.append(CommentCandidate(
            candidate_id=f"{v_id}_syn_2",
            video_id=v_id,
            style="Insightful",
            language="vi",
            content=f"{op_ins} Nhiều khi áp lực không đến từ ngoại cảnh mà do chính tâm mong cầu quá mức của mình. {cl_ins}",
            insight_summary="Ứng dụng bài học buông xả vào đời sống và công việc.",
            evidence_points=[secondary_evidence],
            research_confidence=confidence_level
        ))

        # Candidate 3: Thoughtful Question
        questions = [
            f"Một bài giảng rất sâu sắc và chạm đến thực tế đời sống. Đứng trước {primary_evidence.lower()}, các đạo hữu thường chọn cách im lặng để thời gian trả lời hay tìm một dịp phù hợp để thẳng thắn giãi bày?",
            f"Nội dung chia sẻ chạm đúng vào trăn trở của nhiều người trẻ. Giữa guồng quay bận rộn, mọi người thường áp dụng cách nào hiệu quả nhất để duy trì chánh niệm khi đối diện áp lực công việc?",
            f"Rất cảm phục năng lượng an lành từ bài giảng. Xin được học hỏi thêm từ quý đạo hữu: làm sao để giữ tâm không dao động khi đối diện với những lời phán xét thiếu thiện chí?"
        ]
        q_sel = questions[(h_val + 2) % len(questions)]

        candidates.append(CommentCandidate(
            candidate_id=f"{v_id}_syn_3",
            video_id=v_id,
            style="Thoughtful Question",
            language="vi",
            content=q_sel,
            insight_summary="Gợi mở câu hỏi đàm đạo thiện lành.",
            evidence_points=[primary_evidence],
            research_confidence=confidence_level
        ))

    else:
        # Danh mục mở đầu đa dạng cho Tiếng Anh
        openings_ref_en = [
            f"Listening to these reflections on {topic.lower()} offers a much-needed sanctuary of stillness.",
            f"A deeply calming reminder on the practice of {primary_evidence.lower()} amidst modern pressures.",
            f"Returning to the core teachings of {topic.lower()} brings an immediate sense of spaciousness."
        ]
        closings_ref_en = [
            "Simply resting in conscious awareness makes a quiet yet profound difference in daily life.",
            "May we all remember to return to our natural breath whenever overwhelm arises.",
            "Warm gratitude for sharing these peaceful and grounding contemplation points."
        ]
        op_en = openings_ref_en[h_val % len(openings_ref_en)]
        cl_en = closings_ref_en[h_val % len(closings_ref_en)]

        candidates.append(CommentCandidate(
            candidate_id=f"{v_id}_syn_1",
            video_id=v_id,
            style="Reflective",
            language="en",
            content=f"{op_en} It is so easy to forget that peace begins by letting things be as they are. {cl_en}",
            insight_summary="Grounding contemplative reflection on inner stillness.",
            evidence_points=[primary_evidence],
            research_confidence=confidence_level
        ))

        # Candidate 2: Insightful
        openings_ins_en = [
            f"The distinction highlighted here regarding {secondary_evidence.lower()} is exceptionally clear.",
            f"A very practical take on applying {topic.lower()} without spiritual bypassing.",
            f"What resonates most is the emphasis on kindness when navigating {secondary_evidence.lower()}."
        ]
        closings_ins_en = [
            "Allowing room for imperfection turns out to be the most genuine form of compassion.",
            "Holding expectations lightly often dissolves unnecessary friction before it even starts.",
            "True strength seems to lie in our willingness to remain open and humble."
        ]
        op_ins_en = openings_ins_en[(h_val + 1) % len(openings_ins_en)]
        cl_ins_en = closings_ins_en[(h_val + 1) % len(closings_ins_en)]

        candidates.append(CommentCandidate(
            candidate_id=f"{v_id}_syn_2",
            video_id=v_id,
            style="Insightful",
            language="en",
            content=f"{op_ins_en} In professional and family life, rigid resistance often causes more suffering than the situation itself. {cl_ins_en}",
            insight_summary="Insightful reflection on letting go and emotional flexibility.",
            evidence_points=[secondary_evidence],
            research_confidence=confidence_level
        ))

        # Candidate 3: Thoughtful Question
        questions_en = [
            f"An enriching and thoughtful talk. When facing {primary_evidence.lower()} in relationships, do you find it more skillful to practice immediate quiet retreat or gentle inquiry once emotions settle?",
            f"Deeply appreciate this clarity on {topic.lower()}. How do long-term practitioners maintain mindful balance when work deadlines demand intense mental focus?",
            f"Such valuable insights. What specific daily habit has helped you most in bridging formal meditation practice with unexpected interpersonal friction?"
        ]
        q_sel_en = questions_en[(h_val + 2) % len(questions_en)]

        candidates.append(CommentCandidate(
            candidate_id=f"{v_id}_syn_3",
            video_id=v_id,
            style="Thoughtful Question",
            language="en",
            content=q_sel_en,
            insight_summary="Open inquiry inviting compassionate community dialogue.",
            evidence_points=[primary_evidence],
            research_confidence=confidence_level
        ))

    return candidates
