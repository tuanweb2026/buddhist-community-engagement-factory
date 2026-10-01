import os
import subprocess
from pathlib import Path

HOME = str(Path.home())
PROJECT_DIR = "/Users/abc/Documents/BUDDHIST COMMUNITY ENGAGEMENT FACTORY"
PYTHON_BIN = os.path.join(PROJECT_DIR, ".venv/bin/python")
LOGS_DIR = os.path.join(PROJECT_DIR, "logs")
LAUNCH_AGENTS_DIR = os.path.join(HOME, "Library/LaunchAgents")

os.makedirs(LAUNCH_AGENTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

PLISTS = [
    {
        "label": "com.bce.factory.discovery",
        "command": [PYTHON_BIN, "main.py", "discovery"],
        "stdout": os.path.join(LOGS_DIR, "launchd_discovery.log"),
        "stderr": os.path.join(LOGS_DIR, "launchd_discovery.log"),
        "calendar": [{"Hour": 7, "Minute": 30}]
    },
    {
        "label": "com.bce.factory.research",
        "command": [PYTHON_BIN, "main.py", "research"],
        "stdout": os.path.join(LOGS_DIR, "launchd_research.log"),
        "stderr": os.path.join(LOGS_DIR, "launchd_research.log"),
        "calendar": [{"Hour": 9, "Minute": 0}]
    },
    {
        "label": "com.bce.factory.engagement",
        "command": [PYTHON_BIN, "main.py", "daily"],
        "stdout": os.path.join(LOGS_DIR, "launchd_engagement.log"),
        "stderr": os.path.join(LOGS_DIR, "launchd_engagement.log"),
        "calendar": [
            {"Hour": 10, "Minute": 30},
            {"Hour": 13, "Minute": 30},
            {"Hour": 16, "Minute": 30},
            {"Hour": 20, "Minute": 30}
        ]
    },
    {
        "label": "com.bce.factory.dailyreport",
        "command": [PYTHON_BIN, "main.py", "daily_report"],
        "stdout": os.path.join(LOGS_DIR, "launchd_daily_report.log"),
        "stderr": os.path.join(LOGS_DIR, "launchd_daily_report.log"),
        "calendar": [{"Hour": 23, "Minute": 0}]
    },
    {
        "label": "com.bce.factory.watchdog",
        "command": ["/bin/bash", os.path.join(PROJECT_DIR, "scripts/watchdog.sh")],
        "stdout": os.path.join(LOGS_DIR, "launchd_watchdog.log"),
        "stderr": os.path.join(LOGS_DIR, "launchd_watchdog.log"),
        "interval": 900
    }
]

for p in PLISTS:
    plist_path = os.path.join(LAUNCH_AGENTS_DIR, f"{p['label']}.plist")
    
    subprocess.run(["launchctl", "unload", plist_path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    
    calendar_xml = ""
    if "calendar" in p:
        calendar_xml = "<key>StartCalendarInterval</key>\n"
        if len(p["calendar"]) == 1:
            c = p["calendar"][0]
            calendar_xml += f"  <dict>\n    <key>Hour</key><integer>{c['Hour']}</integer>\n    <key>Minute</key><integer>{c['Minute']}</integer>\n  </dict>\n"
        else:
            calendar_xml += "  <array>\n"
            for c in p["calendar"]:
                calendar_xml += f"    <dict>\n      <key>Hour</key><integer>{c['Hour']}</integer>\n      <key>Minute</key><integer>{c['Minute']}</integer>\n    </dict>\n"
            calendar_xml += "  </array>\n"
            
    interval_xml = ""
    if "interval" in p:
        interval_xml = f"<key>StartInterval</key><integer>{p['interval']}</integer>\n"

    args_xml = "".join([f"    <string>{arg}</string>\n" for arg in p['command']])

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{p['label']}</string>
  <key>WorkingDirectory</key>
  <string>{PROJECT_DIR}</string>
  <key>ProgramArguments</key>
  <array>
{args_xml}  </array>
  {calendar_xml}  {interval_xml}  <key>StandardOutPath</key>
  <string>{p['stdout']}</string>
  <key>StandardErrorPath</key>
  <string>{p['stderr']}</string>
</dict>
</plist>
"""
    with open(plist_path, "w") as f:
        f.write(plist_content)
        
    res = subprocess.run(["launchctl", "load", plist_path], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] Đã kích hoạt LaunchAgent: {p['label']}")
    else:
        print(f"[-] Lỗi kích hoạt {p['label']}: {res.stderr}")

print("\n🎉 HOÀN TẤT CHUYỂN ĐỔI SANG MACOS LAUNCHAGENTS!")
