#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================================"
echo "☸️  BCE FACTORY — TRẠNG THÁI VẬN HÀNH"
echo "========================================================"
"./.venv/bin/python" main.py health

echo ""
echo "--- LAUNCHAGENTS CHẠY NGẦM ---"
launchctl list | grep bce || echo "[!] Chưa phát hiện LaunchAgent nào."
