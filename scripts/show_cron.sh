#!/usr/bin/env bash
# ==============================================================================
# BCE Factory — Show Raw Cron Configuration
# Hiển thị toàn bộ khối cấu hình Cron của BCE Factory (Không hiển thị bí mật)
# ==============================================================================

CRON_RAW=$(crontab -l 2>/dev/null)

START_MARKER="# === BCE FACTORY SCHEDULER START ==="
END_MARKER="# === BCE FACTORY SCHEDULER END ==="

if [[ -z "$CRON_RAW" ]]; then
    echo "Không tìm thấy crontab trên hệ thống macOS (Crontab rỗng)."
    exit 0
fi

if [[ "$CRON_RAW" != *"$START_MARKER"* ]]; then
    echo "Crontab hệ thống đang hoạt động nhưng CHƯA CÀI ĐẶT khối BCE Factory scheduler."
    exit 0
fi

echo "================================================================="
echo "        BCE FACTORY RAW CRON BLOCK (SAFE VIEW)"
echo "================================================================="

# Trích xuất phần giữa START_MARKER và END_MARKER
echo "$CRON_RAW" | sed -n "/$START_MARKER/,/$END_MARKER/p" | while IFS= read -r line; do
    # Ẩn các key hoặc secret nếu tình cờ xuất hiện trên dòng lệnh
    SAFE_LINE=$(echo "$line" | sed -E 's/(AIzaSy[A-Za-z0-9_-]{30})/[REDACTED_API_KEY]/g' | sed -E 's/(AQ\.[A-Za-z0-9_-]{30})/[REDACTED_GEMINI_KEY]/g')
    echo "$SAFE_LINE"
done

echo "================================================================="
