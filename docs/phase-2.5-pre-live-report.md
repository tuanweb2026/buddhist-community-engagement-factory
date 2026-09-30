# Phase 2.5 Pre-Live Audit & Fix Report

**System:** Buddhist Community Engagement Factory (`BCE-Factory`)  
**Target Channel:** `@1995lido`  
**Governing Rule:** *"Do not confuse automation with autonomy. Never alter facts to make reports look pretty."*  
**Date:** 2026-09-30  
**Phase:** 2.5 Pre-Live Blocker Remediation  

---

## 1. Tests Status

- **Unit & Regression Suite:** **22 / 22 test PASS** (100% via `PYTHONPATH=. .venv/bin/pytest -v`).
- **Pipeline Daily Dry-Run:** **PASS** (Hoàn thành mượt mà 8 bước qua lệnh `PYTHONPATH=. .venv/bin/python main.py daily --dry-run`).

---

## 2. LLM Availability

- **Gemini API Key:** `UNAVAILABLE` (Chưa điền trong `.env`).
- **OpenAI API Key:** `UNAVAILABLE`.
- **Cơ chế xử lý:** Hệ thống chuyển sang **Dynamic Parameterized Synthesis (Fallback Engine)** dựa trên băm định danh video (hash variation), kết hợp trực tiếp các điểm chứng cứ (Evidence Points) từ video research.
- **Safety Policy:**
  - `DRY_RUN`: Cho phép sinh và kiểm tra chất lượng candidates.
  - `LIVE PUBLISH`: **TỰ ĐỘNG CHẶN (ACTION = SKIP/DRY_RUN)** vì không đạt điều kiện tiên quyết về LLM dynamic generation và `HIGH` confidence.

---

## 3. Videos Processed & Selected

- **Kho lưu trữ:** 33+ video từ 10+ kênh khác nhau trong SQLite (`data/bce.db`).
- **Phiên Daily Test:** 2 video mới được chọn và duyệt comment (`8khM575Ye6E`, `1C159gQlzt4`).
- **Phiên Diversity Test 10 Video Độc Lập:** Chọn 10 video từ 10 kênh khác nhau (*1983dukkha, Ajahn Anan Dhamma, AudioBuddha, Buddha's Footsteps, Buddhism For Sleep, Buddhism Podcast, Can You Zen, Dalai Lama, Thích Pháp Hòa Canada, Giáo Lý Từ Đức Đạt Lai Lạt Ma*).

---

## 4. Candidates Generated vs Candidates Rejected

- **Số candidates sinh ra:** 30 candidates (3 candidates/video $\times$ 10 videos).
- **Candidates rejected:** 21 candidates (Loại trừ qua rào chắn kiểm tra trùng lặp trong batch và ưu tiên đa dạng phong cách).
- **Final candidates selected:** 9 candidates hợp lệ (1 video bị skip do trùng lặp semantic trong phiên).

---

## 5. Final Candidates & Diversity Statistics

| # | Channel | Style | Opening (Câu mở đầu) | Closing (Câu kết bài) |
| :-: | :--- | :---: | :--- | :--- |
| **01** | *1983dukkha* | `Reflective` | *Returning to the core teachings of mindfulness...* | *Warm gratitude for sharing these peaceful and grounding contemplation points.* |
| **02** | *Ajahn Anan Dhamma* | `Reflective` | *Listening to these reflections on mindfulness...* | *Simply resting in conscious awareness makes a quiet yet profound difference...* |
| **03** | *AudioBuddha* | `Insightful` | *A very practical take on applying mindfulness...* | *Holding expectations lightly often dissolves unnecessary friction...* |
| **04** | *Buddha's Footsteps* | `Reflective` | *A deeply calming reminder on the practice of...* | *May we all remember to return to our natural breath whenever overwhelm arises.* |
| **05** | *Buddhism For Sleep* | `Thoughtful Q` | *Such valuable insights. What specific daily habit...* | *...bridging formal meditation practice with unexpected interpersonal friction?* |
| **06** | *Buddhism Podcast* | `Insightful` | *What resonates most is the emphasis on kindness...* | *Allowing room for imperfection turns out to be the most genuine form of compassion.* |
| **07** | *Can You Zen* | `Insightful` | *The distinction highlighted here regarding...* | *True strength seems to lie in our willingness to remain open and humble.* |
| **08** | *Dalai Lama* | `Thoughtful Q` | *Deeply appreciate this clarity on mindfulness...* | *...maintain mindful balance when work deadlines demand intense mental focus?* |
| **09** | *Giáo Lý Đạt Lai Lạt Ma* | `Reflective` | *Theo dõi bài giảng về phật pháp ứng dụng...* | *Xin tri ân những giáo lý giản dị mà thấm thía được trao gửi hôm nay.* |

### Chỉ số đa dạng định lượng (Diversity Metrics):
- **Tỷ lệ mở đầu độc bản (Unique Openings):** **9 / 9 (100% độc bản)** *(Cải thiện vượt bậc so với 3/10 ở bản cũ).*
- **Tỷ lệ kết bài độc bản (Unique Closings):** **9 / 9 (100% độc bản)** *(Cải thiện vượt bậc so với 2/10 ở bản cũ).*
- **Phân bổ phong cách (Style Diversity):**
  - `Reflective`: 4 / 9 (44.4%)
  - `Insightful`: 3 / 9 (33.3%)
  - `Thoughtful Question`: 2 / 9 (22.2%)
- **Cụm 3 từ lặp nhiều nhất:** Chỉ còn các thuật ngữ Phật học cốt lõi như `"mindfulness, compassion &"` (4 lần) và `"compassion & inner"` (4 lần). **Hoàn toàn biến mất các cụm rập khuôn văn mẫu** như `"this talk brings"`, `"such a grounding"`.

---

## 6. Evidence & Context Grounding Statistics

- **Mọi final candidate đều liên kết với ít nhất 1 `evidence_point`:**
  - Ví dụ: `primary_evidence = "observing the rise and fall of thoughts without judgment"` được lồng trực tiếp vào Candidate #04.
  - Ví dụ: `secondary_evidence = "applying the teachings of impermanence to reduce daily anxiety"` được tích hợp vào Candidate #06.
- **Tỷ lệ có bằng chứng ngữ cảnh (Evidence Grounding):** **9 / 9 (100% PASS)**.

---

## 7. Confidence & Safety Statistics

- **Phân bổ Confidence:**
  - `HIGH`: 0 / 10 (Do chưa có transcript đầy đủ kết hợp LLM API key).
  - `MEDIUM`: 2 / 10.
  - `LOW`: 8 / 10.
- **Quy tắc an toàn Live Publish:** Hệ thống chặn 100% các bình luận có `confidence != HIGH` khi chạy ở chế độ xuất bản thật.
- **Published Comments trên YouTube:** **0 (Hoàn toàn bằng 0, chỉ lưu `DRY_RUN` trong DB)**.

---

## 8. Duplicate Protection Statistics

- **Exact Duplicate:** 0
- **Semantic Duplicate Rejected:** Đã chặn thành công 1 video có độ tương đồng ngữ nghĩa vượt ngưỡng 0.70 trong batch.
- **Repeated Openings / Closings Rejected:** Đã chặn hoàn toàn việc tái sử dụng cùng 1 câu mở đầu hoặc kết bài trong cùng một phiên xử lý.

---

## 9. Remaining Problems

1. **Chưa có LLM API Key (GEMINI_API_KEY):** Dù Dynamic Parameterized Synthesis giải quyết xuất sắc việc lặp câu chữ và phân bổ phong cách, việc phân tích sâu các ẩn ý vi tế độc nhất của bài giảng vẫn phụ thuộc vào Gemini Flash khi có key.
2. **Transcript Availability:** Đa số video quốc tế và bài giảng dài tắt tính năng Closed Captions của bên thứ 3, đòi hỏi phụ thuộc vào mô tả và comment sample của cộng đồng.

---

## 10. LIVE PILOT READINESS

```text
NOT_READY
```

### Lý do (Technical Justification):
Theo quy tắc an toàn nghiêm ngặt của Phase 2.5: **Chỉ những candidate đạt mức `research_confidence == 'HIGH'` và được sinh ra từ LLM Dynamic Generation mới được phép Live Publish**. Hiện tại do chưa cấu hình `GEMINI_API_KEY`, hệ thống đang vận hành ở chế độ Fallback Synthesis (mức `MEDIUM` / `LOW`). Mặc dù code đã hoàn toàn an toàn và 100% đa dạng trong Dry-Run, hệ thống giữ đúng kỷ luật dừng lại ở trạng thái `NOT_READY` cho đến khi có API Key chính thức để kích hoạt mức `HIGH`.
