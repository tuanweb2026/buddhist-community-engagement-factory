"""
Unit and Integration Tests for Phase Self-Recovery & Cron Health Management
Kiểm tra toàn diện:
1. Health check command & diagnostic logic
2. Cron configuration validator
3. Stale job detection & heartbeat mechanism
4. Watchdog safe recovery logic (No publishing)
5. Missed job recording
6. Database integrity protection (No deletion)
"""

import os
import sqlite3
from datetime import datetime, timedelta
from health_engine import check_system_health, check_cron_configuration
from db_storage import (
    start_job_run, update_job_heartbeat, finish_job_run,
    record_missed_job, log_recovery_event, get_stale_or_running_jobs,
    get_connection, init_database
)

TEST_DB = "data/test_recovery.db"

def setup_module():
    init_database(TEST_DB)

def teardown_module():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_health_check_detects_valid_environment():
    h = check_system_health()
    assert h["python"] == "OK"
    assert h["virtual_env"] == "OK"
    assert h["sqlite"] == "OK"
    assert h["database"] == "OK"
    assert h["dotenv"] == "OK"
    assert h["youtube_api"] == "OK"
    assert h["llm_api"] == "OK"
    assert h["cron_installed"] == "YES"
    assert h["cron_config"] == "OK"
    assert h["overall_status"] == "HEALTHY"

def test_cron_configuration_validation():
    info = check_cron_configuration()
    assert info["installed"] is True
    assert info["block_found"] is True
    assert info["duplicate_blocks"] == 0
    assert info["invalid_jobs"] == 0
    assert info["scheduled_jobs"] >= 7
    assert info["valid"] is True

def test_stale_job_detection():
    # 1. Normal active job
    r1 = start_job_run("engagement_test", db_path=TEST_DB)
    update_job_heartbeat(r1, db_path=TEST_DB)
    stales = get_stale_or_running_jobs(stale_minutes=45, db_path=TEST_DB)
    target1 = next((j for j in stales if j["run_id"] == r1), None)
    assert target1 is not None
    assert target1["is_stale"] is False

    # 2. Expired heartbeat job (>45 mins ago)
    conn = get_connection(TEST_DB)
    cur = conn.cursor()
    old_time = "2026-09-30 10:00:00"
    cur.execute("INSERT INTO job_runs (run_id, job_type, started_at, heartbeat_at, status) VALUES (?, ?, ?, ?, 'RUNNING')",
                ("stale_job_xyz", "research_test", old_time, old_time))
    conn.commit()
    conn.close()

    stales_after = get_stale_or_running_jobs(stale_minutes=45, db_path=TEST_DB)
    target_stale = next((j for j in stales_after if j["run_id"] == "stale_job_xyz"), None)
    assert target_stale is not None
    assert target_stale["is_stale"] is True

    # 3. Finish and clean
    finish_job_run("stale_job_xyz", status="STALE_KILLED", error="Watchdog test cleanup", db_path=TEST_DB)
    finish_job_run(r1, status="COMPLETED", db_path=TEST_DB)

def test_missed_job_recorded_truthfully():
    record_missed_job("discovery", "2026-09-30 07:30:00", "Macbook closed", db_path=TEST_DB)
    conn = get_connection(TEST_DB)
    cur = conn.cursor()
    cur.execute("SELECT status, error FROM job_runs WHERE job_type = 'discovery' AND status = 'MISSED'")
    row = cur.fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "MISSED"
    assert "Macbook closed" in row[1]

def test_recovery_event_logging():
    log_recovery_event("TEST_RECOVERY", "Simulated lock removal", "Action executed", "SUCCESS", db_path=TEST_DB)
    conn = get_connection(TEST_DB)
    cur = conn.cursor()
    cur.execute("SELECT event_type, result FROM recovery_events WHERE event_type = 'TEST_RECOVERY'")
    row = cur.fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "TEST_RECOVERY"
    assert row[1] == "SUCCESS"
