#!/usr/bin/env python3
"""
BCE Factory v1.0 — Phase 2: Real Publishing + Performance Tracking
Lệnh chạy:
  python main.py daily       - Chạy quy trình hàng ngày (3-5 videos, 1 comment duy nhất/video)
  python main.py track       - Cập nhật số like và reply của các comment đã publish (24h/48h)
  python main.py analytics   - Thống kê hiệu quả các phong cách comment sau khi có dữ liệu
"""

import sys
import os
import warnings
warnings.filterwarnings("ignore")
import uuid
from datetime import datetime
from typing import List, Dict, Any


from app_config import (
    DAILY_VIDEO_TARGET, MAX_COMMENTS_PER_VIDEO, MAX_COMMENTS_PER_DAY,
    PUBLISH_MODE, TARGET_CHANNEL_HANDLE
)
from db_storage import (
    init_database, is_video_processed, has_video_published, save_video, save_research,
    save_candidate_comment, save_published_comment, save_run,
    update_comment_performance, get_all_published_with_metrics
)
from discovery import discover_videos
from transcript import get_transcript_text
from comments import get_recent_comments
from research import research_video
from comment_generator import generate_candidates
from quality import check_duplicate, validate_quality, check_diversity_against_batch
from report import generate_phase2_daily_report

from youtube_publisher import YouTubePublisher

# Phase 2 Upgrade Modules
from channel_radar import ChannelRadar
from channel_intelligence import ChannelIntelligenceEngine
from video_inventory import VideoInventory
from video_queue import VideoPriorityQueue
from community_intelligence import CommunityIntelligenceEngine
from lido_improvement import LidoImprovementEngine

def run_daily_pipeline(dry_run_override: bool = False):
    date_str = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    current_publish_mode = "dry_run" if dry_run_override else PUBLISH_MODE

    print("=" * 68)
    print(f"☸️  BCE FACTORY v1.0 — PHASE 2 DAILY RUN [{date_str}]")
    print(f"Target Channel: {TARGET_CHANNEL_HANDLE} | Mode: {current_publish_mode.upper()}")
    print("=" * 68)

    init_database()

    # 1. Khởi tạo & Xác minh Publisher (Nếu chế độ không phải dry_run)
    publisher = YouTubePublisher()
    if current_publish_mode in ("supervised", "autopilot"):
        print("\n[Auth] 🔐 Đang xác thực tài khoản YouTube qua OAuth...")
        if not publisher.authenticate():
            print("[!] Xác thực OAuth thất bại hoặc chưa có token.json / client_secrets.json.")
            print("[!] Hệ thống tự động chuyển sang chế độ an toàn: DRY_RUN.")
            current_publish_mode = "dry_run"
        else:
            verified, msg = publisher.verify_channel()
            print(f"[Auth] {msg}")
            if not verified:
                print(f"[HARD STOP] {msg}")
                sys.exit(1)

    # 2. CHANNEL RADAR & CHANNEL INTELLIGENCE
    print("\n[1/8] 📡 CHANNEL RADAR: Quét & đồng bộ danh mục các kênh Phật giáo uy tín...")
    radar = ChannelRadar()
    monitored_channels = radar.scan_and_update()
    print(f"      -> Đang theo dõi {len(monitored_channels)} kênh Phật giáo trong Radar.")

    ci_engine = ChannelIntelligenceEngine()
    channel_cards = []
    channel_map = {}
    tier_counts = {"A_MAJOR": 0, "B_STRONG": 0, "C_RISING": 0, "D_EMERGING": 0}

    for ch in monitored_channels:
        tier_counts[ch.tier] = tier_counts.get(ch.tier, 0) + 1
        channel_map[ch.channel_id] = ch
        card = ci_engine.analyze_channel(ch)
        channel_cards.append(card)

    radar_summary = {
        "active_channels": len(monitored_channels),
        "tier_a_count": tier_counts.get("A_MAJOR", 0),
        "tier_b_count": tier_counts.get("B_STRONG", 0),
        "tier_cd_count": tier_counts.get("C_RISING", 0) + tier_counts.get("D_EMERGING", 0)
    }

    # 3. DISCOVER & INVENTORY INGESTION
    print(f"\n[2/8] 🔍 DISCOVER & INVENTORY: Tìm kiếm video Phật giáo tiềm năng...")
    inventory = VideoInventory()
    discovered = discover_videos(target_count=DAILY_VIDEO_TARGET + 5)

    # Ingest video từ các kênh trong radar nếu có
    for ch in monitored_channels[:3]:
        recent_ch_vids = inventory.fetch_channel_recent_videos(ch, max_results=3)
        discovered.extend(recent_ch_vids)

    # Ingest vào kho
    print(f"      -> Tổng cộng phát hiện {len(discovered)} video.")

    # 4. VIDEO PRIORITY QUEUE (Lọc chưa từng đăng comment & chấm điểm ưu tiên)
    print(f"\n[3/8] ⚖️ PRIORITY QUEUE: Chấm điểm và xếp hạng danh sách video...")
    eligible_videos = []
    skipped_records = []

    for v in discovered:
        if has_video_published(v.video_id):
            continue
        eligible_videos.append(v)

    queue = VideoPriorityQueue()
    ranked_videos = queue.rank_and_select(eligible_videos, channel_map=channel_map, top_k=DAILY_VIDEO_TARGET)
    selected_videos = [item[0] for item in ranked_videos]

    # Ingest các video đủ điều kiện vào kho
    ingested_count = inventory.ingest_videos(discovered)
    print(f"      -> {ingested_count} video mới nạp vào kho dữ liệu.")


    print(f"      -> Đã chọn {len(selected_videos)} video có độ ưu tiên cao nhất cho ngày hôm nay.")
    for idx, (v, sc) in enumerate(ranked_videos, 1):
        print(f"         #{idx:02d} [Score: {sc:.1f}] {v.title[:50]}... ({v.channel_name})")

    processed_records = []
    community_reports = []
    selected_comments_batch = []
    opening_counter = {}
    closing_counter = {}
    errors = []
    total_generated = 0
    total_published = 0

    # 4. PROCESS EACH VIDEO (CHỈ 1 COMMENT CUỐI CÙNG/VIDEO)
    for idx, video in enumerate(selected_videos, 1):
        if total_published >= MAX_COMMENTS_PER_DAY:
            print(f"\n[!] Đã đạt giới hạn tối đa trong ngày ({MAX_COMMENTS_PER_DAY} comments). Dừng chu trình.")
            break

        print(f"\n--- [Video #{idx:02d}]: {video.title[:55]}... ---")
        print(f"Kênh: {video.channel_name} | Ngôn ngữ: {video.language.upper()} | URL: {video.url}")

        try:
            # Transcript
            transcript = get_transcript_text(video.video_id)
            if transcript:
                print("  📖 Phụ đề: Đã lấy được transcript chính thức.")
            else:
                print("  ℹ️ Phụ đề: Không có phụ đề, sử dụng metadata và mô tả.")

            # Comments
            recent_comments = get_recent_comments(video.video_id, max_comments=10)
            print(f"  💬 Bình luận: Đã đọc {len(recent_comments)} bình luận của cộng đồng.")

            # Community Intelligence Engine
            comm_engine = CommunityIntelligenceEngine()
            comm_report = comm_engine.analyze_community(
                video_id=video.video_id,
                channel_id=video.channel_id,
                comments=recent_comments
            )
            community_reports.append(comm_report)

            # Understand & Research
            research = research_video(video, transcript, recent_comments)
            print(f"  🧠 Chủ đề cốt lõi: {research.main_topic}")
            print(f"  💡 Discussion Gap: {research.discussion_gap[:80]}...")

            # Generate 3-5 candidates
            candidates = generate_candidates(video, research, recent_comments)
            total_generated += len(candidates)
            for c in candidates:
                save_candidate_comment(c)

            # Evaluate & Select ONE BEST COMMENT (Khắt khe với đa dạng cấu trúc & mở/kết)
            best_candidate = None
            for cand in candidates:
                # 1. Duplicate check với lịch sử
                is_dup, dup_reason = check_duplicate(cand, video.channel_id or "", date_str)
                if is_dup:
                    continue

                # 2. Quality check cơ bản & liên kết evidence
                q_res = validate_quality(cand, research)
                if not q_res.passed:
                    continue

                # 3. Diversity check với các comment đã được chọn trong phiên hiện tại
                is_batch_dup, batch_reason = check_diversity_against_batch(
                    cand,
                    selected_comments_batch,
                    opening_counter=opening_counter,
                    closing_counter=closing_counter,
                    max_opening_repeat=1
                )
                if is_batch_dup:
                    continue

                best_candidate = cand
                break

            if not best_candidate:
                print("  ⚠️ Không có candidate nào vượt qua Quality & Duplicate check (NO_COMMENT).")
                skipped_records.append({
                    "title": video.title,
                    "video_id": video.video_id,
                    "reason": "Tất cả các candidates đều không vượt qua Quality Gate / Trùng lặp"
                })
                continue

            # Cập nhật bộ đếm mở đầu và kết bài cho candidate đã chọn
            c_text = best_candidate.content.strip()
            import re as _re
            _sentences = [s.strip().lower() for s in _re.split(r'[.!?]', c_text) if s.strip()]
            if _sentences:
                _op = _sentences[0]
                _cl = _sentences[-1]
                opening_counter[_op] = opening_counter.get(_op, 0) + 1
                closing_counter[_cl] = closing_counter.get(_cl, 0) + 1
            selected_comments_batch.append(best_candidate)

            print(f"  🎯 Đã chọn 1 COMMENT XUẤT SẮC NHẤT ({best_candidate.style} - {best_candidate.language.upper()} - Confidence: {best_candidate.research_confidence}):")
            print(f"     \"{best_candidate.content}\"")


            # 5. PUBLISH ACTION
            publish_status = "DRY_RUN"
            published_comment_id = None
            error_msg = None

            if PUBLISH_MODE == "dry_run":
                publish_status = "DRY_RUN"
                print("  🛡️ [DRY_RUN]: Đã lưu comment an toàn vào cơ sở dữ liệu (chưa đăng thật).")

            elif PUBLISH_MODE == "supervised":
                # PHASE 2.5 LIVE GUARD: Chỉ cho phép publish khi research_confidence == 'HIGH'
                if best_candidate.research_confidence != "HIGH":
                    print(f"  🛑 [SAFETY STOP] Chỉ candidate đạt HIGH confidence mới được phép Live Publish (hiện tại: {best_candidate.research_confidence}). Tự động chuyển sang DRY_RUN.")
                    publish_status = "DRY_RUN"
                else:
                    print("\n  👉 [SUPERVISED APPROVAL REQUIRED]")
                    print(f"  Bình luận sắp đăng lên: {video.title}")
                    print(f"  Nội dung: \"{best_candidate.content}\"")
                    confirm = input("  Xác nhận đăng bình luận này lên YouTube? (y/N): ").strip().lower()
                    if confirm == "y":
                        published_comment_id, error_msg = publisher.publish_comment(video.video_id, best_candidate.content)
                        publish_status = "PUBLISHED" if published_comment_id else "FAILED"
                        if published_comment_id:
                            print(f"  🚀 [THÀNH CÔNG] Đã đăng! Comment ID: {published_comment_id}")
                        else:
                            print(f"  🛑 [THẤT BẠI] Lỗi: {error_msg}")
                    else:
                        publish_status = "SKIPPED"
                        print("  ⏭️ Bỏ qua xuất bản theo yêu cầu của người giám sát.")

            elif PUBLISH_MODE == "autopilot":
                if best_candidate.research_confidence != "HIGH":
                    print(f"  🛑 [SAFETY STOP] Autopilot từ chối xuất bản vì confidence ({best_candidate.research_confidence}) không đạt HIGH.")
                    publish_status = "DRY_RUN"
                else:
                    published_comment_id, error_msg = publisher.publish_comment(video.video_id, best_candidate.content)
                    publish_status = "PUBLISHED" if published_comment_id else "FAILED"
                    if published_comment_id:
                        print(f"  🚀 [AUTOPILOT PUBLISHED] Comment ID: {published_comment_id}")
                    else:
                        print(f"  🛑 [AUTOPILOT FAILED] Lỗi: {error_msg}")


            from models import PublishResult
            pub_res = PublishResult(
                video_id=video.video_id,
                video_url=video.url,
                channel_name=video.channel_name,
                channel_id=video.channel_id,
                comment_id=published_comment_id,
                comment_text=best_candidate.content,
                language=best_candidate.language,
                published_at=now_str,
                status=publish_status,
                error_message=error_msg
            )

            # Lưu vào Database
            save_video(video)
            save_research(research)
            save_published_comment(pub_res)

            if publish_status in ("PUBLISHED", "DRY_RUN"):
                total_published += 1

            processed_records.append({
                "video": video,
                "research": research,
                "candidates": candidates,
                "selected_comment": best_candidate,
                "publish_result": pub_res
            })

        except Exception as e:
            err = f"Lỗi xử lý video {video.video_id}: {str(e)}"
            print(f"  🛑 {err}")
            errors.append(err)

    # 6. Lưu Run Record
    save_run(
        date_str=date_str,
        discovered=len(discovered),
        selected=len(selected_videos),
        generated=total_generated,
        published=total_published,
        skipped=len(skipped_records),
        errors=errors
    )

    # 7. LIDO IMPROVEMENT LOOP: Tổng hợp bài học và đề xuất cho @1995lido
    print(f"\n[7/8] 🪷 LIDO IMPROVEMENT: Tổng hợp bài học & chiến lược nội dung cho @1995lido...")
    lido_engine = LidoImprovementEngine()
    lido_insights = lido_engine.synthesize_insights(date_str, channel_cards, community_reports)
    lido_report_file = lido_engine.generate_lido_daily_report(date_str, lido_insights)
    print(f"      -> Đã sinh {len(lido_insights)} chiến lược phát triển tại: {lido_report_file}")

    # 8. Xuất Báo Cáo Chi Tiết Ngày (Audit Report)
    print(f"\n[8/8] 📋 AUDIT REPORT: Xuất báo cáo tổng hợp chu trình ngày...")
    community_snapshots = []
    for r, cr in zip(processed_records, community_reports):
        community_snapshots.append({
            "title": r["video"].title,
            "pain_points": cr.audience_pain_points,
            "desired_emotions": cr.desired_emotions
        })

    report_file = generate_phase2_daily_report(
        date_str=date_str,
        videos_discovered=len(discovered),
        videos_selected=len(selected_videos),
        processed_records=processed_records,
        skipped_records=skipped_records,
        errors=errors,
        radar_summary=radar_summary,
        community_insights=community_snapshots
    )

    print("\n" + "=" * 68)
    print(f"🎉 HOÀN TẤT CHU KỲ PHASE 2 DAILY RUN!")
    print(f"- Video đã xử lý & chọn comment: {len(processed_records)}")
    print(f"- Comment đã xuất bản ({current_publish_mode}): {total_published}")
    print(f"- Báo cáo kiểm toán chi tiết: {report_file}")
    print(f"- Báo cáo cải tiến kênh @1995lido: {lido_report_file}")
    print("=" * 68)

def track_performance():
    """Theo dõi số like & reply của các comment đã đăng"""
    print("=" * 68)
    print("📊 THEO DÕI HIỆU QUẢ BÌNH LUẬN (PERFORMANCE TRACKING)")
    print("=" * 68)

    publisher = YouTubePublisher()
    if not publisher.authenticate():
        print("[!] Cần xác thực OAuth để truy vấn metrics comment.")
        return

    items = get_all_published_with_metrics()
    if not items:
        print("Chưa có comment nào ở trạng thái PUBLISHED với comment_id hợp lệ.")
        return

    for item in items:
        cid = item.get("comment_id")
        if not cid:
            continue
        metrics = publisher.get_comment_metrics(cid)
        update_comment_performance(cid, metrics["likes"], metrics["replies"], period="24h")
        print(f"- Comment {cid} (Video: {item.get('video_id')}): {metrics['likes']} likes, {metrics['replies']} replies")

def show_analytics():
    """Báo cáo phân tích phong cách comment (Descriptive Analysis)"""
    print("=" * 68)
    print("📈 BÁO CÁO PHÂN TÍCH HIỆU QUẢ CÁC PHONG CÁCH BÌNH LUẬN")
    print("=" * 68)
    items = get_all_published_with_metrics()
    if len(items) < 3:
        print(f"Hiện có {len(items)} bình luận được xuất bản. Cần thêm dữ liệu để tổng hợp mẫu (30+ comments).")
        return

    styles = {}
    for it in items:
        st = it.get("style", "Reflective")
        if st not in styles:
            styles[st] = {"count": 0, "likes": 0, "replies": 0}
        styles[st]["count"] += 1
        styles[st]["likes"] += it.get("likes_24h", 0)
        styles[st]["replies"] += it.get("replies_24h", 0)

    for st, data in styles.items():
        avg_likes = data["likes"] / max(1, data["count"])
        avg_rep = data["replies"] / max(1, data["count"])
        print(f"\n[{st.upper()}]:")
        print(f"  • Số lượng: {data['count']}")
        print(f"  • Lượt thích trung bình: {avg_likes:.1f}")
        print(f"  • Phản hồi trung bình: {avg_rep:.1f}")

def run_discrete_job(job_name: str):
    """Thực thi các sub-job độc lập phục vụ macOS cron schedule với heartbeat tracking"""
    from db_storage import start_job_run, update_job_heartbeat, finish_job_run
    run_id = start_job_run(job_name)
    try:
        print(f"[*] Bắt đầu thực thi sub-job '{job_name}' (Run ID: {run_id})...")
        update_job_heartbeat(run_id)
        
        if job_name == "discovery":
            # Quét video & radar
            radar = ChannelRadar()
            radar.scan_and_update()
            inventory = VideoInventory()
            discovered = discover_videos(target_count=DAILY_VIDEO_TARGET + 5)
            inventory.ingest_videos(discovered)
            print(f"[+] Discovery hoàn tất. Đã nạp {len(discovered)} video vào kho.")

        elif job_name == "research":
            # Nghiên cứu các video ưu tiên trong kho
            inventory = VideoInventory()
            eligible = inventory.get_unprocessed_videos(limit=DAILY_VIDEO_TARGET)
            for v in eligible:
                update_job_heartbeat(run_id)
                transcript = get_transcript_text(v.video_id)
                comments = get_recent_comments(v.video_id, max_comments=10)
                research = research_video(v, transcript, comments)
                save_video(v)
                save_research(research)
                print(f"[+] Đã nghiên cứu xong video: {v.title[:45]}...")

        elif job_name.startswith("engagement"):
            # Chạy 1 slot engagement duy nhất
            print(f"[*] Thực thi engagement slot: {job_name}")
            run_daily_pipeline()

        elif job_name == "daily_report":
            # Xuất báo cáo tổng kết ngày
            date_str = datetime.now().strftime("%Y-%m-%d")
            report_file = generate_phase2_daily_report(
                date_str=date_str,
                videos_discovered=0,
                videos_selected=0,
                processed_records=[],
                skipped_records=[],
                errors=[]
            )
            print(f"[+] Báo cáo ngày đã tạo tại: {report_file}")

        elif job_name == "tracking":
            track_performance()

        finish_job_run(run_id, status="COMPLETED")
        print(f"[+] Sub-job '{job_name}' kết thúc thành công.")
    except Exception as e:
        finish_job_run(run_id, status="FAILED", error=str(e))
        print(f"[!] Sub-job '{job_name}' thất bại: {e}")
        sys.exit(1)

if __name__ == "__main__":
    is_dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    cmd = args[0].lower() if args else "daily"

    if cmd == "daily":
        run_daily_pipeline(dry_run_override=is_dry_run)
    elif cmd == "track":
        track_performance()
    elif cmd == "analytics":
        show_analytics()
    elif cmd == "health":
        from health_engine import print_health_report
        print_health_report()
    elif cmd == "cron-status":
        from health_engine import print_cron_status
        print_cron_status()
    elif cmd in ("discovery", "research", "daily_report", "tracking") or cmd.startswith("engagement"):
        run_discrete_job(cmd)
    else:
        print("Lệnh hỗ trợ: python main.py [daily [--dry-run] | health | cron-status | track | analytics | discovery | research | engagement | daily_report]")


