# CODE ADOPTION MATRIX — BCE-FACTORY v1.0

Bảng ma trận quyết định tái sử dụng, thích ứng hoặc tự xây dựng cho từng thành phần trong hệ thống BCE-Factory.

| Thành phần hệ thống | Repository nguồn | Hành động (Action) | Lý do kỹ thuật | Bản quyền (License) |
| :--- | :--- | :--- | :--- | :--- |
| **YouTube Discovery (Official)** | `googleapis/google-api-python-client` | **PRIMARY (API First)** | Chuẩn chính thức từ Google, xác thực an toàn kênh `@1995lido` | Apache-2.0 |
| **YouTube Metadata & Fallback** | `yt-dlp/yt-dlp` | **PRIMARY (Tier 2 Scraper)** | Cào metadata & comment chất lượng cao khi không có API key | Unlicense |
| **Transcript Extraction** | `jdepoix/youtube-transcript-api` | **PRIMARY (Tier 1)** | Lấy phụ đề đa ngữ có timestamp, không cần headless browser | MIT |
| **Data Schema & Validation** | `pydantic/pydantic` | **DEPENDENCY** | Định nghĩa I/O an toàn, chống lỗi type giữa 10 agents | MIT |
| **Quality Gate Architecture** | `guardrails-ai/guardrails` | **ADAPT** | Áp dụng triết lý Fail-fast 10 gates nhị phân (Pass/Fail) | Apache-2.0 |
| **State & Interruption Flow** | `langchain-ai/langgraph` | **ARCHITECTURE REFERENCE** | Mô hình ngắt dừng con người giám sát (Supervised Autopilot) | MIT |
| **3-Tier Memory System** | `mem0ai/mem0` | **ARCHITECTURE REFERENCE** | Thiết kế bộ nhớ ngắn hạn, trung hạn và dài hạn cho agent | Apache-2.0 |
| **Retry & Rate Limit Safety** | `jd/tenacity` | **DEPENDENCY** | Cơ chế exponential backoff tối đa 3 lần khắc phục an toàn | Apache-2.0 |
| **Terminal Dashboard & UI** | `Textualize/rich` | **DEPENDENCY** | Hiển thị Funnel và trạng thái 10 Quality Gates trực quan | MIT |
| **Scheduler & Webhook Layer** | `n8n-io/n8n` | **ARCHITECTURE REFERENCE** | Tách rời tầng tự động hóa lịch trình với tầng trí tuệ nhân tạo | Sustainable Use |
| **Browser Automation (Selenium)**| `verlorengest/YScraper` | **REJECT** | Dễ bị Google checkpoint/khóa tài khoản `@1995lido`, không an toàn | GPL-3.0 |
| **Spam / Bot Auto-poster** | `spambot-example/yt-bot` | **REJECT** | Vi phạm nghiêm trọng nguyên tắc cấm spam và chính sách YouTube | None |

---

## 🎯 Intellectual Property (IP) Riêng Biệt Do BCE-Factory Tự Xây

Những giá trị cốt lõi KHÔNG sao chép từ bất kỳ repository nào mà do BCE-Factory tự nghiên cứu và phát triển:

1. **Buddhist Opportunity Ranking Formula**: Công thức chấm điểm 6 trọng số đánh giá tiềm năng đàm đạo Phật giáo.
2. **Video Knowledge Card Builder**: Đúc kết luận điểm bài giảng dựa trên bằng chứng (Never Hallucinate).
3. **Discussion Gap Detector**: Thuật toán tìm kiếm "khoảng trống thảo luận" mà người xem đang khao khát.
4. **Buddhist Context Identifier**: Tự động nhận diện trường phái (Thiền Làng Mai, Bắc tông, Nam tông) để chuẩn hóa văn phong khiêm cung, thanh tịnh.
5. **Value-First Comment Generator**: Sinh 3 Candidates độc bản (Reflective, Insightful, Question-based) mang giá trị chữa lành.
6. **10 Non-Compromising Quality Gates**: Hàng rào kiểm duyệt tự động ngăn chặn hoàn toàn self-promotion và quote giả.
7. **Identity Hard Stop Gate**: Ngắt dừng tuyệt đối nếu tài khoản không phải `@1995lido`.
