# handlers/youtube_poster.py
from telegram import Bot
import feedparser
import os

CHANNEL_ID = os.getenv("CHANNEL_ID")  # کانال تلگرام
BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUTUBE_FEED = "https://www.youtube.com/feeds/videos.xml?channel_id=YOUR_CHANNEL_ID"

async def check_new_youtube_video(context):
    bot = context.bot
    feed = feedparser.parse(YOUTUBE_FEED)
    if feed.entries:
        video = feed.entries[0]
        title = video.title
        link = video.link
        await bot.send_message(chat_id=CHANNEL_ID, text=f"🎬 ویدیوی جدید:\n{title}\n{link}")
