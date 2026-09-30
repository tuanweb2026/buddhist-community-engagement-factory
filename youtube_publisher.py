"""
YouTube Publisher Module:
Thực thi xác thực OAuth, xác minh định danh kênh mục tiêu @1995lido
và publish comment thật qua YouTube Data API v3 chính thống.
Tuân thủ tuyệt đối: Kênh khác @1995lido -> HARD STOP!
"""

import os
import json
from typing import Optional, Dict, Any, Tuple
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app_config import CLIENT_SECRETS_FILE, TOKEN_STORAGE_FILE, TARGET_CHANNEL_HANDLE

SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

class YouTubePublisher:
    def __init__(self, target_handle: str = TARGET_CHANNEL_HANDLE):
        self.target_handle = target_handle
        self.service = None
        self.verified_channel_id = None
        self.verified_channel_title = None

    def authenticate(self) -> bool:
        """
        Xác thực người dùng qua OAuth 2.0.
        Sử dụng token.json đã lưu nếu có, hoặc yêu cầu đăng nhập qua browser flow.
        """
        creds = None
        if os.path.exists(TOKEN_STORAGE_FILE):
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_STORAGE_FILE, SCOPES)
            except Exception as e:
                print(f"[!] Lỗi đọc token.json: {e}")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"[!] Không thể refresh token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(CLIENT_SECRETS_FILE):
                    print(f"[!] Không tìm thấy {CLIENT_SECRETS_FILE}. Cần tải credentials từ Google Cloud Console.")
                    return False
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open(TOKEN_STORAGE_FILE, "w") as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"[!] Quá trình OAuth thất bại: {e}")
                    return False

        try:
            self.service = build("youtube", "v3", credentials=creds)
            return True
        except Exception as e:
            print(f"[!] Lỗi kết nối YouTube service: {e}")
            return False

    def verify_channel(self) -> Tuple[bool, str]:
        """
        Kiểm tra danh tính tài khoản đang đăng nhập.
        Bắt buộc phải khớp @1995lido. Nếu sai kênh -> HARD STOP!
        """
        if not self.service:
            return False, "Chưa xác thực service."

        try:
            res = self.service.channels().list(
                part="snippet,contentDetails",
                mine=True
            ).execute()

            items = res.get("items", [])
            if not items:
                return False, "Không tìm thấy thông tin kênh của tài khoản đăng nhập."

            channel_info = items[0]
            self.verified_channel_id = channel_info.get("id")
            snippet = channel_info.get("snippet", {})
            self.verified_channel_title = snippet.get("title", "")
            custom_url = snippet.get("customUrl", "").lower()

            # Chuẩn hóa so khớp handle
            expected = self.target_handle.lower().lstrip("@")
            actual = custom_url.lstrip("@")

            if expected not in actual and actual not in expected and expected not in self.verified_channel_title.lower():
                # HARD STOP nếu sai kênh
                return False, f"[HARD STOP] Tài khoản đăng nhập ({self.verified_channel_title}, {custom_url}) KHÔNG PHẢI {self.target_handle}!"

            return True, f"Xác nhận kênh thành công: {self.verified_channel_title} ({self.verified_channel_id})"

        except Exception as e:
            return False, f"Lỗi xác thực danh tính kênh: {str(e)}"

    def publish_comment(self, video_id: str, comment_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Đăng comment thật lên YouTube Video.
        Trả về (comment_id, error_message)
        """
        if not self.service:
            return None, "YouTube service chưa sẵn sàng."

        try:
            body = {
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
            response = self.service.commentThreads().insert(
                part="snippet",
                body=body
            ).execute()

            comment_id = response.get("id")
            return comment_id, None
        except Exception as e:
            return None, str(e)

    def get_comment_metrics(self, comment_thread_id: str) -> Dict[str, int]:
        """
        Lấy số like và số câu trả lời của 1 comment
        """
        metrics = {"likes": 0, "replies": 0}
        if not self.service:
            return metrics

        try:
            res = self.service.commentThreads().list(
                part="snippet,replies",
                id=comment_thread_id
            ).execute()
            items = res.get("items", [])
            if items:
                top_snippet = items[0]["snippet"]["topLevelComment"]["snippet"]
                metrics["likes"] = top_snippet.get("likeCount", 0)
                metrics["replies"] = items[0]["snippet"].get("totalReplyCount", 0)
        except Exception as e:
            print(f"[!] Không thể lấy metrics cho {comment_thread_id}: {e}")

        return metrics
