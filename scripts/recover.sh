#!/usr/bin/env bash
# ==============================================================================
# BCE Factory — Full System Recovery
# Kiểm tra tuần tự 12 bước an toàn:
# 1. Project exists
# 2. Python exists
# 3. .venv exists
# 4. dependencies available
# 5. .env exists
# 6. database accessible
# 7. database integrity
# 8. log directory
# 9. cron installation
# 10. stale lock
# 11. scheduler health
# 12. last successful job
#
# TUYỆT ĐỐI: Không bao giờ tự xóa database!
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
LOG_DIR="$PROJECT_DIR/logs"
DB_FILE="$PROJECT_DIR/data/bce.db"
mkdir -p "$LOG_DIR" data

echo "================================================================="
echo "           BCE FACTORY FULL SYSTEM RECOVERY"
echo "================================================================="

RECOVERY_ERRORS=0

# Step 1: Project exists
echo -n "[1/12] Checking project directory... "
if [[ -d "$PROJECT_DIR" ]]; then echo "OK"; else echo "FAIL"; exit 1; fi

# Step 2: Python exists
echo -n "[2/12] Checking system Python... "
if which python3 >/dev/null 2>&1; then echo "OK ($(python3 --version))"; else echo "FAIL"; exit 1; fi

# Step 3: .venv exists
echo -n "[3/12] Checking virtual environment... "
if [[ -f "$PYTHON_BIN" ]]; then
    echo "OK"
else
    echo "FAIL (Rebuilding virtualenv...)"
    python3 -m venv .venv
    "$PYTHON_BIN" -m pip install --upgrade pip
fi

# Step 4: Dependencies available
echo -n "[4/12] Checking dependencies... "
if "$PYTHON_BIN" -c "import google.genai, googleapiclient, youtube_transcript_api, sqlite3, dotenv" 2>/dev/null; then
    echo "OK"
else
    echo "MISSING (Installing requirements...)"
    "$PYTHON_BIN" -m pip install -r requirements.txt > /dev/null 2>&1 || true
fi

# Step 5: .env exists
echo -n "[5/12] Checking .env configuration... "
if [[ -f ".env" ]]; then
    echo "OK"
else
    echo "FAIL (.env file missing!)"
    RECOVERY_ERRORS=$((RECOVERY_ERRORS+1))
fi

# Step 6: Database accessible
echo -n "[6/12] Checking database file... "
if [[ -f "$DB_FILE" ]]; then
    echo "OK"
else
    echo "CREATING DATABASE (Initializing schema without deleting)..."
    "$PYTHON_BIN" -c "from db_storage import init_database; init_database()"
fi

# Step 7: Database integrity
echo -n "[7/12] Checking database integrity... "
DB_INTEGRITY=$("$PYTHON_BIN" -c "
import sqlite3
try:
    conn = sqlite3.connect('$DB_FILE')
    cur = conn.cursor()
    cur.execute('PRAGMA integrity_check;')
    res = cur.fetchone()[0]
    conn.close()
    print(res)
except Exception as e:
    print('ERROR:', e)
")

if [[ "$DB_INTEGRITY" == "ok" ]]; then
    echo "OK"
else
    echo "DATABASE ERROR DETECTED: $DB_INTEGRITY"
    echo "-> DO NOT DELETE DATABASE. Creating backup timestamped file..."
    cp "$DB_FILE" "$LOG_DIR/bce_db_corrupt_backup_$(date +%Y%m%d_%H%M%S).db"
    RECOVERY_ERRORS=$((RECOVERY_ERRORS+1))
fi

# Step 8: Log directory
echo -n "[8/12] Checking log directory... "
if [[ -d "$LOG_DIR" && -w "$LOG_DIR" ]]; then echo "OK"; else echo "FAIL"; exit 1; fi

# Step 9: Cron installation
echo -n "[9/12] Checking cron installation... "
CRON_CHECK=$("$PYTHON_BIN" -c "
from health_engine import check_cron_configuration
info = check_cron_configuration()
print('FOUND' if info['block_found'] else 'NOT_FOUND')
")

if [[ "$CRON_CHECK" == "FOUND" ]]; then
    echo "OK"
else
    echo "CRON NOT FOUND"
    echo "-> Automatically reinstalling BCE Factory scheduler..."
    bash "$PROJECT_DIR/scripts/restart_cron.sh" > /dev/null 2>&1
    "$PYTHON_BIN" -c "from db_storage import log_recovery_event; log_recovery_event('CRON_REINSTALLED', 'Cron block không tồn tại.', 'Tự động cài đặt lại scheduler qua recovery.sh.', 'SUCCESS')"
fi

# Step 10: Stale lock
echo -n "[10/12] Checking stale locks... "
LOCK_FILE="/tmp/bce_factory.lock"
if [[ -f "$LOCK_FILE" ]]; then
    LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if [[ -n "$LOCK_PID" ]] && ! ps -p "$LOCK_PID" > /dev/null 2>&1; then
        echo "STALE LOCK DETECTED"
        echo "-> Process PID $LOCK_PID no longer exists. Safely removing lock..."
        rm -f "$LOCK_FILE"
        "$PYTHON_BIN" -c "from db_storage import log_recovery_event; log_recovery_event('STALE_LOCK_CLEARED', 'Stale lock file được gỡ bỏ.', 'Đã xóa /tmp/bce_factory.lock.', 'SUCCESS')"
    else
        echo "ACTIVE PROCESS LOCK (PID: $LOCK_PID)"
    fi
else
    echo "OK (No lock conflicts)"
fi

# Step 11: Scheduler health
echo -n "[11/12] Checking scheduler health... "
SCHED_HEALTH=$("$PYTHON_BIN" -c "
from health_engine import check_cron_configuration
info = check_cron_configuration()
print('VALID' if info['valid'] else 'INVALID')
")

if [[ "$SCHED_HEALTH" == "VALID" ]]; then
    echo "OK"
else
    echo "CRON INVALID"
    echo "-> Repairing crontab configuration automatically..."
    bash "$PROJECT_DIR/scripts/restart_cron.sh" > /dev/null 2>&1
fi

# Step 12: Last successful job
echo -n "[12/12] Checking last successful job... "
LAST_JOB_INFO=$("$PYTHON_BIN" -c "
from health_engine import check_system_health
h = check_system_health()
print(f\"{h['last_engagement']} | Status: {h['overall_status']}\")
")
echo "$LAST_JOB_INFO"

echo "================================================================="

if [[ "$RECOVERY_ERRORS" -eq 0 ]]; then
    echo "               RECOVERY COMPLETE: ALL CHECKS PASSED"
    echo "================================================================="
    exit 0
else
    echo "               RECOVERY FAILED: REQUIRES HUMAN ATTENTION"
    echo "               ($RECOVERY_ERRORS critical issue(s) detected above)"
    echo "================================================================="
    exit 1
fi
