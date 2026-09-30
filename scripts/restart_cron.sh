#!/usr/bin/env bash
# ==============================================================================
# BCE Factory — Restart & Reinstall Scheduler
# 1. Kiểm tra crontab hiện tại
# 2. Backup cron configuration
# 3. Gỡ bỏ BCE cron block cũ
# 4. Cài đặt lại 7 jobs + 1 watchdog + startup check
# 5. Verify & Chạy Health Check
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

START_MARKER="# === BCE FACTORY SCHEDULER START ==="
END_MARKER="# === BCE FACTORY SCHEDULER END ==="

echo "Stopping BCE Factory scheduler..."

CURRENT_CRON=$(crontab -l 2>/dev/null || true)

# 2. Backup
BACKUP_FILE="$LOG_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
if [[ -n "$CURRENT_CRON" ]]; then
    echo "$CURRENT_CRON" > "$BACKUP_FILE"
fi

# 3. Lọc bỏ block BCE cũ, giữ nguyên 100% các cron jobs khác của người dùng
CLEANED_CRON=""
if [[ -n "$CURRENT_CRON" ]]; then
    CLEANED_CRON=$(echo "$CURRENT_CRON" | sed "/$START_MARKER/,/$END_MARKER/d")
fi

echo "Installing BCE Factory scheduler..."

# 4. Soạn thảo khối cron chuẩn của BCE Factory
NEW_BCE_BLOCK=$(cat <<EOF
$START_MARKER
# Environment Setup
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
PYTHONPATH=$PROJECT_DIR

# 1. Quét Discovery & Đồng bộ Radar (07:30 sáng)
30 7 * * * cd "$PROJECT_DIR" && "$PYTHON_BIN" main.py discovery >> "$LOG_DIR/cron_discovery.log" 2>&1

# 2. Nghiên cứu sâu Video Knowledge Cards (09:00 sáng)
0 9 * * * cd "$PROJECT_DIR" && "$PYTHON_BIN" main.py research >> "$LOG_DIR/cron_research.log" 2>&1

# 3. Khung tương tác #1 (10:30 trưa)
30 10 * * * cd "$PROJECT_DIR" && "$PYTHON_BIN" main.py engagement-1 >> "$LOG_DIR/cron_engagement_1.log" 2>&1

# 4. Khung tương tác #2 (13:30 chiều)
30 13 * * * cd "$PROJECT_DIR" && "$PYTHON_BIN" main.py engagement-2 >> "$LOG_DIR/cron_engagement_2.log" 2>&1

# 5. Khung tương tác #3 (16:30 chiều)
30 16 * * * cd "$PROJECT_DIR" && "$PYTHON_BIN" main.py engagement-3 >> "$LOG_DIR/cron_engagement_3.log" 2>&1

# 6. Khung tương tác #4 (20:30 tối)
30 20 * * * cd "$PROJECT_DIR" && "$PYTHON_BIN" main.py engagement-4 >> "$LOG_DIR/cron_engagement_4.log" 2>&1

# 7. Xuất Báo Cáo Kiểm Toán Ngày & Chiến lược Lido (23:00 tối)
0 23 * * * cd "$PROJECT_DIR" && "$PYTHON_BIN" main.py daily_report >> "$LOG_DIR/cron_daily_report.log" 2>&1

# Watchdog định kỳ 15 phút (Giám sát hạ tầng, phát hiện treo job, KHÔNG tự publish)
*/15 * * * * bash "$PROJECT_DIR/scripts/watchdog.sh" >> "$LOG_DIR/watchdog.log" 2>&1

# Startup / Reboot Verification định kỳ
*/30 * * * * bash "$PROJECT_DIR/scripts/startup_check.sh" >> "$LOG_DIR/startup.log" 2>&1
$END_MARKER
EOF
)

# Ghi đè vào crontab
if [[ -n "$CLEANED_CRON" ]]; then
    FINAL_CRON="${CLEANED_CRON}"$'\n'"${NEW_BCE_BLOCK}"
else
    FINAL_CRON="${NEW_BCE_BLOCK}"
fi

echo "$FINAL_CRON" | crontab -

echo "Verifying scheduler..."
"$PYTHON_BIN" main.py cron-status

echo "Health check..."
"$PYTHON_BIN" main.py health

echo ""
echo "BCE Factory scheduler restarted successfully."
