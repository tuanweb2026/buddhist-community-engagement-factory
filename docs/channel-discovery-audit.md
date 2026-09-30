# Channel Discovery Architecture & Audit Report

**Date:** 2026-09-30  
**Target Channel:** `@1995lido`  
**Auditor:** Antigravity (Implementation Agent)  
**Rule:** *"Do not confuse automation with autonomy. Never alter facts to make reports look pretty."*  

---

## 1. Bản Chất Của 5 Kênh Radar Được Báo Cáo

Trong báo cáo tích hợp trước đó, 5 kênh xuất hiện trong Channel Radar là:
1. *Làng Mai - Plum Village* (`@plumvillage`)
2. *Pháp Âm Thầy Thích Pháp Hòa* (`@phapamthaythichphaphoa`)
3. *Thích Minh Niệm - Hiểu Về Trái Tim* (`@thichminhniem`)
4. *Buddhist Society of Western Australia (BSWA)* (`@buddhistsocietywa`)
5. *Yuttadhammo Bhikkhu* (`@yuttadhammo`)

### 🔍 Kết Quả Kiểm Toán Thực Tế:
- **Câu hỏi 1: Những channel này có được Channel Radar tự discovery không? Hay được seed/configuration trước?**
  - **Sự thật kỹ thuật:** 5 channel trên **ĐƯỢC CẤU HÌNH TRƯỚC (Pre-configured Seed Channels)** trong tệp `channel_radar.py` tại biến `SEED_CHANNELS` (dòng 22–83).
  - Hệ thống chưa tự động search ra các kênh mới bằng YouTube API query trong runtime này vì `YOUTUBE_API_KEY` công khai trong `.env` chưa được điền. Khi API key trống hoặc DB chưa có dữ liệu kênh, hàm `initialize_seeds()` sẽ nạp danh sách 5 kênh uy tín này làm gốc để theo dõi.
- **Câu hỏi 2: Tại sao các video được chọn lại thuộc "Buddhism Podcast" hay "AudioBuddha"?**
  - **Sự thật kỹ thuật:** Các video này được tìm ra bởi **Discovery Path 1 (Phase 1 Video Discovery)** thông qua thư viện `yt-dlp` dựa trên danh sách từ khóa tìm kiếm (`DISCOVERY_KEYWORDS` như `"Vipassana mindfulness meditation"`, `"Ajahn Chah teachings"`).

---

## 2. Kiến Trúc Hai Nhánh Tìm Kiếm Song Song (Dual-Path Discovery Architecture)

Trong mã nguồn `main.py` hiện tại, hệ thống vận hành **2 Discovery Paths song song**:

```text
                                       ┌───────────────────────────────────┐
                                       │     BUDDHIST ENGAGEMENT ENGINE    │
                                       └─────────────────┬─────────────────┘
                                                         │
                        ┌────────────────────────────────┴────────────────────────────────┐
                        ▼                                                                 ▼
      ┌───────────────────────────────────┐                             ┌───────────────────────────────────┐
      │          DISCOVERY PATH A         │                             │          DISCOVERY PATH B         │
      │   Channel Radar & Channel Intel   │                             │  Video Discovery Engine (Keyword) │
      │      (`channel_radar.py`)         │                             │          (`discovery.py`)         │
      └─────────────────┬─────────────────┘                             └─────────────────┬─────────────────┘
                        │                                                                 │
      • Quản lý các kênh hạt giống uy tín                                • Tìm kiếm theo 8 từ khóa Phật giáo
        (Plum Village, Pháp Hòa, Minh Niệm...)                            bằng `yt-dlp` hoặc YouTube Search API.
      • Phân tầng Tier (A_MAJOR, B_STRONG...)                           • Quét trên toàn bộ YouTube, phát hiện
      • Đọc metadata, phân tích 3 lớp                                     các video có lượt xem cao (vd: Buddhism
        (Observation, Interpretation, Opportunity).                       Podcast, AudioBuddha, Samaneri...).
                        │                                                                 │
                        ▼                                                                 ▼
      ┌───────────────────────────────────┐                             ┌───────────────────────────────────┐
      │      Channel Recent Video Scan    │                             │      Keyword Search Video Pool    │
      │       (`video_inventory.py`)      │                             │         (5-10 videos/run)         │
      └─────────────────┬─────────────────┘                             └─────────────────┬─────────────────┘
                        │                                                                 │
                        └────────────────────────────────┬────────────────────────────────┘
                                                         │
                                                         ▼
                                       ┌───────────────────────────────────┐
                                       │       VIDEO INVENTORY POOL        │
                                       │     (Deduplicated Ingestion)      │
                                       └─────────────────┬─────────────────┘
                                                         │
                                                         ▼
                                       ┌───────────────────────────────────┐
                                       │       VIDEO PRIORITY QUEUE        │
                                       │  (Tier, Recency, Comment Ratio)   │
                                       └─────────────────┬─────────────────┘
                                                         │
                                                         ▼
                                       Top 3–5 Videos For Deep Research
```

### Đánh giá kiến trúc:
- **Ưu điểm:** Vừa đảm bảo luôn có sự hiện diện của các kênh Phật giáo chính thống uy tín (Path A), vừa linh hoạt bắt được các video đang thịnh hành hoặc podcast Phật giáo quốc tế có thảo luận sôi nổi từ tìm kiếm từ khóa tự nhiên (Path B).
- **Hạn chế kỹ thuật hiện tại:** Danh sách kênh trong Path A hiện là Seed cố định, chưa có module tự động mở rộng channel pool từ kết quả tìm kiếm của Path B.

---

## 3. Bảng Điểm Chi Tiết Của Các Kênh Radar (Exposed Channel Score Breakdown)

Công thức tính điểm minh bạch có thể kiểm toán:
- **Subscriber Score (tối đa 30đ):** $\min(30.0, (\text{subs} / 1,000,000) \times 30.0 + 5.0)$
- **Recent Activity Score (tối đa 20đ):** Dựa trên kho video (>1,000 video = 18đ; >400 video = 15đ)
- **View Scale Score (tối đa 20đ):** Tier A (18đ), Tier B (14đ)
- **Like Engagement Score (tối đa 10đ):** Tỷ lệ phản hồi tích cực (9.0đ)
- **Comment Discussion Depth (tối đa 10đ):** Độ sâu thảo luận (Tier A = 9.0đ, Tier B = 8.0đ)
- **Content Relevance (tối đa 10đ):** Tính chuẩn mực Phật giáo (10.0đ)

| Channel Name | Subscribers | Sub Score (/30) | Activity (/20) | View (/20) | Like (/10) | Comment (/10) | Relevance (/10) | Final Score (/100) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Làng Mai - Plum Village** | 850,000 | 30.0 | 18.0 | 18.0 | 9.0 | 9.0 | 10.0 | **94.0** |
| **Pháp Âm Thầy Thích Pháp Hòa** | 620,000 | 23.6 | 15.0 | 18.0 | 9.0 | 9.0 | 10.0 | **84.6** |
| **Thích Minh Niệm - Hiểu Về Trái Tim** | 450,000 | 18.5 | 15.0 | 18.0 | 9.0 | 9.0 | 10.0 | **79.5** |
| **BSWA (Ajahn Brahm)** | 280,000 | 13.4 | 18.0 | 18.0 | 9.0 | 9.0 | 10.0 | **77.4** |
| **Yuttadhammo Bhikkhu** | 140,000 | 9.2 | 18.0 | 14.0 | 9.0 | 8.0 | 10.0 | **68.2** |

---

## 4. Kết Luận Audit
- **Channel Radar hiện tại:** Đạt **PARTIAL**. 5 kênh được xếp hạng và phân tích là những kênh Phật giáo hàng đầu có thật, nhưng nguồn gốc ban đầu là **Seed List được cấu hình sẵn**, chưa phải là Dynamic Discovery độc lập hoàn toàn.
- **Tính an toàn:** Không có hiện tượng bịa đặt dữ liệu ảo; các kênh được gán Tier chính xác theo quy mô thực tế.
