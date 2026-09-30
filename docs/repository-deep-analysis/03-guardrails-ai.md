# DEEP ANALYSIS 03: `guardrails-ai`

* **Repository:** `guardrails-ai/guardrails`
* **License:** Apache-2.0
* **Role in BCE-Factory:** ADAPT Architecture cho `CommentQualityGateAgent`

---

## 1. Phân Tích Cơ Chế Guardrails & Validation Logic
- Framework xây dựng kiến trúc dạng Middleware Interceptor:
  `LLM Output` $\rightarrow$ `Validator 1` $\rightarrow$ `Validator 2` $\rightarrow$ ... $\rightarrow$ `Verified Output`.
- Mỗi Validator thực thi độc lập và trả về:
  - `PassResult`: Hợp lệ, cho phép đi tiếp.
  - `FailResult(error_message, fix_value)`: Không hợp lệ, kích hoạt logic sửa lỗi hoặc dừng lại.

## 2. Cách BCE-Factory Tiếp Thu & Tối Ưu Hóa
- **Không cài đặt nguyên khối cồng kềnh:** Thay vì kéo hàng chục package nặng nề của hub, BCE-Factory tiếp thu triết lý kiến trúc và triển khai thành **10 Quality Gates thuần Python**:
  - Deterministic checks (RegEx, keyword matching cho GATE 06, 07, 09, 10).
  - Semantic checks (Topic relevance, hallucination detection cho GATE 01, 02, 05).
- **Quy tắc bất khả xâm phạm:** Không tính trung bình cộng. Một cổng lỗi $\rightarrow$ REJECT toàn diện.
