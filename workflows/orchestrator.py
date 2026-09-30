"""
Orchestrator trung tâm điều phối toàn bộ 10 Agents của BCE-Factory
Tuân thủ Supervised Autopilot & Nguyên tắc DRY-RUN bắt buộc
"""

import uuid
import json
from typing import List, Dict, Any, Optional

from database.repository import init_master_database, get_connection
from agents.discovery.discovery_agents import BuddhistDiscoveryAgent, OpportunityRankerAgent
from agents.research.research_agents import TranscriptAgent, VideoResearchAgent, BuddhistContextAgent
from agents.engagement.engagement_agents import CommentIntelligenceAgent, DiscussionGapAgent, BuddhistCommentWriterAgent
from agents.quality.quality_agents import CommentQualityGateAgent
from agents.analytics.analytics_agents import EngagementAnalyticsAgent
from connectors.youtube_connector import YouTubeConnector

class MasterOrchestrator:
    def __init__(self, target_channel_handle: str = "@1995lido"):
        self.target_handle = target_channel_handle
        init_master_database()
        
        # Identity Safety Check
        if self.target_handle != "@1995lido":
            raise ValueError(f"[HARD STOP] Kênh mục tiêu không khớp với cấu hình được cấp phép ({self.target_handle} != @1995lido)")

        # Khởi tạo 10 Agents
        self.discovery_agent = BuddhistDiscoveryAgent()
        self.ranker_agent = OpportunityRankerAgent()
        self.transcript_agent = TranscriptAgent()
        self.research_agent = VideoResearchAgent()
        self.context_agent = BuddhistContextAgent()
        self.intel_agent = CommentIntelligenceAgent()
        self.gap_agent = DiscussionGapAgent()
        self.writer_agent = BuddhistCommentWriterAgent()
        self.quality_gate_agent = CommentQualityGateAgent()
        self.analytics_agent = EngagementAnalyticsAgent()
        self.connector = YouTubeConnector()

    def run_cycle(self, keywords: List[str], limit_per_keyword: int = 2, dry_run: bool = True) -> Dict[str, Any]:
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        self.analytics_agent.log_run_event(run_id, "ORCHESTRATOR", "CYCLE_START", f"Bắt đầu chu kỳ quét với {len(keywords)} từ khóa.")
        
        print("\n" + "=" * 65)
        print(f"☸️  BCE-FACTORY: SUPERVISED AUTOPILOT CYCLE [{run_id}]")
        print(f"Target Channel Identity: {self.target_handle} | DRY_RUN: {dry_run}")
        print("=" * 65)

        # 1. DISCOVERY LAYER
        print("\n[Phase 1] 🔍 Discovery Layer: Quét video Phật giáo tiềm năng...")
        discovered_videos = self.discovery_agent.discover(keywords, limit_per_keyword=limit_per_keyword)
        print(f"  -> Đã tìm thấy và deduplicate: {len(discovered_videos)} video.")

        processed_count = 0
        conn = get_connection()
        cur = conn.cursor()

        for video in discovered_videos:
            print(f"\n--- [Đang xử lý Video: {video.video_id}] ---")
            print(f"Tiêu đề: {video.title}")
            print(f"Kênh: {video.channel_title}")

            # Lưu thông tin video vào DB
            cur.execute("""
                INSERT OR REPLACE INTO videos (video_id, channel_id, channel_title, title, url, description, duration, published_at, keyword_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (video.video_id, video.channel_id, video.channel_title, video.title, video.url, video.description, video.duration, video.published_at, video.keyword_source))

            # 2. OPPORTUNITY RANKER
            rank_res = self.ranker_agent.rank(video)
            print(f"  📊 Opportunity Score: {rank_res.total_score} (Đề xuất: {rank_res.recommended_for_research})")
            cur.execute("""
                INSERT OR REPLACE INTO opportunities (video_id, opportunity_score, breakdown_json, recommended, reasoning)
                VALUES (?, ?, ?, ?, ?)
            """, (video.video_id, rank_res.total_score, rank_res.model_dump_json(), rank_res.recommended_for_research, rank_res.reasoning))

            if not rank_res.recommended_for_research:
                print("  ⏭️ Bỏ qua nghiên cứu do điểm tiềm năng chưa đạt ngưỡng.")
                continue

            # 3. RESEARCH LAYER (Transcript + Knowledge Card + Buddhist Context)
            print("  📖 Research Layer: Lấy Transcript & xây dựng Knowledge Card...")
            transcript = self.transcript_agent.get_transcript(video.video_id)
            cur.execute("""
                INSERT OR REPLACE INTO transcripts (video_id, language, source, confidence, full_text)
                VALUES (?, ?, ?, ?, ?)
            """, (video.video_id, transcript.language, transcript.source, transcript.confidence, transcript.full_text))

            card = self.research_agent.build_knowledge_card(video.video_id, video.title, video.description, transcript)
            buddhist_ctx = self.context_agent.analyze_context(card)
            print(f"     Truyền thống: {buddhist_ctx.tradition} | Khái niệm: {', '.join(buddhist_ctx.key_concepts)}")

            # 4. COMMENT INTELLIGENCE & DISCUSSION GAP
            print("  🧠 Engagement Layer: Cào top comments & phát hiện Discussion Gap...")
            raw_comments = self.connector.get_comments(video.video_id, max_comments=15)
            analysis_report = self.intel_agent.analyze_comments(video.video_id, raw_comments)
            
            # Lưu comments vào DB
            for c in raw_comments:
                cur.execute("""
                    INSERT OR REPLACE INTO comments (comment_id, video_id, author, text, like_count, published_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (c.get("comment_id"), video.video_id, c.get("author"), c.get("text"), c.get("like_count"), c.get("published_at")))

            gap = self.gap_agent.find_gap(video.video_id, card, analysis_report)
            print(f"     💡 Discussion Gap phát hiện: [{gap.gap_type}] {gap.description[:90]}...")
            cur.execute("""
                INSERT INTO discussion_gaps (video_id, gap_type, description, confidence)
                VALUES (?, ?, ?, ?)
            """, (video.video_id, gap.gap_type, gap.description, gap.confidence))

            # 5. COMMENT WRITER AGENT (3 CANDIDATES)
            print("  ✍️ Sinh 3 ứng viên comment độc bản (Reflective, Insightful, Question-based)...")
            candidates = self.writer_agent.generate_candidates(video.video_id, card, gap, buddhist_ctx)

            # 6. QUALITY GATE AGENT (10 QUALITY GATES)
            print("  🛡️ Quality Layer: Kiểm duyệt qua 10 Quality Gates...")
            for cand in candidates:
                q_res = self.quality_gate_agent.evaluate(cand, card, gap)
                cur.execute("""
                    INSERT OR REPLACE INTO comment_drafts (candidate_id, video_id, style, hook_angle, content, intended_value, target_channel_ref)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (cand.candidate_id, cand.video_id, cand.style, cand.hook_angle, cand.content, cand.intended_value, cand.target_channel_ref))

                cur.execute("""
                    INSERT OR REPLACE INTO quality_results (candidate_id, passed_all, gate_breakdown_json, rejection_reason)
                    VALUES (?, ?, ?, ?)
                """, (cand.candidate_id, q_res.passed_all, json.dumps([g.model_dump() for g in q_res.gate_results], ensure_ascii=False), q_res.rejection_reason))

                status_label = "✅ ĐÃ QUA 10 GATES" if q_res.passed_all else f"❌ TỪ CHỐI ({q_res.rejection_reason})"
                print(f"     - [{cand.style}] {status_label}")

                # Đưa vào approval queue
                cur.execute("""
                    INSERT INTO approval_queue (candidate_id, video_id, status)
                    VALUES (?, ?, ?)
                """, (cand.candidate_id, video.video_id, "AWAITING_REVIEW" if q_res.passed_all else "REJECTED"))

            processed_count += 1

        conn.commit()
        conn.close()

        print("\n" + "=" * 65)
        print(f"🎉 HOÀN THÀNH CHU KỲ VẬN HÀNH [{run_id}]: {processed_count} video đã được nghiên cứu sâu.")
        print(f"Dữ liệu được lưu trong 'buddhist_engagement_factory.db'")
        print("=" * 65)
        return {"run_id": run_id, "processed_videos": processed_count}

if __name__ == "__main__":
    orchestrator = MasterOrchestrator()
    orchestrator.run_cycle(["thuyết pháp Thích Pháp Hòa", "thiền buông thư Thích Nhất Hạnh"], limit_per_keyword=1)
