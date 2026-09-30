# DEEP ANALYSIS 01: `youtube-transcript-api`

* **Repository:** `jdepoix/youtube-transcript-api`
* **Version/Commit:** Latest stable (2026)
* **License:** MIT
* **Role in BCE-Factory:** PRIMARY Dependency cho `TranscriptAgent`

---

## 1. Kiến Trúc & Cách Thức Hoạt Động (Source Code Analysis)

Thư viện giao tiếp trực tiếp với YouTube player web client:
1. Gửi HTTP GET request tới trang watch: `https://www.youtube.com/watch?v={video_id}`.
2. Trích xuất biến JSON `ytInitialPlayerResponse` chứa đối tượng `captions.playerCaptionsTracklistRenderer`.
3. Phân tích danh sách `captionTracks` để lấy danh sách ngôn ngữ sẵn có (`languageCode`, `kind`).
4. Tải xuống file XML/JSON phụ đề chứa thẻ `<text start="..." dur="...">`.
5. Parse thành list các dict `[{'text': ..., 'start': ..., 'duration': ...}]`.

## 2. Ưu Điểm Kỹ Thuật
- **Hoàn toàn không cần API Key:** Tiết kiệm 100% quota YouTube Data API v3 cho các tác vụ khác.
- **Tốc độ cực nhanh:** Chỉ mất khoảng 300–600ms cho mỗi video.
- **Hỗ trợ tự động tạo phụ đề:** Lấy được cả phụ đề do người dùng tải lên lẫn phụ đề do YouTube AI tự tạo (`kind='asr'`).

## 3. Rủi Ro & Giải Pháp Tự Phục Hồi Cho BCE-Factory
- **Lỗi `TranscriptsDisabled` / `NoTranscriptFound`:** Khoảng 15–20% video Phật giáo không có phụ đề.
- **Cơ chế xử lý của BCE-Factory:** Khi bắt được ngoại lệ này, `TranscriptAgent` lập tức gắn nhãn `source='FALLBACK_METADATA'`, kích hoạt `VideoResearchAgent` sử dụng tiêu đề bài giảng và mô tả chi tiết của video để phân tích ngữ cảnh, bảo đảm quy trình không bị đứt đoạn.
