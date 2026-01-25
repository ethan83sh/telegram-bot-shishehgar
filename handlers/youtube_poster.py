# handlers/youtube_poster.py
import feedparser
import json
import os

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
STATUS_FILE = "handlers/last_video.json"


def get_last_video_id():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_video_id", "")
    return ""


def set_last_video_id(video_id):
    with open(STATUS_FILE, "w") as f:
        json.dump({"last_video_id": video_id}, f)


async def check_new_youtube_video(context):
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        return

    entry = feed.entries[0]

    video_id = entry.yt_videoid
    title = entry.title
    url = entry.link

    last_video_id = get_last_video_id()

    if video_id != last_video_id:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"""🎬 ویدیوی جدید منتشر شد!

📌 تیتر: {title}

🔗 لینک:
{url}

@E_Shishehgar"""
        )

        set_last_video_id(video_id)
