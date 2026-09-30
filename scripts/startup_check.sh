#!/usr/bin/env bash
# ==============================================================================
# BCE Factory — Startup & Reboot Verification
# Chạy khi Mac khởi động lại hoặc định kỳ kiểm tra sau reboot:
# 1. Xác định thời điểm boot của macOS (sysctl kern.boottime)
# 2. Kiểm tra xem có missed discovery / research do Mac tắt không
# 3. Phục hồi trạng thái hoạt động bình thường, ghi nhận sự kiện reboot
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
LOG_DIR="$PROJECT_DIR/logs"
STATE_FILE="$LOG_DIR/last_boot_time.txt"
mkdir -p "$LOG_DIR"

NOW_STR=$(date "+%Y-%m-%d %H:%M:%S")

# Lấy thời điểm boot của máy Mac
CURRENT_BOOT=$(sysctl -n kern.boottime 2>/dev/null | awk '{print $4}' | tr -d ',')

LAST_BOOT=""
if [[ -f "$STATE_FILE" ]]; then
    LAST_BOOT=$(cat "$STATE_FILE" 2>/dev/null || echo "")
fi

if [[ "$CURRENT_BOOT" != "$LAST_BOOT" ]]; then
    echo "[$NOW_STR] [MAC REBOOT DETECTED] Phát hiện máy Mac vừa khởi động lại (Boot epoch: $CURRENT_BOOT)."
    echo "$CURRENT_BOOT" > "$STATE_FILE"
    
    # 1. Verify cron scheduler
    CRON_EXISTS=$(crontab -l 2>/dev/null | grep -c "BCE FACTORY SCHEDULER" || true)
    if [[ "$CRON_EXISTS" -eq 0 ]]; then
        echo "[$NOW_STR] Reinstalling BCE scheduler after reboot..."
        bash "$PROJECT_DIR/scripts/restart_cron.sh" > /dev/null 2>&1
    fi

    # 2. Xóa bỏ bất kỳ stale lock file nào còn sót lại từ phiên trước khi reboot
    rm -f /tmp/bce_factory.lock

    # 3. Ghi nhận sự kiện phục hồi sau reboot vào database
    "$PYTHON_BIN" -c "
from db_storage import log_recovery_event
log_recovery_event('MAC_REBOOT', 'Máy tính MacBook vừa khởi động lại.', 'Xác minh môi trường, giải phóng lock file cũ, kiểm tra cron scheduler.', 'SUCCESS')
"

    # 4. Kiểm tra Missed Discovery
    "$PYTHON_BIN" -c "
import os
from datetime import datetime
from db_storage import get_last_job_by_type, record_missed_job
from health_engine import check_system_health

h = check_system_health()
now = datetime.now()
# Nếu hiện tại đã quá 08:00 sáng mà hôm nay chưa có Discovery
if now.hour >= 8:
    last_disc = h.get('last_discovery', '')
    today_str = now.strftime('%Y-%m-%d')
    if today_str not in str(last_disc):
        print('[+] Phát hiện bỏ lỡ ca Discovery sáng nay (do Mac tắt). Đang tự động chạy bù 1 lần duy nhất...')
        record_missed_job('discovery', f'{today_str} 07:30:00', 'Mac tắt trong khung giờ 07:30 sáng.')
        os.system('PYTHONPATH=. .venv/bin/python main.py discovery')
"
    echo "[$NOW_STR] Startup check completed successfully. Ready for scheduled operation."
else
    # Không phải reboot mới, hoạt động bình thường
    echo "[$NOW_STR] Startup check: Normal operation (No new reboot detected)."
fi
