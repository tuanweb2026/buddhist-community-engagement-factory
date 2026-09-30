#!/usr/bin/env bash
# ==============================================================================
# BCE Factory — Log Viewer Helper
# Hỗ trợ:
# bash scripts/logs.sh            -> Hiển thị 30 dòng log mới nhất
# bash scripts/logs.sh today      -> Hiển thị log của hôm nay
# bash scripts/logs.sh errors     -> Lọc riêng các dòng lỗi/cảnh báo
# bash scripts/logs.sh engagement -> Xem log của tiến trình tương tác
# ==============================================================================

LOG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/logs"
mkdir -p "$LOG_DIR"

MODE="${1:-recent}"
TODAY=$(date "+%Y-%m-%d")

echo "================================================================="
echo "                BCE FACTORY LOG VIEWER ($MODE)"
echo "================================================================="

case "$MODE" in
    "today")
        echo "=== [LOGS HÔM NAY: $TODAY] ==="
        find "$LOG_DIR" -type f -name "*.log" -exec grep -H "$TODAY" {} + 2>/dev/null | tail -n 50 || echo "Chưa có log ngày hôm nay."
        ;;
    "errors")
        echo "=== [LỌC CÁC DÒNG ERROR / ALERT / FAIL] ==="
        find "$LOG_DIR" -type f -name "*.log" -exec grep -Ei "error|fail|alert|exception|stale" {} + 2>/dev/null | tail -n 50 || echo "Không phát hiện dòng lỗi nào."
        ;;
    "engagement")
        echo "=== [LOGS TIẾN TRÌNH ENGAGEMENT] ==="
        cat "$LOG_DIR"/cron_engagement_*.log 2>/dev/null | tail -n 50 || echo "Chưa có log engagement."
        ;;
    *)
        echo "=== [30 DÒNG LOG HỆ THỐNG MỚI NHẤT] ==="
        find "$LOG_DIR" -type f -name "*.log" -exec tail -n 5 {} + 2>/dev/null | tail -n 35 || echo "Chưa có log hệ thống."
        ;;
esac

echo "================================================================="
