#!/usr/bin/env python3
"""
Scheduler chạy tự động ngầm:
Lập lịch tự động chạy pipeline định kỳ (ví dụ mỗi 6 tiếng hoặc 12 tiếng)
để liên tục cập nhật video mới và bình luận nóng nhất.
"""

import time
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pipeline import run_pipeline

load_dotenv()

def start_scheduler():
    interval_hours = int(os.getenv("SCHEDULE_INTERVAL_HOURS", 6))
    interval_seconds = interval_hours * 3600

    print("=" * 60)
    print(f"⏰ BUDDHIST ENGAGEMENT FACTORY - SCHEDULER STARTED")
    print(f"Chu kỳ quét tự động: {interval_hours} giờ một lần.")
    print("Nhấn Ctrl+C để dừng.")
    print("=" * 60)

    try:
        while True:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{now_str}] 🚀 Đang kích hoạt chu kỳ quét tự động...")
            try:
                run_pipeline()
            except Exception as e:
                print(f"[!] Gặp lỗi trong phiên chạy: {e}")
                
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ Hoàn thành phiên! Đang đợi {interval_hours} tiếng cho phiên tiếp theo...")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n[!] Scheduler đã dừng an toàn theo yêu cầu.")

if __name__ == "__main__":
    start_scheduler()
