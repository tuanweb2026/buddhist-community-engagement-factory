#!/usr/bin/env bash
# ==============================================================================
# BCE Factory — Quick One-Command Status
# Hiển thị tóm tắt tình trạng hệ thống, tiến trình hôm nay và slot tiếp theo
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"

"$PYTHON_BIN" -c "
import os
import sqlite3
from datetime import datetime
from app_config import DATABASE_PATH, JOB_STALE_MINUTES
from health_engine import check_system_health, check_cron_configuration, EXPECTED_CRON_SCHEDULE

h = check_system_health()
cron_info = check_cron_configuration()
today_str = datetime.now().strftime('%Y-%m-%d')
now = datetime.now()

# Đếm các tác vụ hôm nay từ DB
try:
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM videos WHERE date(processed_at) = date(?)', (today_str,))
    disc_count = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM research WHERE date(created_at) = date(?)', (today_str,))
    res_count = cur.fetchone()[0]

    cur.execute(\"SELECT COUNT(*) FROM published_comments WHERE date(published_at) = date(?) AND status IN ('PUBLISHED', 'DRY_RUN')\", (today_str,))
    pub_count = cur.fetchone()[0]

    cur.execute(\"SELECT COUNT(*) FROM published_comments WHERE date(published_at) = date(?) AND status LIKE '%SKIP%'\", (today_str,))
    skip_count = cur.fetchone()[0]

    cur.execute(\"SELECT COUNT(*) FROM published_comments WHERE date(published_at) = date(?) AND status LIKE '%FAIL%'\", (today_str,))
    fail_count = cur.fetchone()[0]

    cur.execute(\"SELECT comment_text, published_at FROM published_comments WHERE date(published_at) = date(?) ORDER BY published_at DESC LIMIT 1\", (today_str,))
    last_pub = cur.fetchone()
    conn.close()
except Exception:
    disc_count = res_count = pub_count = skip_count = fail_count = 0
    last_pub = None

# Trạng thái Scheduler & Watchdog
sched_icon = '🟢 RUNNING' if cron_info['valid'] else '🔴 ERROR'
watchdog_icon = '🟢 RUNNING' if cron_info['block_found'] else '🟡 NOT INSTALLED'
db_icon = '🟢 OK' if h['database'] == 'OK' else '🔴 ERROR'
yt_icon = '🟢 OK' if h['youtube_api'] == 'OK' else '🔴 ERROR'
llm_icon = '🟢 OK' if h['llm_api'] == 'OK' else '🔴 ERROR'

# Xác định job kế tiếp theo mốc thời gian
next_job_desc = 'Engagement #1 — 10:30'
cur_time_str = now.strftime('%H:%M')
for t_str, j_name, _ in EXPECTED_CRON_SCHEDULE:
    if t_str > cur_time_str:
        next_job_desc = f'{j_name.capitalize()} — {t_str}'
        break
else:
    next_job_desc = 'Discovery — 07:30 (Tomorrow)'

last_job_desc = 'None yet'
if last_pub:
    t_part = last_pub[1].split()[-1][:5]
    last_job_desc = f'Published Comment — {t_part}'
elif h['last_engagement'] != 'NEVER':
    last_job_desc = f\"Engagement — {h['last_engagement'].split()[-1][:5]}\"

sys_status = 'HEALTHY' if h['overall_status'] == 'HEALTHY' else h['overall_status']

print('=====================================')
print('         BCE FACTORY STATUS')
print('=====================================')
print('')
print(f'Scheduler    : {sched_icon}')
print(f'Watchdog     : {watchdog_icon}')
print(f'Database     : {db_icon}')
print(f'YouTube API  : {yt_icon}')
print(f'LLM          : {llm_icon}')
print('')
print('Last job:')
print(f'{last_job_desc}')
print('')
print('Today:')
print(f'Discovery    {disc_count}')
print(f'Research     {res_count}')
print(f'Published    {pub_count}')
print(f'Skipped      {skip_count}')
print(f'Failed       {fail_count}')
print('')
print('Next:')
print(f'{next_job_desc}')
print('')
print(f'System       : {sys_status}')
print('=====================================')

if sys_status != 'HEALTHY':
    print('Recommended:')
    print('bash scripts/recover.sh')
"
