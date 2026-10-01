with open('health_engine.py', 'r') as f:
    content = f.read()

old_cron_part = """    # Cron Status
    cron_info = check_cron_configuration()
    res["cron_installed"] = "YES" if cron_info["installed"] else "NO"
    res["cron_config"] = "OK" if cron_info["valid"] else ("MISSING" if not cron_info["block_found"] else "MALFORMED")"""

new_cron_part = """    # Scheduler Status (LaunchAgent or Cron)
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
        res["cron_config"] = "MISSING" """

content = content.replace(old_cron_part, new_cron_part)
with open('health_engine.py', 'w') as f:
    f.write(content)
