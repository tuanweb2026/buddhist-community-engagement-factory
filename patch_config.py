import re
with open('app_config.py', 'r') as f:
    content = f.read()

# Add new keywords
if '"nhạc thiền tĩnh tâm",' not in content:
    content = content.replace('"thuyết pháp Thích Pháp Hòa",', '"thuyết pháp Thích Pháp Hòa",\n    "nhạc thiền tĩnh tâm",\n    "nhạc thiền Phật giáo",')

# Add min thresholds
if 'MIN_VIEWS_THRESHOLD' not in content:
    content += '\n# Custom Filter\nMIN_VIEWS_THRESHOLD = int(os.getenv("MIN_VIEWS", 500000))\nMIN_SUBS_THRESHOLD = int(os.getenv("MIN_SUBS", 100000))\n'

with open('app_config.py', 'w') as f:
    f.write(content)
