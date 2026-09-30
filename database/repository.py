"""
Database Module chuẩn hoá 15 Relational Tables theo Master Build Prompt
Hỗ trợ SQLite và Clean Repository Pattern (Dễ dàng migrate PostgreSQL)
"""

import sqlite3
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

DATABASE_FILE = "buddhist_engagement_factory.db"

def get_connection(db_file: str = DATABASE_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def init_master_database(db_file: str = DATABASE_FILE):
    conn = get_connection(db_file)
    cur = conn.cursor()

    # 1. channels
    cur.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        channel_id TEXT PRIMARY KEY,
        channel_handle TEXT,
        channel_title TEXT,
        channel_url TEXT,
        subscriber_count INTEGER DEFAULT 0,
        video_count INTEGER DEFAULT 0,
        view_count INTEGER DEFAULT 0,
        is_target_channel BOOLEAN DEFAULT 0,
        verified_at TIMESTAMP
    );
    """)

    # 2. videos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT PRIMARY KEY,
        channel_id TEXT,
        channel_title TEXT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        description TEXT,
        duration INTEGER DEFAULT 0,
        published_at TEXT,
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        keyword_source TEXT,
        status TEXT DEFAULT 'DISCOVERED'
    );
    """)

    # 3. video_metrics
    cur.execute("""
    CREATE TABLE IF NOT EXISTS video_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT NOT NULL,
        view_count INTEGER DEFAULT 0,
        like_count INTEGER DEFAULT 0,
        comment_count INTEGER DEFAULT 0,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    );
    """)

    # 4. transcripts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transcripts (
        video_id TEXT PRIMARY KEY,
        language TEXT,
        source TEXT,
        confidence REAL,
        full_text TEXT,
        segments_json TEXT,
        retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    );
    """)

    # 5. comments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        comment_id TEXT PRIMARY KEY,
        video_id TEXT NOT NULL,
        author TEXT,
        text TEXT NOT NULL,
        like_count INTEGER DEFAULT 0,
        published_at TEXT,
        category TEXT,
        extracted_pain_point TEXT,
        analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    );
    """)

    # 6. comment_clusters
    cur.execute("""
    CREATE TABLE IF NOT EXISTS comment_clusters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT NOT NULL,
        cluster_name TEXT,
        cluster_theme TEXT,
        comment_count INTEGER DEFAULT 0,
        representative_quotes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. discussion_gaps
    cur.execute("""
    CREATE TABLE IF NOT EXISTS discussion_gaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT NOT NULL,
        gap_type TEXT NOT NULL,
        description TEXT NOT NULL,
        evidence_comment_ids TEXT,
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    );
    """)

    # 8. opportunities
    cur.execute("""
    CREATE TABLE IF NOT EXISTS opportunities (
        video_id TEXT PRIMARY KEY,
        opportunity_score REAL NOT NULL,
        breakdown_json TEXT,
        recommended BOOLEAN DEFAULT 1,
        reasoning TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    );
    """)

    # 9. comment_drafts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS comment_drafts (
        candidate_id TEXT PRIMARY KEY,
        video_id TEXT NOT NULL,
        style TEXT NOT NULL,
        hook_angle TEXT,
        content TEXT NOT NULL,
        intended_value TEXT,
        target_channel_ref TEXT DEFAULT '@1995lido',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    );
    """)

    # 10. quality_results
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quality_results (
        candidate_id TEXT PRIMARY KEY,
        passed_all BOOLEAN NOT NULL,
        gate_breakdown_json TEXT NOT NULL,
        rejection_reason TEXT,
        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (candidate_id) REFERENCES comment_drafts(candidate_id)
    );
    """)

    # 11. approval_queue
    cur.execute("""
    CREATE TABLE IF NOT EXISTS approval_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL,
        video_id TEXT NOT NULL,
        status TEXT DEFAULT 'AWAITING_REVIEW', -- AWAITING_REVIEW, APPROVED, REJECTED, PUBLISHED
        reviewer_notes TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (candidate_id) REFERENCES comment_drafts(candidate_id)
    );
    """)

    # 12. actions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS actions (
        action_id TEXT PRIMARY KEY,
        candidate_id TEXT NOT NULL,
        action_type TEXT DEFAULT 'POST_COMMENT',
        is_dry_run BOOLEAN DEFAULT 1,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT,
        platform_response TEXT
    );
    """)

    # 13. engagement_metrics
    cur.execute("""
    CREATE TABLE IF NOT EXISTS engagement_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_id TEXT NOT NULL,
        likes_received INTEGER DEFAULT 0,
        replies_received INTEGER DEFAULT 0,
        profile_visits_estimated INTEGER DEFAULT 0,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 14. experiments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS experiments (
        experiment_id TEXT PRIMARY KEY,
        hypothesis TEXT,
        target_style TEXT,
        status TEXT DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 15. system_events
    cur.execute("""
    CREATE TABLE IF NOT EXISTS system_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT,
        agent_name TEXT,
        event_type TEXT,
        message TEXT,
        details_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_master_database()
    print("Khởi tạo thành công 15 bảng theo Master Schema của BCE-Factory!")
