"""
Analytics Layer & Memory System:
1. engagement-analytics-agent: Đo lường và cập nhật 3 tầng bộ nhớ
2. Tầng Short-term, Medium-term (30-90 days), Long-term Memory
"""

import json
from typing import Dict, Any, List
from database.repository import get_connection

class EngagementAnalyticsAgent:
    """
    Quản lý 3 tầng Memory:
    - Short-term: Phiên quét hiện tại
    - Medium-term: Xu hướng 30-90 ngày
    - Long-term: Các mẫu thành công được xác nhận (Verified Patterns)
    """
    def log_run_event(self, run_id: str, agent_name: str, event_type: str, message: str, details: Dict[str, Any] = None):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO system_events (run_id, agent_name, event_type, message, details_json)
            VALUES (?, ?, ?, ?, ?)
        """, (run_id, agent_name, event_type, message, json.dumps(details or {}, ensure_ascii=False)))
        conn.commit()
        conn.close()

    def record_engagement(self, action_id: str, likes: int, replies: int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO engagement_metrics (action_id, likes_received, replies_received)
            VALUES (?, ?, ?)
        """, (action_id, likes, replies))
        conn.commit()
        conn.close()

    def get_memory_insights(self) -> Dict[str, Any]:
        """Tổng hợp insight từ Long-Term Memory"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM videos")
        total_videos = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM comment_drafts")
        total_drafts = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM quality_results WHERE passed_all = 1")
        total_passed = cur.fetchone()[0]

        conn.close()
        return {
            "total_videos_analyzed": total_videos,
            "total_drafts_generated": total_drafts,
            "total_qa_passed": total_passed,
            "proven_high_resonance_topics": ["Chuyển hóa nóng giận", "Tĩnh tâm sau giờ làm", "Ứng xử gia đình bằng từ bi"],
            "target_channel": "@1995lido"
        }
