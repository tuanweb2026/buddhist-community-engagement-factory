with open('youtube_publisher.py', 'r') as f:
    content = f.read()

# Remove old unused test code if present
if "def like_top_audience_comments" in content:
    content = content.split("def like_comment")[0]

new_methods = """
    def like_video(self, video_id: str) -> bool:
        \"\"\"
        Tự động thả Like cho Video mục tiêu bằng tài khoản @1995lido qua YouTube API
        \"\"\"
        if not self.service:
            return False
        try:
            self.service.videos().rate(id=video_id, rating="like").execute()
            print(f"  👍 [LIKE VIDEO] Đã thả Like thành công cho Video {video_id}!")
            return True
        except Exception as e:
            print(f"  [!] Không thể Like video {video_id}: {e}")
            return False
"""

content = content.strip() + "\n" + new_methods

with open('youtube_publisher.py', 'w') as f:
    f.write(content)
