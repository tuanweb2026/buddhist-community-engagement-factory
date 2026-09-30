# TOP 10 REPOSITORIES DÀNH CHO BCE-FACTORY

Báo cáo xếp hạng 10 Repository xuất sắc nhất được trích xuất từ 30 ứng viên trong `docs/repository-candidates.json`.

---

## 1. `google-api-python-client` (Google)
* **Category:** YouTube Discovery & Channel Analytics
* **Adoption Score:** 0.94 | **License:** Apache-2.0 | **Recommendation:** **PRIMARY**
* **Why selected:** Client chính thức và chuẩn mực nhất của Google cho YouTube Data API v3 và YouTube Analytics API.
* **Useful components:** `youtube.search().list`, `youtube.commentThreads().list`, `youtube.channels().list`.
* **Architecture strengths:** Quản lý OAuth2 token an toàn, hỗ trợ quota management và error handling chính xác theo mã HTTP chuẩn.
* **Weaknesses:** Giới hạn quota 10,000 units/ngày cho bản miễn phí.
* **Security concerns:** Không có. Tuân thủ enterprise security.
* **What BCE-Factory should reuse:** Service builder, resource request mapping và xác thực kênh `@1995lido`.
* **What BCE-Factory should NOT reuse:** Tránh gọi API liên tục cho các tác vụ search nặng nề gây cạn quota.

---

## 2. `youtube-transcript-api` (jdepoix)
* **Category:** Transcript Layer
* **Adoption Score:** 0.92 | **License:** MIT | **Recommendation:** **PRIMARY**
* **Why selected:** Tiêu chuẩn de facto của cộng đồng Python để trích xuất phụ đề video YouTube không cần API key và không cần browser automation.
* **Useful components:** Parser định dạng phụ đề XML/JSON, đa ngôn ngữ (`vi`, `en`), lấy timestamps chi tiết (`start`, `duration`).
* **Architecture strengths:** Nhẹ, độc lập, không phụ thuộc Chromium/Playwright.
* **Weaknesses:** Chỉ lấy được khi video có bật phụ đề (chính thức hoặc auto-generated).
* **Security concerns:** Không có. Không can thiệp credential.
* **What BCE-Factory should reuse:** Engine trích xuất phụ đề cấp độ 1 trong `TranscriptAgent`.
* **What BCE-Factory should NOT reuse:** Không phụ thuộc tuyệt đối 100% nếu video không có phụ đề (phải có fallback sang mô tả bài giảng).

---

## 3. `yt-dlp` (yt-dlp team)
* **Category:** YouTube Discovery & Fallback Scraping
* **Adoption Score:** 0.92 | **License:** Unlicense | **Recommendation:** **PRIMARY**
* **Why selected:** Dự án mã nguồn mở mạnh mẽ và được bảo trì tích cực nhất hiện nay để cào metadata, thống kê và comment threads.
* **Useful components:** Extractor module `YoutubeIE`, `getcomments` logic, mô phỏng client headers an toàn.
* **Architecture strengths:** Khả năng tự thích ứng khi YouTube cập nhật giao diện web, cào được top comments sắp xếp theo like_count.
* **Weaknesses:** Codebase rất lớn, phức tạp nếu nhúng sâu toàn bộ repository.
* **Security concerns:** Thận trọng khi chạy script hook bên ngoài.
* **What BCE-Factory should reuse:** Cơ chế trích xuất metadata và top comments dự phòng cho Discovery & Engagement Layer.
* **What BCE-Factory should NOT reuse:** Tuyệt đối không sử dụng tính năng tải file media (MP4/WebM) gây tốn tài nguyên.

---

## 4. `pydantic` (Pydantic team)
* **Category:** Core Architecture & Schemas
* **Adoption Score:** 0.98 | **License:** MIT | **Recommendation:** **DEPENDENCY**
* **Why selected:** Chuẩn mực tối cao để xác thực dữ liệu, định hình Input/Output schemas cho cả 10 Agents.
* **Useful components:** `BaseModel`, `Field`, `model_dump_json()`, type validation.
* **Architecture strengths:** Thực thi tốc độ cao bằng Rust core (`pydantic-core`), đảm bảo mọi Agent giao tiếp an toàn, không lỗi type.
* **What BCE-Factory should reuse:** Toàn bộ schemas trong `config/schemas.py`.

---

## 5. `guardrails-ai` (Guardrails AI)
* **Category:** Quality Layer
* **Adoption Score:** 0.88 | **License:** Apache-2.0 | **Recommendation:** **ADAPT**
* **Why selected:** Framework dẫn đầu về xây dựng hàng rào kiểm duyệt chất lượng output của LLM.
* **Useful components:** Mô hình Validator độc lập, cơ chế chặn hallucination, cấm promotion và regex verification.
* **Architecture strengths:** Fail-fast gate logic: Nếu 1 gate fail $\rightarrow$ lập tức REJECT, không tính trung bình.
* **What BCE-Factory should reuse:** Tư duy kiến trúc của 10 Quality Gates trong `CommentQualityGateAgent`.
* **What BCE-Factory should NOT reuse:** Tránh cài đặt các dependency remote inference quá nặng nề của hub.

---

## 6. `langgraph` (LangChain)
* **Category:** AI Agent Orchestration
* **Adoption Score:** 0.88 | **License:** MIT | **Recommendation:** **ARCHITECTURE REFERENCE**
* **Why selected:** Mô hình đồ thị trạng thái có hướng (Stateful Directed Graph) tốt nhất cho quy trình Agentic có sự giám sát của con người.
* **Useful components:** Checkpoint state management, Human-in-the-loop interruption gate, replayable traces.
* **Architecture strengths:** Đảm bảo hệ thống vận hành có tính tất định (deterministic), có thể tạm dừng để chờ review.
* **What BCE-Factory should reuse:** Triết lý tách biệt giữa Autonomous Task (Level 0/1) và Supervised Gate (Level 2).
* **What BCE-Factory should NOT reuse:** Tránh gắn chặt toàn bộ project vào abstractions cồng kềnh của hệ sinh thái LangChain.

---

## 7. `mem0` (mem0ai)
* **Category:** RAG & Memory System
* **Adoption Score:** 0.87 | **License:** Apache-2.0 | **Recommendation:** **ARCHITECTURE REFERENCE**
* **Why selected:** Kiến trúc bộ nhớ đa tầng (Multi-tier Memory) tiên tiến dành riêng cho autonomous agents.
* **Useful components:** Phân chia bộ nhớ ngắn hạn (Session), trung hạn (Recent interactions) và dài hạn (Learned Patterns).
* **Architecture strengths:** Tự động đúc kết factual insights và loại bỏ nhiễu.
* **What BCE-Factory should reuse:** Thiết kế 3 tầng bộ nhớ Short/Medium/Long-Term Memory cho `EngagementAnalyticsAgent`.

---

## 8. `tenacity` (jd)
* **Category:** Resiliency & Error Recovery
* **Adoption Score:** 0.94 | **License:** Apache-2.0 | **Recommendation:** **DEPENDENCY**
* **Why selected:** Thư viện xử lý retry và hồi phục lỗi mạng, rate-limit tin cậy nhất trong Python.
* **Useful components:** `@retry`, `wait_exponential`, `stop_after_attempt(3)`.
* **Architecture strengths:** Đảm bảo hệ thống tự chẩn đoán và khắc phục tối đa 3 lần theo nguyên tắc Supervised Autopilot.

---

## 9. `rich` (Textualize)
* **Category:** Observability & Terminal Dashboard
* **Adoption Score:** 0.95 | **License:** MIT | **Recommendation:** **DEPENDENCY**
* **Why selected:** Thư viện dựng giao diện terminal bảng biểu, màu sắc và tiến trình xuất sắc nhất cho CLI.
* **Useful components:** `Table`, `Panel`, `Console`, live progress rendering.
* **What BCE-Factory should reuse:** Giao diện `dashboard/terminal_dashboard.py` hiển thị Funnel và 10 Quality Gates.

---

## 10. `n8n` (n8n.io)
* **Category:** Automation Layer
* **Adoption Score:** 0.86 | **License:** Sustainable Use License | **Recommendation:** **ARCHITECTURE REFERENCE**
* **Why selected:** Nền tảng điều phối workflow, scheduler và webhook mạnh mẽ nhất cho hệ thống tích hợp bên ngoài.
* **Useful components:** Định dạng JSON workflow trigger, cron timer, webhook dispatching.
* **What BCE-Factory should reuse:** Cơ chế làm việc ở lớp Automation (kích hoạt lịch trình, thông báo Telegram/Email khi có comment được phê duyệt).
* **What BCE-Factory should NOT reuse:** Không đặt core AI reasoning vào n8n; trí tuệ cốt lõi phải nằm trong Agent Architecture.
