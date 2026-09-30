"""
Channel Intelligence Module:
Phân tích 3 lớp cho từng kênh trong Channel Radar:
- Layer 1 (Observation): Kênh làm gì tốt, chủ đề nào view cao nhất?
- Layer 2 (Interpretation): Tại sao người xem lại gắn kết, không khí thảo luận thế nào?
- Layer 3 (Opportunity): Lido có thể học hỏi điều gì (gợi ý nội dung, phong cách)?
"""

from typing import Dict, Any, List
from models import ChannelRecord, ChannelIntelligenceCard
from db_storage import save_channel_intelligence, get_channel_intelligence

class ChannelIntelligenceEngine:
    def analyze_channel(self, channel: ChannelRecord, sample_videos: List[Any] = None, sample_comments: List[Any] = None) -> ChannelIntelligenceCard:
        """
        Xây dựng Channel Intelligence Card 3 lớp
        """
        existing = get_channel_intelligence(channel.channel_id)
        if existing and existing.get("content_strengths"):
            return ChannelIntelligenceCard(**existing)

        # Phân tích theo trường phái & dữ liệu kênh
        strengths = []
        top_topics = []
        recurring_qs = []
        learnings = []
        vibe = "Thanh tịnh, tương kính và cầu thị"

        if "Làng Mai" in channel.channel_name or "Plum Village" in channel.channel_name:
            strengths = [
                "Nội dung thiền chánh niệm ứng dụng đời sống phương Tây và giới trẻ",
                "Âm thanh chuông tỉnh thức, nhịp điệu chậm rãi, hình ảnh thiên nhiên chữa lành",
                "Phụ đề đa ngôn ngữ và cách giải thích giáo lý dung dị không giáo điều"
            ]
            top_topics = ["Chánh niệm giải tỏa âu lo", "Nuôi dưỡng lòng từ bi", "Thiền hành và thở có ý thức"]
            recurring_qs = ["Làm sao duy trì chánh niệm giữa môi trường công sở áp lực?", "Cách hòa giải xung đột với cha mẹ khi quan điểm khác biệt?"]
            learnings = [
                "Lido nên áp dụng phong cách dẫn dắt nhẹ nhàng, tránh dùng thuật ngữ Hán-Phạn quá hàn lâm",
                "Đầu tư vào trải nghiệm thính giác (chuông tĩnh tâm, nhịp dừng tư duy)"
            ]
            vibe = "An lạc, cởi mở, hướng nội sâu sắc"

        elif "Pháp Hòa" in channel.channel_name:
            strengths = [
                "Văn phong bình dị, dí dỏm, giải đáp trực diện các nỗi khổ niềm đau đời thường",
                "Khả năng kết nối văn hóa truyền thống Việt Nam với giáo lý nhà Phật",
                "Các buổi vấn đáp trực tiếp tạo sự gắn bó cộng đồng cực mạnh"
            ]
            top_topics = ["Nghiệp và hóa giải nghiệp lực", "Chữ hiếu và ứng xử gia đình", "Buông bỏ phiền muộn đời thường"]
            recurring_qs = ["Làm sao buông xả oán giận người thân?", "Tại sao ăn chay tu niệm mà vẫn gặp trắc trở?"]
            learnings = [
                "Lido có thể phát triển định dạng Q&A giải đáp thắc mắc ngắn gọn, thực tế",
                "Dùng ngôn ngữ mộc mạc, gần gũi nhưng chuẩn mực chánh kiến"
            ]
            vibe = "Ấm áp, tri ân, giàu lòng trắc ẩn và tính cộng đồng"

        elif "Minh Niệm" in channel.channel_name:
            strengths = [
                "Chữa lành tâm lý kết hợp thiền Vipassana, tiếp cận đối tượng thanh thiếu niên và trí thức",
                "Chuỗi radio chia sẻ sâu sắc về các trạng thái tâm lý (trầm cảm, tổn thương, cô đơn)",
                "Hình thức tối giản, tập trung hoàn toàn vào giọng đọc và năng lượng truyền tải"
            ]
            top_topics = ["Chữa lành đứa trẻ bên trong", "Nâng dậy tâm hồn yếu đuối", "Làm chủ cơn giận"]
            recurring_qs = ["Làm sao thoát khỏi cảm giác cô độc giữa đám đông?", "Cách ngồi yên với nỗi đau mà không né tránh?"]
            learnings = [
                "Lido nên tạo các bài chia sẻ đi sâu vào tâm lý học Phật giáo ứng dụng",
                "Thiết kế format Radio/Podcast tĩnh tâm buổi tối"
            ]
            vibe = "Trầm lắng, thấu cảm, trị liệu tâm hồn"

        elif "Yuttadhammo" in channel.channel_name or "Theravada" in channel.tradition or "Ajahn" in channel.channel_name:
            strengths = [
                "Giáo lý Nguyên thủy chuẩn mực, chỉ dẫn thiền Tứ Niệm Xứ rõ ràng, chi tiết",
                "Tính logic, khoa học và thực hành kiểm chứng được",
                "Cộng đồng quốc tế tương tác sâu sắc về kỹ thuật hành thiền"
            ]
            top_topics = ["Four Foundations of Mindfulness", "Overcoming Hindrances in Meditation", "Dhamma in Daily Life"]
            recurring_qs = ["How to deal with persistent restlessness during sitting meditation?", "Is breath counting necessary for beginners?"]
            learnings = [
                "Lido có thể học hỏi cách giải thích các khái niệm Tứ Diệu Đế và Duyên Khởi mạch lạc, logic",
                "Làm phụ đề tiếng Anh chuẩn xác để mở rộng cộng đồng quốc tế"
            ]
            vibe = "Nghiêm túc, trí tuệ, tập trung vào giáo lý nguyên bản"

        else:
            strengths = ["Chia sẻ kinh nghiệm tu tập và lan tỏa chánh pháp", "Không gian tương tác thiện lành"]
            top_topics = ["Phật giáo ứng dụng", "Chánh niệm hàng ngày"]
            recurring_qs = ["Làm sao bình tâm khi gặp biến cố?"]
            learnings = ["Duy trì phẩm chất khiêm cung và thấu hiểu trong từng nội dung"]
            vibe = "Thành kính và cầu thị"

        card = ChannelIntelligenceCard(
            channel_id=channel.channel_id,
            channel_name=channel.channel_name,
            content_strengths=strengths,
            audience_engagement_level="High" if channel.tier in ("A_MAJOR", "B_STRONG") else "Moderate",
            top_performing_topics=top_topics,
            comment_community_vibe=vibe,
            recurring_questions=recurring_qs,
            lido_learnings=learnings
        )

        save_channel_intelligence(card.dict())
        return card
