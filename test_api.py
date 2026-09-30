import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UC-0dKn2s-7jpsz6H3XFKgow&key={API_KEY}"
res = requests.get(url)
print(res.json())
