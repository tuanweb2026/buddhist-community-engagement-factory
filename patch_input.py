with open('main.py', 'r') as f:
    content = f.read()
    
old_block = """                    confirm = input("  Xác nhận đăng bình luận này lên YouTube? (y/N): ").strip().lower()
                    if confirm == "y":"""
                    
new_block = """                    try:
                        confirm = input("  Xác nhận đăng bình luận này lên YouTube? (y/N): ").strip().lower()
                    except EOFError:
                        print("  [!] Chạy trong môi trường nền (Cron). Tự động bỏ qua do không thể xác nhận (Supervised Mode).")
                        confirm = "n"
                    
                    if confirm == "y":"""
                    
content = content.replace(old_block, new_block)
with open('main.py', 'w') as f:
    f.write(content)
