with open('health_engine.py', 'r') as f:
    content = f.read()

# Make check_system_health aware of LaunchAgents
old_code = """    return {
        "python": "OK" if python_ok else "FAIL",
        "virtual_env": "OK" if venv_ok else "FAIL",
        "sqlite": "OK" if sqlite_ok else "FAIL",
        "database": "OK" if db_ok else "FAIL",
        "dotenv": "OK" if env_ok else "FAIL",
        "youtube_api": "OK" if yt_api_ok else "FAIL",
        "llm_api": "OK" if llm_api_ok else "FAIL",
        "cron_installed": "YES" if cron_installed else "NO",
        "cron_config": "OK" if cron_ok else "MISSING",
        "last_discovery": last_discovery,
        "last_research": last_research,
        "last_engagement": last_engagement,
        "last_tracking": last_tracking,
        "last_daily_report": last_daily_report,
        "current_job": current_job or "NONE",
        "stale_job": "YES" if stale_job else "NO",
        "overall_status": overall_status
    }"""

new_code = """    return {
        "python": "OK" if python_ok else "FAIL",
        "virtual_env": "OK" if venv_ok else "FAIL",
        "sqlite": "OK" if sqlite_ok else "FAIL",
        "database": "OK" if db_ok else "FAIL",
        "dotenv": "OK" if env_ok else "FAIL",
        "youtube_api": "OK" if yt_api_ok else "FAIL",
        "llm_api": "OK" if llm_api_ok else "FAIL",
        "cron_installed": "YES (LaunchAgent)" if launchd_ok else ("YES (Cron)" if cron_installed else "NO"),
        "cron_config": "OK" if cron_ok else "MISSING",
        "last_discovery": last_discovery,
        "last_research": last_research,
        "last_engagement": last_engagement,
        "last_tracking": last_tracking,
        "last_daily_report": last_daily_report,
        "current_job": current_job or "NONE",
        "stale_job": "YES" if stale_job else "NO",
        "overall_status": overall_status
    }"""

content = content.replace(old_code, new_code)
with open('health_engine.py', 'w') as f:
    f.write(content)
