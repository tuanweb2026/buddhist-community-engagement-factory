# AGENTS SPECIFICATION & GOVERNANCE

**System:** Buddhist Community Engagement Factory (`BCE-Factory`)  
**Target Channel:** `@1995lido`  
**Governing Rule:** *"Do not confuse automation with autonomy."*  

---

## 1. Nguyên Tắc Cốt Lõi (Core Directive)

> **Do not confuse automation with autonomy.**
>
> Hệ thống được phép tự động hoá nghiên cứu, tìm kiếm, phân tích, sinh bản nháp, kiểm thử, chẩn đoán và khắc phục lỗi implementation an toàn.
>
> **TUYỆT ĐỐI KHÔNG** được tự ý mở rộng quyền hạn của chính nó (ví dụ: tự dùng bot browser để qua mặt API, tự đổi tài khoản YouTube khác, hoặc tự ý tăng tần suất bình luận khi tương tác thấp). Mọi hành động mở rộng đều phải thông qua Architecture & Safety Gate.

---

## 2. Danh Sách 10 Agents Bắt Buộc

### 1. `buddhist-discovery-agent`
* **Nhiệm vụ:** Tìm kiếm video/kênh theo từ khóa Phật giáo (Anh & Việt), deduplicate video đã quét.
* **Input Schema:** `keywords: List[str]`, `languages: ['vi', 'en']`, `limit: int`
* **Output Schema:** `List[DiscoveredVideo]` (video_id, title, channel_id, url, metrics, ...)

### 2. `opportunity-ranker-agent`
* **Nhiệm vụ:** Chấm điểm Opportunity Score (0.0 - 1.0) dựa trên 6 yếu tố trọng số.
* **Input Schema:** `DiscoveredVideo`
* **Output Schema:** `OpportunityScoreResult` (score, breakdown, recommended_for_research: bool)

### 3. `video-research-agent`
* **Nhiệm vụ:** Xây dựng **Video Knowledge Card** (core_topic, main_claims, key_points, emotional_themes, uncertainties, evidence).
* **Input Schema:** `video_id`, `title`, `description`, `transcript`
* **Output Schema:** `VideoKnowledgeCard`

### 4. `transcript-agent`
* **Nhiệm vụ:** Thu thập phụ đề chính thức qua `youtube-transcript-api` hoặc fallback metadata.
* **Input Schema:** `video_id`, `preferred_languages: ['vi', 'en']`
* **Output Schema:** `TranscriptResult` (text, segments, confidence, source)

### 5. `buddhist-context-agent`
* **Nhiệm vụ:** Định danh truyền thống Phật giáo (Theravada, Zen, Bắc tông, Làng Mai,...), xác thực các khái niệm chánh niệm/giáo lý.
* **Input Schema:** `VideoKnowledgeCard`
* **Output Schema:** `BuddhistContext` (tradition, key_concepts, appropriate_tone)

### 6. `comment-intelligence-agent`
* **Nhiệm vụ:** Phân loại comment theo 11 nhóm (QUESTION, INSIGHT, PERSONAL_EXPERIENCE, AGREEMENT, DISAGREEMENT, GRATITUDE, CONFUSION, DISCUSSION, REPETITION, LOW_VALUE, SPAM).
* **Input Schema:** `List[RawComment]`
* **Output Schema:** `CommentAnalysisReport` (clusters, unanswered_questions, emotional_pulse)

### 7. `discussion-gap-agent`
* **Nhiệm vụ:** Tìm ra "điểm thiếu vắng" có giá trị trong cuộc thảo luận hiện tại mà người xem đang khao khát.
* **Input Schema:** `VideoKnowledgeCard`, `CommentAnalysisReport`
* **Output Schema:** `DiscussionGapResult` (gap_type, description, evidence_comment_ids, confidence)

### 8. `buddhist-comment-writer-agent`
* **Nhiệm vụ:** Tạo 3 ứng viên comment độc bản:
  * **Candidate A (Reflective):** Trầm lắng, đúc kết, chiêm nghiệm.
  * **Candidate B (Insightful):** Sâu sắc, chỉ ra góc nhìn ứng dụng thực tế.
  * **Candidate C (Question-based):** Đặt câu hỏi gợi mở, kích thích tư duy thiện lành.
* **Input Schema:** `VideoKnowledgeCard`, `DiscussionGapResult`, `BuddhistContext`
* **Output Schema:** `List[CommentCandidate]`

### 9. `comment-quality-gate-agent`
* **Nhiệm vụ:** Kiểm duyệt qua **10 Quality Gates**. Bất kỳ gate trọng yếu nào fail $\rightarrow$ REJECT ngay lập tức.
* **Input Schema:** `CommentCandidate`, `VideoKnowledgeCard`, `DiscussionGapResult`
* **Output Schema:** `QualityEvaluationResult` (passed: bool, gate_results: Dict[str, GateStatus], rejection_reason: Optional[str])

### 10. `engagement-analytics-agent`
* **Nhiệm vụ:** Ghi nhận phản hồi thực tế, lưu trữ vào 3 tầng bộ nhớ (Short/Medium/Long-Term Memory) để tối ưu hóa liên tục.
* **Input Schema:** `action_id`, `feedback_metrics`
* **Output Schema:** `MemoryUpdateReport`
