#!/usr/bin/env python3
"""
Workflow Pipeline tự động hoá:
1. Đọc cấu hình từ .env hoặc tham số truyền vào
2. Lùng sục các video nổi tiếng theo từ khoá Phật giáo
3. Cào top bình luận của từng video
4. AI phân tích tâm lý, tìm điểm chạm cảm xúc
5. Tạo ra các mẫu comment đắt giá hướng về @1995lido
6. Lưu trữ vào database SQLite và xuất báo cáo
"""

import os
import sys
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

from database import init_db, save_video_and_comments, save_analysis_and_comments
from youtube_collector import YouTubeScraper
from engagement_ai import EngagementAI

load_dotenv()

def run_pipeline(keywords=None, max_videos=2, max_comments=15):
    print("=" * 60)
    print("☸️  BUDDHIST COMMUNITY ENGAGEMENT FACTORY - STARTING PIPELINE")
    print("=" * 60)
    
    init_db()
    
    if not keywords:
        env_keywords = os.getenv("SEARCH_KEYWORDS", "thuyết pháp Thích Pháp Hòa, thiền buông thư Thích Nhất Hạnh")
        keywords = [k.strip() for k in env_keywords.split(",") if k.strip()]
        
    scraper = YouTubeScraper()
    ai_engine = EngagementAI()
    
    print(f"[*] Danh sách từ khoá quét: {keywords}")
    print(f"[*] Kênh mục tiêu hướng đến: @1995lido\n")
    
    total_processed = 0
    
    for kw in keywords:
        print(f"\n🔍 [1/3] Đang tìm kiếm video nổi tiếng cho từ khoá: '{kw}'...")
        videos = scraper.search_videos(kw, max_results=max_videos)
        print(f"    -> Tìm thấy {len(videos)} video tiềm năng.")
        
        for v in videos:
            v_url = v.get("webpage_url")
            v_title = v.get("title")
            print(f"\n📥 [2/3] Đang lấy thông tin & comments cho: '{v_title}'")
            print(f"    URL: {v_url}")
            
            data = scraper.get_video_details_and_comments(v_url, max_comments=max_comments)
            info = data.get("info") if data.get("info") and data.get("info").get("id") else v
            comments = data.get("comments", [])
            print(f"    -> Đã thu thập được {len(comments)} bình luận của khán giả.")
            
            # Lưu vào Database
            save_video_and_comments(info, comments, keyword=kw)
            
            # Gửi vào AI Phân tích & Tạo Comment
            print("🧠 [3/3] AI đang phân tích tâm lý & sáng tạo comment có giá trị...")
            result = ai_engine.analyze_and_generate(info, comments)
            
            analysis = result.get("analysis", {})
            suggestions = result.get("suggested_comments", [])
            
            # Lưu kết quả phân tích & comment gợi ý
            save_analysis_and_comments(info.get("id"), analysis, suggestions)
            
            print(f"    ✅ Hoàn tất phân tích! Đã tạo {len(suggestions)} mẫu comment chiến lược:")
            for idx, s in enumerate(suggestions, 1):
                print(f"\n    --- [Mẫu {idx}: {s.get('style')}] ---")
                print(f"    🎯 Góc tiếp cận: {s.get('hook_angle')}")
                print(f"    💬 Bình luận: {s.get('suggested_comment')}")
                print(f"    🔗 Điều hướng: {s.get('subtle_call_to_action')}")
                
            total_processed += 1
            time.sleep(2) # Tránh rate-limit
            
    print("\n" + "=" * 60)
    print(f"🎉 HOÀN THÀNH TOÀN BỘ TIẾN TRÌNH! Đã xử lý {total_processed} video.")
    print("📁 Tất cả dữ liệu đã được lưu trữ an toàn trong 'buddhist_engagement.db'")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy Buddhist Engagement Factory Pipeline")
    parser.add_argument("--keywords", type=str, help="Từ khóa cách nhau bằng dấu phẩy")
    parser.add_argument("--max_videos", type=int, default=2, help="Số video tối đa mỗi từ khóa")
    parser.add_argument("--max_comments", type=int, default=15, help="Số comment tối đa thu thập mỗi video")
    
    args = parser.parse_args()
    kw_list = [k.strip() for k in args.keywords.split(",")] if args.keywords else None
    run_pipeline(keywords=kw_list, max_videos=args.max_videos, max_comments=args.max_comments)
