"""
Health and Cron Diagnostic Engine for BCE Factory.
Cung cấp phân tích chi tiết, trung thực và không che giấu lỗi:
1. System Dependency Health (Python, Venv, SQLite, .env, API keys)
2. Cron Configuration & Schedule Parsing
3. Job Execution History & Stale Detection
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")
import sqlite3
import subprocess
from datetime import datetime, timedelta

from typing import Dict, Any, List, Tuple

from app_config import (
    DATABASE_PATH, YOUTUBE_API_KEY, LLM_API_KEY, TARGET_CHANNEL_HANDLE,
    JOB_STALE_MINUTES, CLIENT_SECRETS_FILE, TOKEN_STORAGE_FILE
)
from db_storage import (
    get_connection, get_last_job_by_type, get_stale_or_running_jobs
)

CRON_SIGNATURE_START = "# === BCE FACTORY SCHEDULER START ==="
CRON_SIGNATURE_END = "# === BCE FACTORY SCHEDULER END ==="

EXPECTED_CRON_SCHEDULE = [
    ("07:30", "discovery", "30 7 * * *"),
    ("09:00", "research", "0 9 * * *"),
    ("10:30", "engagement #1", "30 10 * * *"),
    ("13:30", "engagement #2", "30 13 * * *"),
    ("16:30", "engagement #3", "30 16 * * *"),
    ("20:30", "engagement #4", "30 20 * * *"),
    ("23:00", "daily report", "0 23 * * *"),
]

def check_system_health() -> Dict[str, Any]:
    """Kiểm tra toàn diện trạng thái các thành phần hệ thống"""
    res = {}
    
    # Python
    py_ver = sys.version_info
    res["python"] = "OK" if (py_ver.major == 3 and py_ver.minor >= 9) else f"FAIL ({sys.version.split()[0]})"
    
    # Virtual Environment
    is_venv = (sys.prefix != sys.base_prefix) or ("VIRTUAL_ENV" in os.environ)
    res["virtual_env"] = "OK" if is_venv else "FAIL (Not in venv)"
    
    # SQLite Library
    try:
        ver = sqlite3.sqlite_version
        res["sqlite"] = "OK"
    except Exception as e:
        res["sqlite"] = f"FAIL ({e})"
        
    # Database accessibility & integrity
    if not os.path.exists(DATABASE_PATH):
        res["database"] = "FAIL (File not found)"
    else:
        try:
            conn = get_connection(DATABASE_PATH)
            cur = conn.cursor()
            cur.execute("PRAGMA integrity_check;")
            row = cur.fetchone()
            conn.close()
            if row and row[0] == "ok":
                res["database"] = "OK"
            else:
                res["database"] = f"FAIL (Integrity: {row[0] if row else 'Unknown'})"
        except Exception as e:
            res["database"] = f"FAIL ({e})"

    # .env File
    res["dotenv"] = "OK" if os.path.exists(".env") else "FAIL (.env missing)"
    
    # YouTube API Key
    if YOUTUBE_API_KEY and len(YOUTUBE_API_KEY.strip()) > 15:
        res["youtube_api"] = "OK"
    else:
        res["youtube_api"] = "FAIL (Missing or invalid YOUTUBE_API_KEY)"
        
    # LLM API Key
    if LLM_API_KEY and len(LLM_API_KEY.strip()) > 15:
        res["llm_api"] = "OK"
    else:
        res["llm_api"] = "FAIL (Missing LLM_API_KEY)"

    # Scheduler Status (LaunchAgent or Cron)
    import subprocess
    launchd_ok = False
    try:
        r = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        if "com.bce.factory" in r.stdout:
            launchd_ok = True
    except Exception:
        pass

    cron_info = check_cron_configuration()
    if launchd_ok:
        res["cron_installed"] = "YES (LaunchAgent)"
        res["cron_config"] = "OK"
    elif cron_info["installed"]:
        res["cron_installed"] = "YES (Cron)"
        res["cron_config"] = "OK" if cron_info["valid"] else "MALFORMED"
    else:
        res["cron_installed"] = "NO"
        res["cron_config"] = "MISSING" 

    # Last Jobs Check (Lấy thời gian thực tế trong DB)
    res["last_discovery"] = _format_job_time("discovery")
    res["last_research"] = _format_job_time("research")
    res["last_engagement"] = _format_job_time("engagement")
    res["last_tracking"] = _format_job_time("tracking")
    res["last_daily_report"] = _format_job_time("daily_report")

    # Current & Stale Jobs
    stale_list = get_stale_or_running_jobs(stale_minutes=JOB_STALE_MINUTES, db_path=DATABASE_PATH)
    active_running = [j for j in stale_list if not j.get("is_stale")]
    stale_running = [j for j in stale_list if j.get("is_stale")]

    if active_running:
        res["current_job"] = f"{active_running[0]['job_type']} (PID: {active_running[0]['run_id']})"
    else:
        res["current_job"] = "NONE"

    if stale_running:
        res["stale_job"] = f"YES ({len(stale_running)} stale job: {stale_running[0]['job_type']})"
    else:
        res["stale_job"] = "NO"

    # Overall Status Calculation
    critical_deps = [res["python"], res["virtual_env"], res["sqlite"], res["database"], res["dotenv"]]
    has_critical_fail = any(v.startswith("FAIL") for v in critical_deps)
    has_api_fail = res["youtube_api"].startswith("FAIL") or res["llm_api"].startswith("FAIL")
    has_cron_fail = (res["cron_installed"] == "NO") or (res["cron_config"] != "OK")
    has_stale = res["stale_job"] != "NO"

    if has_critical_fail:
        res["overall_status"] = "DOWN"
    elif has_api_fail or has_cron_fail or has_stale:
        res["overall_status"] = "DEGRADED"
    else:
        res["overall_status"] = "HEALTHY"

    return res

def _format_job_time(job_type: str) -> str:
    job = get_last_job_by_type(job_type, db_path=DATABASE_PATH)
    if job and job.get("finished_at"):
        return str(job["finished_at"])
    # Fallback to check runs or published comments if table just migrated
    if job_type == "engagement":
        try:
            conn = get_connection(DATABASE_PATH)
            cur = conn.cursor()
            cur.execute("SELECT published_at FROM published_comments ORDER BY published_at DESC LIMIT 1")
            r = cur.fetchone()
            conn.close()
            if r and r[0]:
                return str(r[0])
        except Exception:
            pass
    elif job_type == "discovery" or job_type == "daily_report":
        try:
            conn = get_connection(DATABASE_PATH)
            cur = conn.cursor()
            cur.execute("SELECT created_at FROM runs ORDER BY id DESC LIMIT 1")
            r = cur.fetchone()
            conn.close()
            if r and r[0]:
                return str(r[0])
        except Exception:
            pass
    return "NEVER"

def get_current_crontab() -> str:
    """Đọc nội dung crontab của người dùng hiện tại"""
    try:
        proc = subprocess.run(["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode == 0:
            return proc.stdout
        return ""
    except Exception:
        return ""

def check_cron_configuration() -> Dict[str, Any]:
    """Phân tích khối crontab của BCE Factory"""
    content = get_current_crontab()
    installed = bool(content.strip())
    
    start_count = content.count(CRON_SIGNATURE_START)
    end_count = content.count(CRON_SIGNATURE_END)
    block_found = (start_count >= 1) and (end_count >= 1)
    duplicate_blocks = max(0, start_count - 1)
    
    scheduled_jobs = 0
    invalid_jobs = 0
    lines = []
    
    if block_found:
        in_block = False
        for line in content.splitlines():
            s = line.strip()
            if s == CRON_SIGNATURE_START:
                in_block = True
                continue
            if s == CRON_SIGNATURE_END:
                in_block = False
                continue
            if in_block and s and not s.startswith("#"):
                # Bỏ qua các dòng gán biến môi trường như PATH=, PYTHONPATH=
                if "=" in s and not s.split()[0].replace("*", "").replace("/", "").isdigit() and not s.startswith("*"):
                    continue
                scheduled_jobs += 1
                parts = s.split()
                if len(parts) >= 6:
                    lines.append(s)
                else:
                    invalid_jobs += 1

    valid = block_found and (duplicate_blocks == 0) and (invalid_jobs == 0) and (scheduled_jobs >= 7)


    return {
        "installed": installed,
        "block_found": block_found,
        "duplicate_blocks": duplicate_blocks,
        "scheduled_jobs": scheduled_jobs,
        "invalid_jobs": invalid_jobs,
        "valid": valid,
        "job_lines": lines
    }

def print_health_report():
    h = check_system_health()
    print("BCE FACTORY HEALTH CHECK")
    print("========================")
    print("")
    print(f"Python              : {h['python']}")
    print(f"Virtual Environment : {h['virtual_env']}")
    print(f"SQLite              : {h['sqlite']}")
    print(f"Database            : {h['database']}")
    print(f".env                : {h['dotenv']}")
    print(f"YouTube API         : {h['youtube_api']}")
    print(f"LLM API             : {h['llm_api']}")
    print("")
    print(f"Cron installed      : {h['cron_installed']}")
    print(f"Cron configuration  : {h['cron_config']}")
    print("")
    print(f"Last Discovery      : {h['last_discovery']}")
    print(f"Last Research       : {h['last_research']}")
    print(f"Last Engagement     : {h['last_engagement']}")
    print(f"Last Tracking       : {h['last_tracking']}")
    print(f"Last Daily Report   : {h['last_daily_report']}")
    print("")
    print(f"Current Job         : {h['current_job']}")
    print(f"Stale Job           : {h['stale_job']}")
    print("")
    print(f"Overall Status      : {h['overall_status']}")

def print_cron_status():
    info = check_cron_configuration()
    print("BCE CRON STATUS")
    print("===============")
    print("")
    print(f"Cron installed       : {'YES' if info['installed'] else 'NO'}")
    print(f"BCE cron block       : {'FOUND' if info['block_found'] else 'NOT FOUND'}")
    print(f"Duplicate blocks     : {info['duplicate_blocks']}")
    print(f"Scheduled jobs       : {info['scheduled_jobs']}")
    print(f"Invalid jobs         : {info['invalid_jobs']}")
    print("")
    print("Next scheduled jobs:")
    for time_str, job_name, _ in EXPECTED_CRON_SCHEDULE:
        print(f"{time_str} {job_name}")
    print("")
    status_str = "OK" if info["valid"] else ("MALFORMED" if info["block_found"] else "MISSING")
    print(f"Status: {status_str}")
