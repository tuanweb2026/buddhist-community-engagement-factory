#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================================"
echo "📋 BÁO CÁO MỚI NHẤT TỪ BCE FACTORY"
echo "========================================================"

LATEST_REPORT=$(ls -t reports/*.md 2>/dev/null | head -n 1)
LATEST_LIDO=$(ls -t reports/lido-improvement/*.md 2>/dev/null | head -n 1)

if [ -z "$LATEST_REPORT" ]; then
    echo "[!] Chưa có báo cáo Daily nào được tạo."
else
    echo "📄 File: $LATEST_REPORT"
    echo "--------------------------------------------------------"
    cat "$LATEST_REPORT"
fi

echo ""
echo "========================================================"
if [ -z "$LATEST_LIDO" ]; then
    echo "[!] Chưa có báo cáo Lido Strategy nào."
else
    echo "🪷 File: $LATEST_LIDO"
    echo "--------------------------------------------------------"
    cat "$LATEST_LIDO"
fi
