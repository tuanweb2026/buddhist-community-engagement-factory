# ARCHITECTURE SPECIFICATION v1.0

**Project:** Buddhist Community Engagement Factory (`BCE-Factory`)  
**Target Channel:** `@1995lido`  
**Architecture:** Supervised Autopilot with Multi-Agent Orchestration  
**Phase 0 Status:** COMPLETED (Repository Intelligence & Adoption Integrated)  

---

## 1. Flow Diagram Tổng Thể

```
                      ┌──────────────────────┐
                      │     ORCHESTRATOR     │
                      └──────────┬───────────┘
                                 │
                                 ▼
                     [ 1. DISCOVERY LAYER ]
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
     Discovery Agent       Channel Finder      Opportunity Ranker
   (YouTube API/yt-dlp)  (Buddhist Channels) (Weighted 6-Factor Score)
            │
            ▼
                     [ 2. RESEARCH LAYER ]
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
   Video Research Agent   Transcript Agent     Buddhist Context Agent
  (Knowledge Card build) (Captions/Timestamps) (Tradition, Core Terms)
            │
            ▼
                    [ 3. ENGAGEMENT LAYER ]
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
 Comment Intelligence    Discussion Gap Agent   Comment Writer Agent
(11 Category Taxonomy) (Missing Value / Need) (3 Distinct Candidates)
            │
            ▼
                     [ 4. QUALITY LAYER ]
            ┌─────────────────────────────────────────┐
            │        COMMENT QUALITY GATE AGENT       │
            │   (10 Non-Compromising Quality Gates)   │
            └────────────────────┬────────────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
              [ REJECTED ]                 [ PASSED ]
           (Logged with Reason)                │
                                               ▼
                                     [ 5. ACTION GATE ]
                                    (DRY-RUN / SUPERVISED)
                                               │
                                               ▼
                                     [ 6. STORAGE & MEMORY ]
                                   (SQLite 15 Relational Tables)
```

---

## 2. Quyết Định Công Nghệ & Nguồn Cảm Hứng Mã Nguồn Mở (Technology Decisions)

Sau khi hoàn tất nghiên cứu 30 repositories tại Phase 0, kiến trúc hệ thống áp dụng các quyết định công nghệ sau:

### 2.1. Discovery Layer
* **Selected Technology:** `google-api-python-client` (Tier 1) kết hợp `yt-dlp` (Tier 2 Fallback)
* **Why Selected:** Bảo đảm nguyên tắc API-First chính thức, vừa bảo toàn quota YouTube thông qua cơ chế cào dự phòng khi quota cạn.
* **Repository Inspiration:** `googleapis/google-api-python-client` & `yt-dlp/yt-dlp`
* **License:** Apache-2.0 / Unlicense
* **Integration Method:** Python module `connectors/youtube_connector.py`.

### 2.2. Transcript Layer
* **Selected Technology:** `youtube-transcript-api` (Public captions extraction)
* **Why Selected:** Không yêu cầu API key, không cần headless browser nặng nề, trích xuất phụ đề đa ngữ (`vi`, `en`) kèm timestamps.
* **Repository Inspiration:** `jdepoix/youtube-transcript-api`
* **License:** MIT
* **Integration Method:** Python package `youtube-transcript-api` trong `TranscriptAgent`.

### 2.3. Schemas & Type Safety
* **Selected Technology:** `pydantic`
* **Why Selected:** Chuẩn hóa toàn bộ Input/Output schemas cho 10 agents, bảo đảm tính tất định và ngăn chặn lỗi type.
* **Repository Inspiration:** `pydantic/pydantic`
* **License:** MIT
* **Integration Method:** `config/schemas.py`.

### 2.4. Quality Gate Layer
* **Selected Technology:** `guardrails-ai` architectural pattern
* **Why Selected:** Mô hình Interceptor Fail-fast: 1 gate lỗi là REJECT ngay lập tức, không tính điểm trung bình.
* **Repository Inspiration:** `guardrails-ai/guardrails`
* **License:** Apache-2.0
* **Integration Method:** `agents/quality/quality_agents.py`.

### 2.5. Memory & Analytics Layer
* **Selected Technology:** `mem0` 3-tier memory model
* **Why Selected:** Phân tách rõ ràng Short-term (Run session), Medium-term (30–90 ngày) và Long-term (Proven patterns).
* **Repository Inspiration:** `mem0ai/mem0`
* **License:** Apache-2.0
* **Integration Method:** `agents/analytics/analytics_agents.py` và CSDL SQLite 15 bảng.

---

## 3. Chi Tiết 10 Quality Gates Bắt Buộc

Mỗi draft comment bắt buộc phải trải qua đánh giá nhị phân (Pass/Fail) độc lập:

1. **GATE 01 — Relevance:** Phải khớp 100% với chủ đề và nội dung video.
2. **GATE 02 — Context Accuracy:** Không hiểu sai bài giảng của Thầy/kênh gốc.
3. **GATE 03 — Originality:** Không dùng văn mẫu rập khuôn, độc bản.
4. **GATE 04 — Value:** Mang lại góc nhìn mới mẻ, an lạc, hữu ích cho người đọc.
5. **GATE 05 — Hallucination Check:** Tuyệt đối không bịa lời Phật, bịa kinh văn, bịa quote.
6. **GATE 06 — No Self-Promotion:** Tuyệt đối cấm câu kéo thô thiển ("subscribe", "qua kênh mình").
7. **GATE 07 — No Spam Pattern:** Không chứa link, không lặp ký tự, không emoji quá đà.
8. **GATE 08 — Natural Language:** Văn phong chân thành, tự nhiên như một người tu tập thực tế.
9. **GATE 09 — Buddhist Sensitivity:** Tôn trọng truyền thống (Bắc tông, Nam tông, Thiền phái,...).
10. **GATE 10 — Duplicate Detection:** So trùng với các comment đã tạo trong 30 ngày qua.

> **Quy tắc bất khả xâm phạm:** Không dùng điểm trung bình cộng. Chỉ cần 1 Critical Gate bị FAIL $\rightarrow$ Lập tức **REJECT** bản nháp đó.

---

## 4. Công Thức Tính Opportunity Score

$$\text{Opportunity Score} = 0.25 A_r + 0.20 F_s + 0.20 E_v + 0.15 D_a + 0.10 T_m + 0.10 G_p$$

Trong đó:
* $A_r$ (Audience Relevance): Độ phù hợp của khán giả mục tiêu Phật giáo.
* $F_s$ (Freshness): Tính thời điểm của video (video mới đăng có thảo luận sôi động).
* $E_v$ (Engagement Velocity): Tốc độ tăng trưởng view/like/comment.
* $D_a$ (Discussion Activity): Số lượng và độ dài thảo luận trong comments.
* $T_m$ (Topic Match): Khớp với các chủ đề trọng tâm (chánh niệm, buông bỏ, thiền, nghiệp báo,...).
* $G_p$ (Discussion Gap Potential): Tiềm năng mở ra một góc nhìn mới mà cộng đồng đang thiếu.

---

## 5. An Toàn Danh Tính Kênh (`@1995lido`)

* Hệ thống thực hiện kiểm tra `channel_handle == '@1995lido'` trước bất kỳ thao tác liên quan đến định danh kênh.
* Chế độ mặc định bắt buộc: `DRY_RUN = True`. Không bao giờ tự ý gửi comment lên YouTube mà không qua phê duyệt giám sát (Supervised Autopilot).
