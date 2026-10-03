with open('discovery.py', 'r') as f:
    content = f.read()

old_params = """                params = {
                    "part": "snippet",
                    "q": kw,
                    "maxResults": 3,
                    "type": "video",
                    "key": YOUTUBE_API_KEY
                }"""

new_params = """                params = {
                    "part": "snippet",
                    "q": kw,
                    "maxResults": 10,
                    "order": "viewCount",
                    "type": "video",
                    "key": YOUTUBE_API_KEY
                }"""

content = content.replace(old_params, new_params)
with open('discovery.py', 'w') as f:
    f.write(content)
