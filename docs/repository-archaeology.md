# Repository Archaeology: YouTube Intelligence & Autonomous Agent Frameworks

**Project:** Buddhist Community Engagement Factory (`BCE-Factory`)  
**Version:** `v1.0`  
**Date:** 2026-09-29  

---

## 1. Mục Đích Nghiên Cứu

Tài liệu này tổng hợp việc khảo sát các dự án mã nguồn mở uy tín liên quan đến:
1. YouTube Data Retrieval & Captions/Transcript extraction
2. Agent Orchestration & Quality Gates
3. Community Discussion Mining & Natural Language Understanding

---

## 2. Danh Sách Repository Khảo Sát & Đánh Giá

### 2.1. `youtube-transcript-api` (jdepoix/youtube-transcript-api)
* **Mục đích:** Trích xuất official phụ đề/captions từ YouTube không cần API key hay browser automation nặng nề.
* **Kiến trúc:** HTTP requests trực tiếp tới endpoint phụ đề của YouTube, parse định dạng XML/JSON.
* **Thành phần hữu ích:**
  - Hỗ trợ đa ngôn ngữ (Vietnamese, English, auto-generated).
  - Trả về danh sách text kèm timestamps chính xác (`start`, `duration`).
* **Học hỏi cho BCE-Factory:** Tích hợp làm tier 1 trong Transcript Agent trước khi tính đến audio fallback.
* **Điều KHÔNG sao chép:** Không dùng làm công cụ duy nhất khi video tắt hoàn toàn phụ đề.
* **License:** MIT
* **Security:** Cao, không yêu cầu credential người dùng.
* **Recommendation:** **PRIMARY** (Thành phần trích xuất phụ đề chính thức).

---

### 2.2. `yt-dlp` (yt-dlp/yt-dlp)
* **Mục đích:** Thu thập metadata, video info, channel details, và top comment threads.
* **Kiến trúc:** Modular extractors viết bằng Python, liên tục cập nhật theo thay đổi của YouTube.
* **Thành phần hữu ích:**
  - Cào metadata phong phú (view velocity, upload date, likes, comment threads).
  - Tích hợp extractor_args linh hoạt (`youtube:player_client`).
* **Học hỏi cho BCE-Factory:** Sử dụng làm Tier 2 Data Connector khi không có YouTube Data API v3 key hoặc bổ trợ cho API v3.
* **Điều KHÔNG sao chép:** Không tải xuống video file (MP4) nặng nề gây tốn băng thông và vi phạm nguyên tắc lưu trữ tối giản.
* **License:** Unlicense
* **Security:** Tốt, chạy local an toàn.
* **Recommendation:** **PRIMARY** (Dự phòng cho Discovery & Metadata extraction).

---

### 2.3. `google-api-python-client` (YouTube Data API v3)
* **Mục đích:** Giao thức chuẩn chính thống từ Google để tìm kiếm, lấy video/channel metrics và comment threads.
* **Kiến trúc:** RESTful client chính thống của Google.
* **Thành phần hữu ích:**
  - `youtube.search().list`
  - `youtube.commentThreads().list`
  - `youtube.channels().list`
* **Học hỏi cho BCE-Factory:** Cần thiết lập làm **Tier 1 (API First)** khi có `YOUTUBE_API_KEY`.
* **Điều KHÔNG sao chép:** Tránh lạm dụng quota (10,000 units/ngày) bằng cách kết hợp cơ chế cache thông minh và fallbacks.
* **License:** Apache 2.0
* **Security:** Cực cao, chuẩn enterprise.
* **Recommendation:** **PRIMARY**.

---

### 2.4. `Guardrails AI` / `Pydantic-based Evaluators`
* **Mục đích:** Xây dựng hàng rào kiểm duyệt chất lượng (Quality Gates), phát hiện hallucination, self-promotion và off-topic.
* **Kiến trúc:** Schema validation song song với Rule-based regex & LLM-as-a-judge.
* **Thành phần hữu ích:**
  - Định nghĩa 10 Quality Gates nghiêm ngặt: No Self-Promotion, No Hallucinated Quotes, Relevance, Sensitivity.
  - Fail-fast pattern: nếu 1 gate trọng yếu fail -> lập tức REJECT.
* **Học hỏi cho BCE-Factory:** Áp dụng mô hình deterministic validation kết hợp semantic LLM guardrails cho Quality Gate Agent.
* **License:** Apache 2.0
* **Recommendation:** **REFERENCE**.

---

### 2.5. Selenium / Playwright Browser Automation cho Commenting
* **Mục đích:** Tự động đăng nhập và click đăng comment.
* **Đánh giá rủi ro:**
  - Dễ kích hoạt checkpoint/CAPTCHA của Google.
  - Vi phạm chính sách an toàn, rủi ro vô hiệu hóa tài khoản `@1995lido`.
* **Recommendation:** **REJECT** (Áp dụng nguyên tắc DRY-RUN và Human Supervised Approval, tuyệt đối không dùng browser bot để spam comment).

---

## 3. Tổng Kết Khuyến Nghị Cho BCE-Factory

| Component | Lựa Chọn Kỹ Thuật | Vai Trò |
| :--- | :--- | :--- |
| **API First Connector** | Google YouTube Data API v3 | Lớp kết nối chính thống (Tier 1) |
| **Fallback Scraper** | `yt-dlp` | Lớp cào dự phòng khi quota cạn hoặc không có key (Tier 2) |
| **Transcript Engine** | `youtube-transcript-api` + Fallback | Lấy văn bản bài giảng có timestamp |
| **AI Brain / LLM** | Google GenAI SDK (`gemini-2.5-flash`) / OpenAI (`gpt-4o-mini`) | Suy luận, phân tích gap, sinh comment |
| **Quality Engine** | Pydantic Schema + Multi-gate Checker | 10 Quality Gates nghiêm ngặt |
| **Storage** | SQLite + Clean Repository Pattern | Lưu trữ bền vững, sẵn sàng migrate PostgreSQL |
