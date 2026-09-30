"""
Cấu hình tập trung cho BCE Factory Phase 2 — Real Publishing + Performance Tracking
"""

import os
from dotenv import load_dotenv

load_dotenv()

# YouTube Data API Key (Public calls) & OAuth Credentials (Publishing)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE", "client_secrets.json")
TOKEN_STORAGE_FILE = os.getenv("TOKEN_STORAGE_FILE", "token.json")

# LLM API Key (Gemini / OpenAI)
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY", "")

# Publish Modes: 'dry_run', 'supervised', 'autopilot'
PUBLISH_MODE = os.getenv("PUBLISH_MODE", "dry_run").lower()

# Daily Targets & Limits
DAILY_VIDEO_TARGET = int(os.getenv("DAILY_VIDEO_TARGET", 5))
MAX_VIDEOS_PER_DAY = int(os.getenv("MAX_VIDEOS_PER_DAY", 5))
MAX_COMMENTS_PER_VIDEO = int(os.getenv("MAX_COMMENTS_PER_VIDEO", 1))
MAX_COMMENTS_PER_DAY = int(os.getenv("MAX_COMMENTS_PER_DAY", 5))

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/bce.db")

# Cron & Health Management
JOB_STALE_MINUTES = int(os.getenv("JOB_STALE_MINUTES", 45))

# Target Identity
TARGET_CHANNEL_HANDLE = "@1995lido"

# Keywords Discovery
DISCOVERY_KEYWORDS = [
    # Tiếng Việt (Cộng đồng Việt Nam)
    "thuyết pháp Thích Pháp Hòa",
    "thiền buông thư Thích Nhất Hạnh",
    "lời Phật dạy về sự an lạc",
    "bài học buông bỏ khổ đau",
    # English (Foreign community)
    "Vipassana mindfulness meditation",
    "Buddhist wisdom compassion impermanence",
    "Ajahn Chah teachings",
    "Dalai Lama peace compassion"
]
