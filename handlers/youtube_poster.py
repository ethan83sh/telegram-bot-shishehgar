# handlers/youtube_poster.py
import json
import os
from telegram.ext import ContextTypes
from googleapiclient.discovery import build

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

STATUS_FILE = "handlers/last_video.json"

def get_last_video_id():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f).get("last_video_id", "")
    return ""

def set_last_video_id(video_id):
    with open(STATUS_FILE, "w") as f:
        json.dump({"last_video_id": video_id}, f)

async def check_new_youtube_video(context: ContextTypes.DEFAULT_TYPE):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # فقط پلی‌لیست آپلودهای کانال
        channel = youtube.channels().list(
            part="contentDetails",
            id=YOUTUBE_CHANNEL_ID
        ).execute()

        uploads_playlist = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        videos = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist,
            maxResults=1
        ).execute()

        video = videos["items"][0]
        video_id = video["snippet"]["resourceId"]["videoId"]
        title = video["snippet"]["title"]
        description = video["snippet"]["description"]
        url = f"https://www.youtube.com/watch?v={video_id}"

        last_video_id = get_last_video_id()

        if video_id != last_video_id:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"🎬 ویدیوی جدید منتشر شد!\n\n"
                     f"📌 {title}\n\n"
                     f"{description}\n\n"
                     f"🔗 {url}"
            )
            set_last_video_id(video_id)

    except Exception as e:
        print("YouTube error:", e)
