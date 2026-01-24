# handlers/youtube_poster.py
import json
import os
from telegram.ext import ContextTypes
from googleapiclient.discovery import build

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

STATUS_FILE = "handlers/last_video.json"  # مسیر فایل JSON

# دریافت آخرین ویدیو
def get_last_video_id():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_video_id", "")
    return ""

# ذخیره آخرین ویدیو
def set_last_video_id(video_id):
    with open(STATUS_FILE, "w") as f:
        json.dump({"last_video_id": video_id}, f)

# تابع چک کردن ویدیو جدید
async def check_new_youtube_video(context: ContextTypes.DEFAULT_TYPE):

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

    # گرفتن آخرین ویدیوی ذخیره شده از فایل
    last_video_id = get_last_video_id()

    if video_id != last_video_id:
        # اگر ویدیو جدید هست → ارسال به تلگرام
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"🎬 ویدیوی جدید منتشر شد!\n\n"
                 f"📌 تیتر: {title}\n\n"
                 f"📝 توضیحات: {description}\n\n"
                 f"🔗 لینک: {url}\n\n"
                 f"@E_Shishehgar"
        )
        # ذخیره آخرین ویدیو در فایل
        set_last_video_id(video_id)
