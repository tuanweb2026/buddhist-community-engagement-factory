#!/usr/bin/env bash
# ==============================================================================
# BCE Factory — Watchdog Monitor
# Chạy định kỳ mỗi 15 phút qua cron:
# 1. Kiểm tra scheduler (cron block có tồn tại không)
# 2. Kiểm tra stale job (quá 45 phút không có heartbeat)
# 3. Kiểm tra database writable & disk space
# 4. Tự động khắc phục an toàn (safe auto-recovery)
#
# TUYỆT ĐỐI TUÂN THỦ:
# Watchdog KHÔNG BAO GIỜ tự generate hay publish comment lên YouTube!
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
export PYTHONPATH="$PROJECT_DIR"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
LOG_DIR="$PROJECT_DIR/logs"
DB_FILE="$PROJECT_DIR/data/bce.db"
mkdir -p "$LOG_DIR"


NOW_STR=$(date "+%Y-%m-%d %H:%M:%S")

# 1. Kiểm tra Disk Space (cảnh báo nếu còn dưới 500MB)
AVAIL_DISK=$(df -m "$PROJECT_DIR" | awk 'NR==2 {print $4}')
if [[ "$AVAIL_DISK" -lt 500 ]]; then
    echo "[$NOW_STR] [WATCHDOG ALERT] Dung lượng ổ cứng sắp hết (còn ${AVAIL_DISK}MB)!"
    "$PYTHON_BIN" -c "from db_storage import log_recovery_event; log_recovery_event('DISK_LOW', 'Dung lượng ổ cứng còn ít hơn 500MB', 'Ghi log cảnh báo', 'ALERT')"
fi

# 2. Kiểm tra Database Writable
if ! touch "$DB_FILE" 2>/dev/null; then
    echo "[$NOW_STR] [WATCHDOG ALERT] Database không thể ghi dữ liệu (Read-only hoặc permission error)!"
    exit 1
fi

# 3. Kiểm tra và xử lý Stale Jobs & Stale Locks
STALE_CHECK_OUTPUT=$("$PYTHON_BIN" -c "
import os, sys
from datetime import datetime
from db_storage import get_stale_or_running_jobs, finish_job_run, log_recovery_event
from app_config import JOB_STALE_MINUTES

stale_list = get_stale_or_running_jobs(stale_minutes=JOB_STALE_MINUTES)
stale_found = 0
for j in stale_list:
    if j.get('is_stale'):
        stale_found += 1
        r_id = j['run_id']
        j_type = j['job_type']
        finish_job_run(r_id, status='STALE_KILLED', error='Job heartbeat expired over 45 mins. Cleared by Watchdog.')
        log_recovery_event('STALE_JOB_CLEARED', f'Job {j_type} (RunID: {r_id}) bị treo quá 45 phút.', 'Chấm dứt trạng thái chạy và giải phóng tài nguyên.', 'SUCCESS')
        print(f'CLEARED_STALE:{r_id}:{j_type}')

print(f'TOTAL_STALE:{stale_found}')
" 2>&1 || true)


if [[ "$STALE_CHECK_OUTPUT" == *"CLEARED_STALE"* ]]; then
    echo "[$NOW_STR] [WATCHDOG ALERT] Đã phát hiện và giải phóng stale job: $STALE_CHECK_OUTPUT"
fi

# 4. Kiểm tra Stale Lock File
LOCK_FILE="/tmp/bce_factory.lock"
if [[ -f "$LOCK_FILE" ]]; then
    LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if [[ -n "$LOCK_PID" ]]; then
        # Kiểm tra xem PID có thực sự đang chạy không
        if ! ps -p "$LOCK_PID" > /dev/null 2>&1; then
            echo "[$NOW_STR] [WATCHDOG ALERT] Phát hiện stale lock file (PID $LOCK_PID đã dừng). Tiến hành gỡ bỏ..."
            rm -f "$LOCK_FILE"
            "$PYTHON_BIN" -c "from db_storage import log_recovery_event; log_recovery_event('STALE_LOCK_REMOVED', 'Lock file tồn tại nhưng process PID $LOCK_PID đã chết.', 'Xóa file /tmp/bce_factory.lock an toàn.', 'SUCCESS')"
        fi
    fi
fi

# 5. Kiểm tra Cron block
CRON_CHECK_OUTPUT=$("$PYTHON_BIN" -c "
from health_engine import check_cron_configuration
info = check_cron_configuration()
print('VALID' if info['valid'] else 'INVALID')
" 2>/dev/null || echo "ERROR")

if [[ "$CRON_CHECK_OUTPUT" != "VALID" ]]; then
    echo "[$NOW_STR] [WATCHDOG ALERT] Khối cron scheduler bị mất hoặc sai cấu trúc. Đang tự động khôi phục..."
    bash "$PROJECT_DIR/scripts/restart_cron.sh" > /dev/null 2>&1
    "$PYTHON_BIN" -c "from db_storage import log_recovery_event; log_recovery_event('CRON_AUTO_REPAIR', 'Cron block bị thiếu hoặc malformed.', 'Tự động gọi restart_cron.sh để tái cấu hình crontab.', 'SUCCESS')"
fi

echo "[$NOW_STR] WATCHDOG OK"
