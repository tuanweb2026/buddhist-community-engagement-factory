# Comment Diversity & Quality Audit Report (10-Video Dry-Run)

**Date:** 2026-09-30  
**Target Channel:** `@1995lido`  
**Test Mode:** `DRY_RUN = True`, `PUBLISH = False` (Zero YouTube comments published)  
**Sample Size:** 10 distinct videos across 10 channels from SQLite database  

---

## 1. Kết Quả Sinh Bình Luận Cho 10 Video Thực Tế

| # | Channel | Video Title | Lang | Style | Research Confidence | Final Candidate Generated |
| :-: | :--- | :--- | :-: | :-: | :-: | :--- |
| **01** | *1983dukkha* | Ajahn Chah - Unshakeable Peace | `en` | `Reflective` | `MEDIUM` | *"This talk brings such a grounding reminder of stillness amidst the busyness of modern life. Simply returning to the breath and acknowledging things as they are makes such a profound difference. Deeply grateful for these peaceful reflections."* |
| **02** | *Ajahn Anan Dhamma* | Why are We Here? \| Ajahn Chah | `en` | `Reflective` | `MEDIUM` | *"This talk brings such a grounding reminder of stillness amidst the busyness of modern life. Simply returning to the breath and acknowledging things as they are makes such a profound difference. Deeply grateful for these peaceful reflections."* |
| **03** | *AudioBuddha* | The Collected Teachings of Ajahn Chah Vol. 1 | `en` | `Reflective` | `MEDIUM` | *"This talk brings such a grounding reminder of stillness amidst the busyness of modern life. Simply returning to the breath and acknowledging things as they are makes such a profound difference. Deeply grateful for these peaceful reflections."* |
| **04** | *Buddha's Footsteps* | Some Endings Are Compassion in Disguise | `en` | `Reflective` | `MEDIUM` | *"This talk brings such a grounding reminder of stillness amidst the busyness of modern life. Simply returning to the breath and acknowledging things as they are makes such a profound difference. Deeply grateful for these peaceful reflections."* |
| **05** | *Buddhism For Sleep* | Guided Meditation for Sleep | `en` | `Reflective` | `MEDIUM` | *"This talk brings such a grounding reminder of stillness amidst the busyness of modern life. Simply returning to the breath and acknowledging things as they are makes such a profound difference. Deeply grateful for these peaceful reflections."* |
| **06** | *Buddhism Podcast* | Understanding Impermanence - Why Everything Changes | `en` | `Reflective` | `MEDIUM` | *"This talk brings such a grounding reminder of stillness amidst the busyness of modern life. Simply returning to the breath and acknowledging things as they are makes such a profound difference. Deeply grateful for these peaceful reflections."* |
| **07** | *Can You Zen* | Vipassana Guided Meditation - 30 Minute Sit | `en` | `Reflective` | `MEDIUM` | *"This talk brings such a grounding reminder of stillness amidst the busyness of modern life. Simply returning to the breath and acknowledging things as they are makes such a profound difference. Deeply grateful for these peaceful reflections."* |
| **08** | *Declutter The Mind* | 10 Minute Vipassana Meditation for Equanimity | `en` | `Reflective` | `MEDIUM` | *"This talk brings such a grounding reminder of stillness amidst the busyness of modern life. Simply returning to the breath and acknowledging things as they are makes such a profound difference. Deeply grateful for these peaceful reflections."* |
| **09** | *Giáo Lý Từ Đức Đạt Lai Lạt Ma* | Giáo Lý Về Chuyển Hóa Tâm | `vi` | `Reflective` | `MEDIUM` | *"Lắng nghe những chia sẻ của Thầy về phật pháp ứng dụng & chuyển hóa tâm thức mà thấy lòng mình lắng lại giữa bao bộn bề. Có những ngày chỉ cần ngồi yên vài phút, nhận biết hơi thở vào ra là đã thấy gánh nặng vơi đi nhiều. Biết ơn bài pháp thoại thật nhiều."* |
| **10** | *HAPPY LIFE* | Nghệ Thuật Buông Bỏ Phiền Muộn | `vi` | `Reflective` | `MEDIUM` | *"Lắng nghe những chia sẻ của Thầy về học cách buông bỏ phiền não mà thấy lòng mình lắng lại giữa bao bộn bề. Có những ngày chỉ cần ngồi yên vài phút, nhận biết hơi thở vào ra là đã thấy gánh nặng vơi đi nhiều. Biết ơn bài pháp thoại thật nhiều."* |

---

## 2. Kiểm Tra Trực Diện Về Tính Đa Dạng (Diversity Audit Metrics)

Phân tích định lượng chính xác trên 10 bình luận:
- **Tỷ lệ mở đầu độc bản (Unique Openings):** **3 / 10** (Thấp).
  - Mở đầu tiếng Anh bị lặp: *"This talk brings such a grounding reminder of stillness amidst the busyness of modern life"* (xuất hiện 8/8 video tiếng Anh).
- **Tỷ lệ kết bài độc bản (Unique Closings):** **2 / 10** (Thấp).
  - Kết bài tiếng Anh bị lặp: *"Deeply grateful for these peaceful reflections"* (xuất hiện 8/8 video).
  - Kết bài tiếng Việt bị lặp: *"Biết ơn bài pháp thoại thật nhiều"* (xuất hiện 2/2 video).
- **Cụm 3 từ lặp nhiều nhất (Top Repeated Phrases):**
  - `"this talk brings"`: 8 lần
  - `"such a grounding"`: 8 lần
  - `"a grounding reminder"`: 8 lần
- **Độ chính xác ngôn ngữ (Language Alignment):** **10 / 10 (100% PASS)**:
  - Video tiếng Việt xuất bình luận tiếng Việt chuẩn mực.
  - Video tiếng Anh xuất bình luận tiếng Anh tự nhiên.
- **Rào chắn bản sắc (Identity & Safety Gates):** **100% PASS**:
  - Không có bất kỳ từ khóa quảng bá kênh `@1995lido` hay kêu gọi sub/like.
  - Không có sự mạo danh tu sĩ hay tự xưng sư thầy.

---

## 3. Nguyên Nhân Gốc Rễ (Root Cause Analysis)

1. **Khi không có LLM API Key (GEMINI_API_KEY / OPENAI_API_KEY chưa cấu hình):**
   - Module `comment_generator.py` đang fallback về bộ khung tĩnh gồm 3 phong cách:
     - Candidate 1: *Reflective*
     - Candidate 2: *Insightful*
     - Candidate 3: *Thoughtful Question*
2. **Quality Gate luôn chọn Candidate 1 theo thứ tự duyệt:**
   - Vòng lặp duyệt ưu tiên `for cand in candidates:` luôn thấy Candidate 1 (Reflective) pass quality gate đầu tiên, nên **Candidate 1 luôn được chọn làm Final Comment**.
   - Điều này dẫn đến hiện tượng **nhiều video tiếng Anh nhận cùng một mẫu bình luận Reflective tĩnh**.
3. **Cơ chế chống trùng lặp (Duplicate Checker) hiện tại:**
   - Hoạt động bằng cách chặn đăng nếu một comment đã tồn tại trong bảng `published_comments` cho kênh đó. Vì vậy trong lần chạy đầu tiên, các comment giống nhau trên các kênh khác nhau vẫn có thể được tạo ra nếu chỉ dựa vào mẫu template cố định.

---

## 4. Đánh Giá Khách Quan

| Tiêu chí | Kết quả | Giải thích |
| :--- | :---: | :--- |
| **Language Match** | **PASS** | 100% video khớp ngôn ngữ chuẩn xác (VI -> VI, EN -> EN). |
| **Safety & Non-Promotional** | **PASS** | 0 self-promotion, 0 fake monk bio, văn phong khiêm nhường. |
| **Comment Diversity** | **PARTIAL** | Các bình luận đều tử tế và đúng văn hóa Phật giáo, nhưng **bị lặp cấu trúc mở đầu và kết bài** khi chạy ở chế độ Template Fallback (chưa có LLM dynamic generation). |
| **Context Awareness** | **PARTIAL** | Bình luận nói về chánh niệm, buông xả nói chung, chưa đào sâu vào chi tiết độc nhất của từng bài giảng cụ thể khi không có LLM đọc toàn văn transcript. |
