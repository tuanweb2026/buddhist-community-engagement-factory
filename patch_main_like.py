with open('main.py', 'r') as f:
    content = f.read()

old_sup = """                        if published_comment_id:
                            print(f"  🚀 [THÀNH CÔNG] Đã đăng! Comment ID: {published_comment_id}")"""

new_sup = """                        if published_comment_id:
                            print(f"  🚀 [THÀNH CÔNG] Đã đăng! Comment ID: {published_comment_id}")
                            publisher.like_video(video.video_id)"""

old_auto = """                    if published_comment_id:
                        print(f"  🚀 [AUTOPILOT PUBLISHED] Comment ID: {published_comment_id}")"""

new_auto = """                    if published_comment_id:
                        print(f"  🚀 [AUTOPILOT PUBLISHED] Comment ID: {published_comment_id}")
                        publisher.like_video(video.video_id)"""

content = content.replace(old_sup, new_sup).replace(old_auto, new_auto)
with open('main.py', 'w') as f:
    f.write(content)
