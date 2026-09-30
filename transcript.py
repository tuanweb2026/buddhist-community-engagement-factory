"""
Transcript Module: Lấy phụ đề bài giảng bằng youtube-transcript-api
Có cơ chế fallback an toàn, không làm crash luồng chạy
"""

from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript_text(video_id: str) -> Optional[str]:
    try:
        # Hỗ trợ phiên bản youtube-transcript-api mới nhất (v1.x)
        api = YouTubeTranscriptApi()
        if hasattr(api, "fetch"):
            fetched = api.fetch(video_id, languages=['vi', 'en'])
            texts = [snippet.text.strip() for snippet in fetched.snippets if snippet.text]
            full_text = " ".join(texts)
            if len(full_text.strip()) > 50:
                return full_text
    except Exception:
        pass

    try:
        # Fallback phiên bản cũ
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['vi', 'en'])
            texts = [item.get("text", "").strip() for item in transcript_list if item.get("text")]
            full_text = " ".join(texts)
            if len(full_text.strip()) > 50:
                return full_text
    except Exception:
        pass

    return None

