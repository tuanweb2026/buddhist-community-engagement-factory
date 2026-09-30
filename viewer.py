#!/usr/bin/env python3
"""
Dashboard dòng lệnh chuyên nghiệp (CLI Dashboard) dùng thư viện rich:
- Liệt kê các video đã quét
- Xem phân tích tâm lý khán giả
- Copy bình luận nhanh vào clipboard hoặc xuất file Markdown/CSV
"""

import sqlite3
import json
import os
from database import DB_PATH
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

def list_scanned_videos():
    if not os.path.exists(DB_PATH):
        console.print("[red]Chưa có cơ sở dữ liệu. Hãy chạy pipeline.py trước![/red]")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.video_id, v.title, v.channel_title, v.view_count, COUNT(c.comment_id), v.scanned_at
        FROM videos v
        LEFT JOIN comments c ON v.video_id = c.video_id
        GROUP BY v.video_id
        ORDER BY v.scanned_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    table = Table(title="📹 DANH SÁCH VIDEO ĐÃ THU THẬP & PHÂN TÍCH", show_lines=True)
    table.add_column("STT", style="cyan", width=4)
    table.add_column("Video ID", style="dim", width=12)
    table.add_column("Tiêu đề Video", style="bold green")
    table.add_column("Kênh", style="yellow", width=20)
    table.add_column("Views", justify="right", style="magenta")
    table.add_column("Comments đã lưu", justify="right", style="blue")

    for idx, row in enumerate(rows, 1):
        vid, title, channel, views, c_count, _ = row
        views_str = f"{views:,}" if views else "N/A"
        table.add_row(str(idx), vid, title, channel or "N/A", views_str, str(c_count))

    console.print(table)

def view_video_analysis(video_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT title, video_url, channel_title FROM videos WHERE video_id = ?", (video_id,))
    v_row = cursor.fetchone()
    if not v_row:
        console.print(f"[red]Không tìm thấy video với ID: {video_id}[/red]")
        conn.close()
        return

    title, url, channel = v_row
    
    cursor.execute("SELECT core_message, audience_emotions, top_pain_points, resonance_hooks FROM analyses WHERE video_id = ? ORDER BY id DESC LIMIT 1", (video_id,))
    a_row = cursor.fetchone()
    
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]\nKênh: [yellow]{channel}[/yellow] | Link: [blue underline]{url}[/blue underline]", title="Thông tin Video"))

    if a_row:
        core_msg, emotions, pain_points, hooks = a_row
        emotions_list = json.loads(emotions) if emotions else []
        pain_list = json.loads(pain_points) if pain_points else []
        hooks_list = json.loads(hooks) if hooks else []

        console.print(Panel(
            f"[bold]Thông điệp cốt lõi:[/bold] {core_msg}\n\n"
            f"[bold]Tâm lý / Cảm xúc người xem:[/bold] {', '.join(emotions_list)}\n\n"
            f"[bold]Điểm chạm / Nỗi niềm lớn nhất:[/bold]\n" + "\n".join([f"  • {p}" for p in pain_list]) + "\n\n"
            f"[bold]Góc tiếp cận gây đồng cảm:[/bold] {', '.join(hooks_list)}",
            title="🧠 Phân Tích Tâm Lý Khán Giả (AI Insights)",
            border_style="green"
        ))

    cursor.execute("SELECT id, style, hook_angle, suggested_comment, subtle_call_to_action FROM engagement_comments WHERE video_id = ?", (video_id,))
    comments = cursor.fetchall()
    
    console.print("\n[bold yellow]✨ CÁC MẪU COMMENT CHIẾN LƯỢC ĐƯỢC TẠO RA (HƯỚNG VỀ @1995lido):[/bold yellow]\n")
    for idx, c in enumerate(comments, 1):
        cid, style, angle, comment_txt, cta = c
        console.print(Panel(
            f"[bold cyan]Phong cách:[/bold cyan] {style}\n"
            f"[bold yellow]Góc dẫn dắt:[/bold yellow] {angle}\n"
            f"[bold green]Nội dung comment:[/bold green]\n{comment_txt}\n\n"
            f"[bold magenta]Mục tiêu chuyển đổi:[/bold magenta] {cta}",
            title=f"Mẫu #{idx} (Comment ID: {cid})",
            border_style="cyan"
        ))

    conn.close()

def export_to_markdown(output_file: str = "ENGAGEMENT_REPORT.md"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT video_id, title, video_url, channel_title FROM videos")
    videos = cursor.fetchall()
    
    md = "# ☸️ BÁO CÁO CHIẾN LƯỢC TƯƠNG TÁC PHẬT GIÁO CHO CHANNEL @1995lido\n\n"
    for v in videos:
        vid, title, url, channel = v
        md += f"## 📹 [{title}]({url})\n"
        md += f"- **Kênh**: {channel}\n"
        
        cursor.execute("SELECT core_message, audience_emotions, top_pain_points FROM analyses WHERE video_id = ? ORDER BY id DESC LIMIT 1", (vid,))
        a_row = cursor.fetchone()
        if a_row:
            core_msg, emotions, pain_points = a_row
            md += f"- **Thông điệp chính**: {core_msg}\n"
            md += f"- **Cảm xúc người xem**: {emotions}\n"
            md += f"- **Nỗi trăn trở phổ biến**: {pain_points}\n\n"
            
        cursor.execute("SELECT style, hook_angle, suggested_comment FROM engagement_comments WHERE video_id = ?", (vid,))
        comments = cursor.fetchall()
        md += "### 💬 Bình luận gợi ý đăng:\n"
        for c in comments:
            style, angle, txt = c
            md += f"#### Style: {style} (Góc nhìn: {angle})\n"
            md += f"> {txt}\n\n"
        md += "---\n\n"
        
    conn.close()
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md)
    console.print(f"[green]Đã xuất báo cáo ra file: {output_file}[/green]")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            list_scanned_videos()
        elif cmd == "view" and len(sys.argv) > 2:
            view_video_analysis(sys.argv[2])
        elif cmd == "export":
            export_to_markdown()
        else:
            print("Cách dùng:")
            print("  python viewer.py list          - Liệt kê các video đã quét")
            print("  python viewer.py view <id>     - Xem phân tích chi tiết & comment của 1 video")
            print("  python viewer.py export        - Xuất báo cáo đầy đủ ra file Markdown")
    else:
        list_scanned_videos()
