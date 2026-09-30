# DEEP ANALYSIS 02: `yt-dlp`

* **Repository:** `yt-dlp/yt-dlp`
* **License:** Unlicense
* **Role in BCE-Factory:** PRIMARY Fallback Scraper cho `DiscoveryAgent` và `CommentIntelligenceAgent`

---

## 1. Phân Tích Cơ Chế Trích Xuất Bình Luận (`getcomments`)
- `yt-dlp` phân tích request AJAX `browse` endpoint của YouTube với payload `continuation_token`.
- Giải mã định dạng protobuf / innerTube API (`android` / `web` client context).
- Trích xuất cấu trúc comment:
  - `comment_id`, `author`, `author_id`
  - `text` (đã loại bỏ html tags)
  - `like_count`, `timestamp`
  - `is_pinned`, `author_is_uploader`

## 2. Bài Học Thiết Kế Áp Dụng Cho BCE-Factory
- Để tránh bị YouTube trả về trang "The page needs to be reloaded", cần thiết lập cấu hình:
  ```python
  extractor_args = {'youtube': {'player_client': ['web', 'android']}}
  user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
  ```
- **Filter & Sort:** Luôn sắp xếp comment theo `like_count` giảm dần để ưu tiên thu thập những ý kiến có mức độ đồng thuận cao nhất của cộng đồng Phật tử.
