"""
Database Storage Module cho Phase 2:
Quản lý 5 bảng SQLite chuẩn xác theo đặc tả Phase 2:
1. videos
2. research
3. comments
4. published_comments
5. runs
"""

import sqlite3
import os
import json
from typing import Optional, List, Dict, Any
from app_config import DATABASE_PATH
from models import VideoMetadata, VideoResearch, CommentCandidate, PublishResult

def get_connection(db_path: str = DATABASE_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_database(db_path: str = DATABASE_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()

    # 1. videos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT UNIQUE NOT NULL,
        channel_id TEXT,
        channel_name TEXT,
        channel_handle TEXT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        published_at TEXT,
        views_at_research INTEGER DEFAULT 0,
        description TEXT,
        language TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. research
    cur.execute("""
    CREATE TABLE IF NOT EXISTS research (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT UNIQUE NOT NULL,
        summary TEXT,
        main_topic TEXT,
        buddhist_context TEXT,
        key_points TEXT,
        discussion_gaps TEXT,
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    );
    """)

    # 3. comments (candidates generated)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT UNIQUE,
        video_id TEXT NOT NULL,
        comment_text TEXT NOT NULL,
        language TEXT,
        style TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'GENERATED',
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    );
    """)

    # 4. published_comments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS published_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT NOT NULL,
        channel_id TEXT,
        comment_id TEXT,
        comment_text TEXT NOT NULL,
        language TEXT,
        published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL,
        error_message TEXT,
        likes_24h INTEGER DEFAULT 0,
        replies_24h INTEGER DEFAULT 0,
        likes_48h INTEGER DEFAULT 0,
        replies_48h INTEGER DEFAULT 0,
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    );
    """)

    # 5. runs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date TEXT NOT NULL,
        videos_discovered INTEGER DEFAULT 0,
        videos_selected INTEGER DEFAULT 0,
        comments_generated INTEGER DEFAULT 0,
        comments_published INTEGER DEFAULT 0,
        comments_skipped INTEGER DEFAULT 0,
        errors TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. channels (Phase 2 Upgrade - Channel Radar)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        channel_id TEXT PRIMARY KEY,
        channel_name TEXT NOT NULL,
        channel_handle TEXT,
        channel_url TEXT,
        language TEXT DEFAULT 'vi',
        subscriber_count INTEGER DEFAULT 0,
        video_count INTEGER DEFAULT 0,
        tradition TEXT DEFAULT 'General Buddhism',
        tier TEXT DEFAULT 'D_EMERGING',
        status TEXT DEFAULT 'ACTIVE',
        last_scanned_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. channel_intelligence
    cur.execute("""
    CREATE TABLE IF NOT EXISTS channel_intelligence (
        channel_id TEXT PRIMARY KEY,
        channel_name TEXT,
        content_strengths TEXT,
        audience_engagement_level TEXT,
        top_performing_topics TEXT,
        comment_community_vibe TEXT,
        recurring_questions TEXT,
        lido_learnings TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
    );
    """)

    # 8. lido_insights
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lido_insights (
        insight_id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        observation TEXT,
        interpretation TEXT,
        opportunity_for_lido TEXT,
        priority TEXT DEFAULT 'MEDIUM',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 9. job_runs (Self-Recovery & Health Management)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_runs (
        run_id TEXT PRIMARY KEY,
        job_type TEXT NOT NULL,
        started_at TEXT NOT NULL,
        heartbeat_at TEXT NOT NULL,
        finished_at TEXT,
        status TEXT NOT NULL,
        error TEXT
    );
    """)

    # 10. recovery_events (Watchdog & Recovery Event Log)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recovery_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_time TEXT NOT NULL,
        event_type TEXT NOT NULL,
        description TEXT NOT NULL,
        action_taken TEXT NOT NULL,
        result TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

# Job Runs & Heartbeat Management
def start_job_run(job_type: str, run_id: Optional[str] = None, db_path: str = DATABASE_PATH) -> str:
    import uuid
    from datetime import datetime
    r_id = run_id or f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO job_runs (run_id, job_type, started_at, heartbeat_at, status, error)
        VALUES (?, ?, ?, ?, 'RUNNING', NULL)
    """, (r_id, job_type, now_str, now_str))
    conn.commit()
    conn.close()
    return r_id

def update_job_heartbeat(run_id: str, db_path: str = DATABASE_PATH):
    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE job_runs SET heartbeat_at = ? WHERE run_id = ?", (now_str, run_id))
    conn.commit()
    conn.close()

def finish_job_run(run_id: str, status: str = "COMPLETED", error: Optional[str] = None, db_path: str = DATABASE_PATH):
    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        UPDATE job_runs
        SET finished_at = ?, heartbeat_at = ?, status = ?, error = ?
        WHERE run_id = ?
    """, (now_str, now_str, status, error, run_id))
    conn.commit()
    conn.close()

def record_missed_job(job_type: str, scheduled_time: str, reason: str = "Mac offline or schedule skipped", db_path: str = DATABASE_PATH):
    import uuid
    from datetime import datetime
    r_id = f"missed_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO job_runs (run_id, job_type, started_at, heartbeat_at, finished_at, status, error)
        VALUES (?, ?, ?, ?, ?, 'MISSED', ?)
    """, (r_id, job_type, scheduled_time, now_str, now_str, reason))
    conn.commit()
    conn.close()

def log_recovery_event(event_type: str, description: str, action_taken: str, result: str, db_path: str = DATABASE_PATH):
    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO recovery_events (event_time, event_type, description, action_taken, result)
        VALUES (?, ?, ?, ?, ?)
    """, (now_str, event_type, description, action_taken, result))
    conn.commit()
    conn.close()

def get_last_job_by_type(job_type: str, db_path: str = DATABASE_PATH) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM job_runs
        WHERE job_type = ? AND status = 'COMPLETED'
        ORDER BY finished_at DESC LIMIT 1
    """, (job_type,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_stale_or_running_jobs(stale_minutes: int = 45, db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    from datetime import datetime, timedelta
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM job_runs WHERE status = 'RUNNING'")
    rows = cur.fetchall()
    conn.close()
    
    stale_jobs = []
    now = datetime.now()
    threshold = timedelta(minutes=stale_minutes)
    
    for r in rows:
        d = dict(r)
        hb_str = d.get("heartbeat_at") or d.get("started_at")
        try:
            hb_dt = datetime.strptime(hb_str, "%Y-%m-%d %H:%M:%S")
            if (now - hb_dt) > threshold:
                d["is_stale"] = True
            else:
                d["is_stale"] = False
        except Exception:
            d["is_stale"] = True
        stale_jobs.append(d)
    return stale_jobs



# Duplicate & Frequency Checkers
def is_video_processed(video_id: str, db_path: str = DATABASE_PATH) -> bool:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM videos WHERE video_id = ?", (video_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row)

def has_video_published(video_id: str, db_path: str = DATABASE_PATH) -> bool:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM published_comments WHERE video_id = ? AND status IN ('PUBLISHED', 'DRY_RUN')", (video_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row)



def get_channel_published_count_today(channel_id: str, date_str: str, db_path: str = DATABASE_PATH) -> int:
    if not channel_id:
        return 0
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM published_comments
        WHERE channel_id = ? AND date(published_at) = date(?) AND status IN ('PUBLISHED', 'DRY_RUN')
    """, (channel_id, date_str))
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_all_past_comments(db_path: str = DATABASE_PATH) -> List[str]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT comment_text FROM published_comments WHERE status IN ('PUBLISHED', 'DRY_RUN')")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

# Persistence Functions
def save_video(v: VideoMetadata, db_path: str = DATABASE_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO videos (
            video_id, channel_id, channel_name, channel_handle,
            title, url, published_at, views_at_research, description, language
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        v.video_id, v.channel_id, v.channel_name, v.channel_handle,
        v.title, v.url, v.published_at, v.view_count, v.description[:2000], v.language
    ))
    conn.commit()
    conn.close()

def save_research(r: VideoResearch, db_path: str = DATABASE_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO research (
            video_id, summary, main_topic, buddhist_context,
            key_points, discussion_gaps, confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        r.video_id, r.summary, r.main_topic, r.buddhist_context,
        "\n".join(r.key_points), r.discussion_gap, r.confidence
    ))
    conn.commit()
    conn.close()

def save_candidate_comment(c: CommentCandidate, status: str = "CANDIDATE", db_path: str = DATABASE_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO comments (candidate_id, video_id, comment_text, language, style, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (c.candidate_id, c.video_id, c.content, c.language, c.style, status))
    conn.commit()
    conn.close()

# Alias tương thích ngược cho Phase 1
def save_comment(c: CommentCandidate, channel_id: Optional[str] = None, status: str = "CANDIDATE", db_path: str = DATABASE_PATH):
    save_candidate_comment(c, status=status, db_path=db_path)

def save_published_comment(res: PublishResult, db_path: str = DATABASE_PATH) -> int:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO published_comments (
            video_id, channel_id, comment_id, comment_text,
            language, published_at, status, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        res.video_id, res.channel_id, res.comment_id, res.comment_text,
        res.language, res.published_at, res.status, res.error_message
    ))
    row_id = cur.lastrowid
    conn.commit()
    conn.close()
    return row_id

def save_run(
    date_str: str,
    discovered: int,
    selected: int,
    generated: int,
    published: int,
    skipped: int,
    errors: List[str],
    db_path: str = DATABASE_PATH
):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO runs (
            run_date, videos_discovered, videos_selected,
            comments_generated, comments_published, comments_skipped, errors
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        date_str, discovered, selected, generated, published, skipped, "\n".join(errors)
    ))
    conn.commit()
    conn.close()

def update_comment_performance(comment_id: str, likes: int, replies: int, period: str = "24h", db_path: str = DATABASE_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()
    if period == "24h":
        cur.execute("UPDATE published_comments SET likes_24h = ?, replies_24h = ? WHERE comment_id = ?", (likes, replies, comment_id))
    elif period == "48h":
        cur.execute("UPDATE published_comments SET likes_48h = ?, replies_48h = ? WHERE comment_id = ?", (likes, replies, comment_id))
    conn.commit()
    conn.close()

def get_all_published_with_metrics(db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT p.comment_id, p.video_id, p.channel_id, p.comment_text, p.language,
               p.published_at, p.status, p.likes_24h, p.replies_24h, p.likes_48h, p.replies_48h,
               c.style
        FROM published_comments p
        LEFT JOIN comments c ON p.comment_text = c.comment_text
        WHERE p.status = 'PUBLISHED'
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Channel Radar & Intelligence Storage ---

def save_channel(channel: Dict[str, Any], db_path: str = DATABASE_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO channels (
            channel_id, channel_name, channel_handle, channel_url,
            language, subscriber_count, video_count, tradition,
            tier, status, last_scanned_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        channel.get("channel_id"), channel.get("channel_name"),
        channel.get("channel_handle"), channel.get("channel_url"),
        channel.get("language", "vi"), channel.get("subscriber_count", 0),
        channel.get("video_count", 0), channel.get("tradition", "General Buddhism"),
        channel.get("tier", "D_EMERGING"), channel.get("status", "ACTIVE"),
        channel.get("last_scanned_at")
    ))
    conn.commit()
    conn.close()

def get_channel(channel_id: str, db_path: str = DATABASE_PATH) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM channels WHERE channel_id = ?", (channel_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_active_channels(db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM channels WHERE status = 'ACTIVE' ORDER BY subscriber_count DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_channel_intelligence(ci: Dict[str, Any], db_path: str = DATABASE_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO channel_intelligence (
            channel_id, channel_name, content_strengths,
            audience_engagement_level, top_performing_topics,
            comment_community_vibe, recurring_questions,
            lido_learnings, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        ci.get("channel_id"), ci.get("channel_name"),
        json.dumps(ci.get("content_strengths", []), ensure_ascii=False),
        ci.get("audience_engagement_level", "Moderate"),
        json.dumps(ci.get("top_performing_topics", []), ensure_ascii=False),
        ci.get("comment_community_vibe", ""),
        json.dumps(ci.get("recurring_questions", []), ensure_ascii=False),
        json.dumps(ci.get("lido_learnings", []), ensure_ascii=False)
    ))
    conn.commit()
    conn.close()

def get_channel_intelligence(channel_id: str, db_path: str = DATABASE_PATH) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM channel_intelligence WHERE channel_id = ?", (channel_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    for f in ["content_strengths", "top_performing_topics", "recurring_questions", "lido_learnings"]:
        if d.get(f):
            try:
                d[f] = json.loads(d[f])
            except Exception:
                pass
    return d

def save_lido_insight(insight: Dict[str, Any], db_path: str = DATABASE_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO lido_insights (
            insight_id, date, category, observation, interpretation, opportunity_for_lido, priority
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        insight.get("insight_id"), insight.get("date"),
        insight.get("category"), insight.get("observation"),
        insight.get("interpretation"), insight.get("opportunity_for_lido"),
        insight.get("priority", "MEDIUM")
    ))
    conn.commit()
    conn.close()

def get_lido_insights_by_date(date_str: str, db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM lido_insights WHERE date = ? ORDER BY priority DESC", (date_str,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

