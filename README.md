# ☸️ BUDDHIST COMMUNITY ENGAGEMENT FACTORY
> Hệ thống AI tự động tìm kiếm video Phật giáo nổi tiếng, phân tích cảm xúc & trăn trở của cộng đồng, từ đó sáng tạo những bình luận đắt giá nhằm kết duyên và điều hướng người xem tinh tế về channel **@1995lido**.

---

## 🌟 Tính Năng Nổi Bật

1. **Quét Video & Bình Luận Tự Động (Không bắt buộc YouTube API Key)**:
   - Tự động tìm kiếm video theo các từ khóa Phật giáo nổi tiếng (Thầy Thích Pháp Hòa, Thiền sư Thích Nhất Hạnh, nghe pháp thoại an lạc, kinh dược sư,...).
   - Tự động cào Top bình luận được yêu thích nhất để lắng nghe trăn trở của người xem.
2. **AI Thấu Cảm & Phân Tích Điểm Chạm (Emotional Insights)**:
   - Đúc kết thông điệp cốt lõi của bài pháp.
   - Bắt trọn cảm xúc người nghe (bế tắc, mệt mỏi, sám hối, tìm kiếm tĩnh lặng).
   - Xác định "nỗi đau" và trăn trở phổ biến của cộng đồng Phật tử / người trẻ.
3. **Bộ Sinh Comment Chiến Lược (Strategic Value-First Comments)**:
   - Tạo ra 4 phong cách bình luận:
     - 🧘 **Đúc kết triết lý sâu sắc (Philosophical)**
     - 🌿 **Đồng cảm & Chữa lành (Empathy & Healing)**
     - 📖 **Kể chuyện & Chiêm nghiệm (Storytelling)**
     - 🙏 **Tri ân & Lan tỏa năng lượng lành (Gratitude)**
   - **Cam kết**: 100% bình luận mang tính cống hiến giá trị, thanh tao, tự nhiên, **tuyệt đối không dùng văn phong spam**.
   - Khéo léo nhắc đến channel **@1995lido** như một góc tĩnh lặng kết duyên.
4. **Cơ Sở Dữ Liệu SQLite**:
   - Lưu trữ toàn bộ dữ liệu video, bình luận, insight và các mẫu gợi ý.
5. **Dashboard Dòng Lệnh Trực Quan & Tự Động Hóa Lập Lịch**:
   - Xem bảng xếp hạng video, xem chi tiết phân tích và copy comment nhanh chóng.
   - Bộ scheduler chạy nền tự động quét theo chu kỳ giờ đã thiết lập.

---

## 🚀 Hướng Dẫn Cài Đặt & Sử Dụng

### 1. Cấu hình môi trường
Sao chép file `.env.example` thành `.env`:
```bash
cp .env.example .env
```
Mở file `.env` và điền:
- `GEMINI_API_KEY`: Lấy miễn phí tại [Google AI Studio](https://aistudio.google.com/app/apikey).
- Hoặc `OPENAI_API_KEY`.
*(Lưu ý: Nếu chưa nhập key, hệ thống vẫn hoạt động mượt mà với bộ mẫu chiến lược chất lượng cao).*

### 2. Chạy thử nghiệm 1 lượt quét
Kích hoạt môi trường ảo và chạy:
```bash
.venv/bin/python pipeline.py --keywords "thuyết pháp Thích Pháp Hòa" --max_videos 2
```

### 3. Xem kết quả và lấy comment
- **Liệt kê danh sách video đã phân tích:**
  ```bash
  .venv/bin/python viewer.py list
  ```
- **Xem phân tích chi tiết & các mẫu comment của 1 video cụ thể:**
  ```bash
  .venv/bin/python viewer.py view <VIDEO_ID>
  ```
- **Xuất toàn bộ báo cáo chiến lược ra file Markdown:**
  ```bash
  .venv/bin/python viewer.py export
  ```

### 4. Chạy chế độ Tự Động Hoá Hoàn Toàn (Background Scheduler)
Để hệ thống tự động quét mỗi 6 tiếng một lần:
```bash
.venv/bin/python scheduler.py
```
