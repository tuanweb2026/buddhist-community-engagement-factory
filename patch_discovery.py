import re

with open('discovery.py', 'r') as f:
    content = f.read()

new_logic = """
from app_config import MIN_VIEWS_THRESHOLD, MIN_SUBS_THRESHOLD
import requests

def fetch_stats_and_filter(videos: List[VideoMetadata]) -> List[VideoMetadata]:
    if not YOUTUBE_API_KEY:
        return videos
    filtered = []
    for v in videos:
        try:
            # Lấy video view count
            v_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={v.video_id}&key={YOUTUBE_API_KEY}"
            v_res = requests.get(v_url, timeout=5).json()
            if not v_res.get("items"):
                continue
            views = int(v_res["items"][0]["statistics"].get("viewCount", 0))
            v.view_count = views
            
            # Lấy channel sub count
            if v.channel_id:
                c_url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={v.channel_id}&key={YOUTUBE_API_KEY}"
                c_res = requests.get(c_url, timeout=5).json()
                if c_res.get("items"):
                    subs = int(c_res["items"][0]["statistics"].get("subscriberCount", 0))
                else:
                    subs = 0
            else:
                subs = 0
                
            if views >= MIN_VIEWS_THRESHOLD and subs >= MIN_SUBS_THRESHOLD:
                print(f"      [OK] {v.title[:30]}... (Views: {views:,} | Subs: {subs:,})")
                filtered.append(v)
            else:
                print(f"      [SKIPPED] {v.title[:30]}... (Views: {views:,} | Subs: {subs:,} -> Không đạt ngưỡng {MIN_VIEWS_THRESHOLD}/{MIN_SUBS_THRESHOLD})")
                
        except Exception as e:
            pass
    return filtered
"""

content = content.replace("from language_detector import detect_community_language", "from language_detector import detect_community_language\n" + new_logic)

# Thay thế chỗ return discovered[:target_count]
content = content.replace("return discovered[:target_count]", "return fetch_stats_and_filter(discovered[:target_count*3])[:target_count]")
content = content.replace("if len(discovered) >= target_count:", "if len(discovered) >= target_count*3:")

with open('discovery.py', 'w') as f:
    f.write(content)
