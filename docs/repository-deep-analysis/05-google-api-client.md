# DEEP ANALYSIS 05: `google-api-python-client` (YouTube Data API v3)

* **Repository:** `googleapis/google-api-python-client`
* **License:** Apache-2.0
* **Role in BCE-Factory:** PRIMARY API Connector cho Channel Verification & Official Search

---

## 1. Phân Tích Cơ Chế Channel Identity Verification
Để đảm bảo an toàn tuyệt đối cho kênh mục tiêu `@1995lido`, việc xác thực danh tính dựa trên endpoint:
```python
youtube.channels().list(part="snippet,contentDetails,statistics", forHandle="1995lido").execute()
```
- Phản hồi từ Google cung cấp chính xác `channel_id`, `customUrl`, và tiêu đề chính thức của kênh.
- Nếu `channel_handle != '@1995lido'`, BCE-Factory kích hoạt **HARD STOP**, ngăn chặn mọi hành vi xuất bản hoặc điều hướng nhầm kênh.

## 2. Quản Trị Quota Thông Minh (Quota Stewardship)
- Gọi tìm kiếm (`search().list`) tiêu tốn 100 units quota/lần.
- Gọi chi tiết video hoặc comment (`commentThreads().list`) tiêu tốn 1 unit/lần.
- **Giải pháp tối ưu của BCE-Factory:** Sử dụng Discovery Agent kết hợp cache kết quả vào bảng `videos` SQLite. Chỉ quét các video mới chưa có trong cơ sở dữ liệu để bảo tồn quota API cả ngày.
