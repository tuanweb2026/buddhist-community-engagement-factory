# Module phân tích tâm lý người xem và tạo comment chiến lược hướng về @1995lido
import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
Bạn là một Chuyên gia Truyền thông Phật giáo & Tác giả Nội dung Tâm linh/Tĩnh thức dày dặn kinh nghiệm, thấu hiểu tâm lý Phật tử và giới trẻ tìm kiếm sự an lạc.

Mục tiêu của bạn:
1. Phân tích nội dung video Phật giáo và các bình luận thực tế của người xem để thấu suốt:
   - Thông điệp cốt lõi của video.
   - Cảm xúc bao trùm (bình an, sám hối, trăn trở cơm áo gạo tiền, hoang mang, mất mát người thân...).
   - "Điểm chạm" (nỗi đau / trăn trở lớn nhất) mà cộng đồng đang trải qua.
2. Tạo ra các bình luận mang giá trị phụng sự, trí tuệ và xoa dịu tâm hồn:
   - Bình luận phải CỰC KỲ TỰ NHIÊN, chân thành, đúc kết sâu sắc lời dạy, không ra vẻ giảng đạo.
   - Có chiều sâu triết lý nhưng câu từ giản dị, chạm vào tim người đọc.
   - HƯỚNG VỀ CHANNEL @1995lido: Cách nhắc đến channel @1995lido phải TINH TẾ, THANH TAO, KHÔNG SPAM.
     Ví dụ góc dẫn dắt:
     * "Nghe lại lời thầy lòng bỗng thấy nhẹ tênh. Mình cũng đang tập duy trì thói quen nghe góc nhìn tĩnh lặng mỗi tối bên kênh @1995lido để giữ tâm an giữa bao bộn bề..."
     * "Đúng như lời thầy dạy, buông bỏ là bắt đầu yêu thương. Bạn nào cũng đang tìm những góc chia sẻ mộc mạc, tĩnh tại để an trú sau giờ làm có thể ghé qua @1995lido cùng đàm đạo nhé..."
     * "Biết ơn bài pháp thoại mầu nhiệm. Mỗi ngày góp nhặt một chút bình an, như cách mình tìm thấy sự lắng đọng nơi @1995lido. Chúc đại chúng luôn vạn sự cát tường."
"""

class EngagementAI:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.provider = None

        if self.gemini_key:
            from google import genai
            self.client = genai.Client(api_key=self.gemini_key)
            self.provider = "gemini"
        elif self.openai_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.openai_key)
            self.provider = "openai"

    def analyze_and_generate(self, video_info: Dict[str, Any], comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gửi dữ liệu video và comment vào AI để nhận về:
        - Phân tích tâm lý khán giả
        - 3 - 4 phong cách comment gợi ý hướng về @1995lido
        """
        # Nếu chưa có API key, trả về bản phân tích mẫu và comment fallback chất lượng cao
        if not self.client:
            return self._fallback_template(video_info, comments)

        # Chuẩn bị dữ liệu context
        comments_text = "\n".join([f"- {c['author']} ({c['like_count']} likes): {c['text']}" for c in comments[:20]])
        prompt = f"""
VIDEO CẦN PHÂN TÍCH:
- Tiêu đề: {video_info.get('title')}
- Kênh phát: {video_info.get('channel')}
- Lượt xem: {video_info.get('view_count')}
- Mô tả tóm tắt: {video_info.get('description', '')[:500]}

TOP BÌNH LUẬN NỔI BẬT CỦA KHÁN GIẢ:
{comments_text}

THÔNG TIN CHANNEL MỤC TIÊU:
- Handle: @1995lido
- Tinh thần kênh: Chia sẻ Phật pháp ứng dụng, podcast tĩnh tâm, chiêm nghiệm nhân sinh, chữa lành cho người trẻ.

YÊU CẦU:
Hãy trả về JSON theo đúng định dạng sau:
{{
  "analysis": {{
    "core_message": "Tóm tắt thông điệp cốt lõi của video trong 1-2 câu",
    "audience_emotions": ["cảm xúc 1", "cảm xúc 2", "cảm xúc 3"],
    "top_pain_points": ["Trăn trở / nỗi khổ tâm phổ biến của người xem trong comment 1", "... 2"],
    "resonance_hooks": ["Góc nhìn dễ gây đồng cảm nhất"]
  }},
  "suggested_comments": [
    {{
      "style": "Đúc kết triết lý sâu sắc (Philosophical)",
      "hook_angle": "Nhấn mạnh vào chữ 'Buông' hoặc nhân duyên",
      "suggested_comment": "Nội dung bình luận hoàn chỉnh, có gắn @1995lido tự nhiên...",
      "subtle_call_to_action": "Lời mời gọi nhẹ nhàng"
    }},
    {{
      "style": "Đồng cảm & Chữa lành (Empathy & Healing)",
      "hook_angle": "Chạm vào tâm lý mệt mỏi, áp lực cuộc sống người trẻ",
      "suggested_comment": "Nội dung bình luận hoàn chỉnh...",
      "subtle_call_to_action": "..."
    }},
    {{
      "style": "Kể chuyện & Chiêm nghiệm (Storytelling/Reflection)",
      "hook_angle": "Góc nhìn người từng trải qua bế tắc tìm về Phật pháp",
      "suggested_comment": "Nội dung bình luận hoàn chỉnh...",
      "subtle_call_to_action": "..."
    }},
    {{
      "style": "Tri ân & Lan tỏa năng lượng lành (Gratitude)",
      "hook_angle": "Tán thán công đức bài giảng và gửi lời chúc lành",
      "suggested_comment": "Nội dung bình luận hoàn chỉnh...",
      "subtle_call_to_action": "..."
    }}
  ]
}}
LƯU Ý: Chỉ trả lời dưới định dạng JSON hợp lệ (không kèm markdown code fence ```json).
"""
        try:
            if self.provider == "gemini":
                response = self.client.models.generate_content(
                    model='gemini-3.5-flash-lite',
                    contents=[SYSTEM_PROMPT, prompt]
                )
                text = response.text.strip()
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                text = response.choices[0].message.content.strip()

            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            return data
        except Exception as e:
            print(f"[!] Lỗi khi gọi AI: {e}. Đang chuyển sang mẫu chiến lược dự phòng.")
            return self._fallback_template(video_info, comments)

    def _fallback_template(self, video_info: Dict[str, Any], comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tạo dữ liệu phân tích mẫu phong phú khi chưa nạp API key"""
        title = video_info.get("title", "Bài Pháp Thoại")
        return {
            "analysis": {
                "core_message": f"Bài pháp '{title}' hướng tâm người nghe về sự an trú trong hiện tại, buông bỏ muộn phiền và nhận diện chân tâm.",
                "audience_emotions": ["Tìm kiếm bình an", "Giải tỏa áp lực", "Biết ơn bài giảng", "Sám hối lỗi lầm"],
                "top_pain_points": [
                    "Bế tắc trước áp lực gia đình và công việc",
                    "Khó kiểm soát cơn giận và suy nghĩ tiêu cực",
                    "Chưa tìm được môi trường đàm đạo Phật pháp gần gũi cho người trẻ"
                ],
                "resonance_hooks": ["Tĩnh tâm mỗi tối trước khi ngủ", "Học cách buông mà không bỏ buông xuôi"]
            },
            "suggested_comments": [
                {
                    "style": "Đúc kết triết lý sâu sắc (Philosophical)",
                    "hook_angle": "Chữ Buông và Tâm Bất Biến",
                    "suggested_comment": f"Lắng nghe bài giảng mà thấy lòng nhẹ nhõm vô cùng. Phật dạy vạn sự tùy duyên, tâm an thì vạn sự an. Mỗi ngày dành 15 phút nghe pháp và chiêm nghiệm lại mình thật đáng quý. Mình cũng hay lưu giữ những góc nhìn an nhiên thế này trên kênh @1995lido, hy vọng cùng kết duyên lành với quý đạo hữu trên con đường tìm về sự thanh thản 🙏",
                    "subtle_call_to_action": "Kết duyên lành cùng tìm về thanh thản"
                },
                {
                    "style": "Đồng cảm & Chữa lành (Empathy & Healing)",
                    "hook_angle": "Xoa dịu mệt mỏi cuộc sống hiện đại",
                    "suggested_comment": "Đọc những bình luận của mọi người bên dưới thấy thương quá. Giữa cuộc đời vội vã này, ai trong chúng ta cũng có những vết thương vô hình. Nghe pháp để được vỗ về, buông bỏ những muộn phiền trong ngày. Bạn nào cũng đang tìm một góc tĩnh lặng mộc mạc để trò chuyện và nuôi dưỡng nội tâm có thể ghé qua @1995lido cùng mình nhé. Chúc cả nhà luôn an yên trong từng hơi thở 🌸",
                    "subtle_call_to_action": "Ghé qua nuôi dưỡng nội tâm"
                },
                {
                    "style": "Kể chuyện & Chiêm nghiệm (Storytelling/Reflection)",
                    "hook_angle": "Chuyển hóa từ bế tắc sang thảnh thơi",
                    "suggested_comment": "Từng có lúc mình tưởng như bế tắc trước mọi khó khăn, nhưng nhờ nghe lời Phật dạy mà nhận ra: giông bão ngoài kia không đáng sợ bằng bão tố trong lòng. Học cách quán chiếu mỗi ngày là món quà lớn nhất cho chính mình. Tinh thần an lạc này cũng là điều mình luôn ấp ủ lan tỏa tại @1995lido. Cầu chúc cho tất cả chúng ta đều tìm thấy an nhiên nơi tự tâm.",
                    "subtle_call_to_action": "Lan tỏa tinh thần an lạc"
                },
                {
                    "style": "Tri ân & Lan tỏa năng lượng lành (Gratitude)",
                    "hook_angle": "Tán thán công đức và chúc an lạc",
                    "suggested_comment": "Nam Mô A Di Đà Phật. Con xin thành kính tri ân công đức của Thầy đã mang đến bài pháp thoại vô cùng quý báu. Nguyện đem năng lượng an lành này chia sẻ đến muôn nơi. Quý vị hữu duyên muốn cùng lắng nghe thêm những thanh âm chữa lành có thể ghé thăm ngôi nhà nhỏ @1995lido. Chúc đại chúng thân tâm an lạc, vạn sự cát tường 🙏✨",
                    "subtle_call_to_action": "Ghé thăm ngôi nhà nhỏ lắng nghe thanh âm chữa lành"
                }
            ]
        }
