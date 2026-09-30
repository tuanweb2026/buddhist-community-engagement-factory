#!/usr/bin/env python3
"""
Dashboard V1 chuyên nghiệp cho BCE-Factory theo Master Prompt Specification:
Hiển thị các trạng thái quy trình:
DISCOVERED -> RESEARCHED -> HIGH OPPORTUNITY -> DRAFTED -> QA PASSED -> AWAITING REVIEW -> PUBLISHED -> REJECTED
Xem chi tiết từng Opportunity: VIDEO, CHANNEL, WHY SELECTED, TRANSCRIPT, DISCUSSION GAP, CANDIDATES, QUALITY RESULTS.
"""

import sys
import json
from database.repository import get_connection
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def show_funnel_summary():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM videos")
    discovered = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM opportunities WHERE recommended = 1")
    high_opp = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transcripts WHERE full_text IS NOT NULL AND length(full_text) > 0")
    researched = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM comment_drafts")
    drafted = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM quality_results WHERE passed_all = 1")
    qa_passed = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM approval_queue WHERE status = 'AWAITING_REVIEW'")
    awaiting = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM approval_queue WHERE status = 'REJECTED'")
    rejected = cur.fetchone()[0]

    conn.close()

    table = Table(title="☸️ BCE-FACTORY: SUPERVISED AUTOPILOT FUNNEL", show_lines=True)
    table.add_column("GIAI ĐOẠN (PIPELINE STAGE)", style="bold cyan")
    table.add_column("SỐ LƯỢNG", justify="center", style="bold yellow")
    table.add_column("MÔ TẢ TRẠNG THÁI", style="green")

    table.add_row("1. DISCOVERED", str(discovered), "Video Phật giáo đã tìm kiếm & deduplicate")
    table.add_row("2. HIGH OPPORTUNITY", str(high_opp), "Video đạt điểm tiềm năng tương tác cao (Score >= 0.65)")
    table.add_row("3. RESEARCHED", str(researched), "Đã trích xuất Transcript & xây dựng Knowledge Card")
    table.add_row("4. DRAFTED", str(drafted), "Số lượng bản nháp comment đã tạo (3 Candidates/video)")
    table.add_row("5. QA PASSED", str(qa_passed), "Vượt qua toàn diện 10 Quality Gates")
    table.add_row("6. AWAITING REVIEW", str(awaiting), "Chờ người quản trị xác nhận (Supervised Autopilot)")
    table.add_row("7. REJECTED", str(rejected), "Bị từ chối do vi phạm chất lượng / chính sách an toàn")

    console.print(table)

def list_opportunities():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.video_id, v.title, v.channel_title, o.opportunity_score, o.recommended, v.url
        FROM videos v
        LEFT JOIN opportunities o ON v.video_id = o.video_id
        ORDER BY o.opportunity_score DESC
    """)
    rows = cur.fetchall()
    conn.close()

    table = Table(title="📹 DANH SÁCH CƠ HỘI TƯƠNG TÁC (OPPORTUNITY LIST)", show_lines=True)
    table.add_column("STT", style="dim", width=4)
    table.add_column("Video ID", style="cyan", width=12)
    table.add_column("Tiêu đề Video", style="bold white")
    table.add_column("Kênh", style="yellow", width=22)
    table.add_column("Opportunity Score", justify="center", style="magenta")
    table.add_column("Đề xuất Research", justify="center", style="green")

    for idx, r in enumerate(rows, 1):
        vid, title, channel, score, rec, _ = r
        score_str = f"{score:.3f}" if score is not None else "N/A"
        rec_str = "✅ YES" if rec else "❌ NO"
        table.add_row(str(idx), vid, title, channel or "N/A", score_str, rec_str)

    console.print(table)

def view_opportunity_detail(video_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT title, channel_title, url, description FROM videos WHERE video_id = ?", (video_id,))
    v_row = cur.fetchone()
    if not v_row:
        console.print(f"[red]Không tìm thấy video ID: {video_id}[/red]")
        conn.close()
        return

    title, channel, url, desc = v_row
    
    cur.execute("SELECT opportunity_score, reasoning FROM opportunities WHERE video_id = ?", (video_id,))
    o_row = cur.fetchone()

    cur.execute("SELECT source, language, full_text FROM transcripts WHERE video_id = ?", (video_id,))
    t_row = cur.fetchone()

    cur.execute("SELECT gap_type, description FROM discussion_gaps WHERE video_id = ? ORDER BY id DESC LIMIT 1", (video_id,))
    g_row = cur.fetchone()

    has_trans = bool(t_row and t_row[2] and len(t_row[2].strip()) > 0)
    trans_desc = f"Có phụ đề ({t_row[0]} - {t_row[1]})" if has_trans else "Không có phụ đề (Sử dụng ngữ cảnh tiêu đề & mô tả bài giảng)"

    console.print(Panel(
        f"[bold white]{title}[/bold white]\n"
        f"Kênh: [yellow]{channel}[/yellow] | Link: [blue underline]{url}[/blue underline]\n\n"
        f"[bold cyan]Lý do chọn (Why Selected):[/bold cyan] {o_row[1] if o_row else 'N/A'}\n"
        f"[bold magenta]Trạng thái Transcript:[/bold magenta] {trans_desc}\n"
        f"[bold green]Discussion Gap (Khoảng trống thảo luận):[/bold green]\n"
        f"  • Loại: {g_row[0] if g_row else 'N/A'}\n"
        f"  • Chi tiết: {g_row[1] if g_row else 'N/A'}",
        title=f"🔎 CHI TIẾT CƠ HỘI TƯƠNG TÁC: {video_id}",
        border_style="cyan"
    ))

    # Candidates và kết quả 10 Quality Gates
    cur.execute("""
        SELECT c.candidate_id, c.style, c.hook_angle, c.content, c.intended_value, q.passed_all, q.gate_breakdown_json, q.rejection_reason
        FROM comment_drafts c
        LEFT JOIN quality_results q ON c.candidate_id = q.candidate_id
        WHERE c.video_id = ?
    """, (video_id,))
    candidates = cur.fetchall()

    console.print("\n[bold yellow]✨ ỨNG VIÊN BÌNH LUẬN & KẾT QUẢ 10 QUALITY GATES:[/bold yellow]\n")
    for cand in candidates:
        cid, style, hook, content, val, passed, breakdown_json, rej_reason = cand
        gate_status = "[bold green]✅ ĐÃ VƯỢT QUA 10 QUALITY GATES (READY FOR REVIEW)[/bold green]" if passed else f"[bold red]❌ REJECTED ({rej_reason})[/bold red]"
        
        console.print(Panel(
            f"[bold cyan]Ứng viên:[/bold cyan] {cid} | [bold yellow]Phong cách:[/bold yellow] {style}\n"
            f"[bold magenta]Góc tiếp cận (Hook Angle):[/bold magenta] {hook}\n"
            f"[bold]Giá trị mang lại:[/bold] {val}\n\n"
            f"[bold white]Nội dung bình luận:[/bold white]\n{content}\n\n"
            f"[bold]Đánh giá Quality Gate:[/bold] {gate_status}",
            title=f"Candidate: {style}",
            border_style="green" if passed else "red"
        ))

    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "funnel":
            show_funnel_summary()
        elif cmd == "list":
            list_opportunities()
        elif cmd == "view" and len(sys.argv) > 2:
            view_opportunity_detail(sys.argv[2])
    else:
        show_funnel_summary()
        print("\nCách dùng lệnh:")
        print("  python dashboard/terminal_dashboard.py funnel       - Xem báo cáo Pipeline Funnel tổng thể")
        print("  python dashboard/terminal_dashboard.py list         - Liệt kê danh sách video kèm Opportunity Score")
        print("  python dashboard/terminal_dashboard.py view <id>    - Xem chi tiết Knowledge Card, Gap, 3 Candidates & 10 Gates")
