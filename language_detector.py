"""
Language Detector Module:
Xác định chuẩn xác cộng đồng ngôn ngữ:
- Vietnamese community -> 'vi'
- Foreign community -> 'en'
- Nếu không chắc chắn với confidence cao -> 'LANGUAGE_UNCERTAIN'
"""

import re
from typing import Optional, List
from langdetect import detect_langs, DetectorFactory

# Đảm bảo kết quả xác định ngôn ngữ có tính nhất quán
DetectorFactory.seed = 0

def detect_community_language(
    title: str,
    description: str = "",
    channel_name: str = "",
    comments_sample: List[str] = None
) -> str:
    """
    Phân tích tổng hợp: title, description, tên kênh và sample comments
    Trả về 'vi', 'en', hoặc 'LANGUAGE_UNCERTAIN'
    """
    text_corpus = f"{title} {channel_name} {description[:300]}"
    if comments_sample:
        text_corpus += " " + " ".join(comments_sample[:5])
    
    clean_text = text_corpus.strip()
    if len(clean_text) < 5:
        return "LANGUAGE_UNCERTAIN"

    # 1. Kiểm tra dấu tiếng Việt đặc trưng
    vietnamese_pattern = re.compile(
        r'[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]',
        re.IGNORECASE
    )
    vn_chars = vietnamese_pattern.findall(clean_text)
    if len(vn_chars) >= 3:
        return "vi"

    # 2. Dùng langdetect cho văn bản dài
    try:
        langs = detect_langs(clean_text)
        for l in langs:
            if l.lang == 'vi' and l.prob > 0.70:
                return "vi"
            if l.lang == 'en' and l.prob > 0.70:
                return "en"
    except Exception:
        pass

    # 3. Heuristic kiểm tra từ khóa tiếng Anh phổ biến
    clean_lower = clean_text.lower()
    en_buddhist_words = ["buddha", "dharma", "dhamma", "meditation", "mindfulness", "compassion", "suffering", "peace", "teachings"]
    matches = sum(1 for w in en_buddhist_words if w in clean_lower)
    if matches >= 2 and len(vn_chars) == 0:
        return "en"

    return "LANGUAGE_UNCERTAIN"

def detect_language(title: str, description: str = "") -> tuple:
    lang = detect_community_language(title, description)
    return lang, 1.0

