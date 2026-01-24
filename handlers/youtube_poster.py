# handlers/youtube_poster.py
import os
from telegram.ext import ContextTypes
from telegram import Update
from googleapiclient.discovery import build

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

# آخرین ویدیو ذخیره شده
last_video_id = None

# تابع چک کردن ویدیو جدید
async def check_new_youtube_video(context: ContextTypes.DEFAULT_TYPE):
    global last_video_id

    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    # گرفتن آخرین ویدیو از کانال
    request = youtube.search().list(
        part="snippet",
        channelId=YOUTUBE_CHANNEL_ID,
        order="date",
        maxResults=1,
        type="video"
    )
    response = request.execute()

    items = response.get("items", [])
    if not items:
        return

    video = items[0]
    video_id = video["id"]["videoId"]
    title = video["snippet"]["title"]
    description = video["snippet"]["description"]
    url = f"https://www.youtube.com/watch?v={video_id}"

    if last_video_id != video_id:
        # اگر ویدیو جدید هست → ارسال به تلگرام
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"🎬 ویدیوی جدید منتشر شد!\n\n"
                 f"📌 تیتر: {title}\n\n"
                 f"📝 توضیحات: {description}\n\n"
                 f"🔗 لینک: {url}\n\n"
                 f"@E_Shishehgar"
        )
        last_video_id = video_id
