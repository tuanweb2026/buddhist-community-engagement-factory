with open('health_engine.py', 'r') as f:
    content = f.read()

# Update health check logic to check launchctl as well as cron
old_check = """    cron_installed, cron_block = check_cron_configuration()
    cron_ok = cron_installed and len(cron_block) >= 5"""

new_check = """    cron_installed, cron_block = check_cron_configuration()
    
    # Check LaunchAgents on macOS
    import subprocess
    launchd_ok = False
    try:
        res = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        if "com.bce.factory" in res.stdout:
            launchd_ok = True
    except Exception:
        pass

    cron_ok = (cron_installed and len(cron_block) >= 5) or launchd_ok"""

content = content.replace(old_check, new_check)

# Update output string in print_health_report
content = content.replace('print(f"Cron installed      : {\'YES\' if cron_installed else \'NO\'}")', 'print(f"Scheduler (LaunchAgent/Cron): {\'YES (LaunchAgent)\' if launchd_ok else (\'YES (Cron)\' if cron_installed else \'NO\')}")')

with open('health_engine.py', 'w') as f:
    f.write(content)
