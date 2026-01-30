# handlers/youtube_poster.py
import os
import json
import feedparser
from telegram.ext import ContextTypes
from telegram import Update
from handlers.signature import get_signature

# ================= CONFIG =================
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
YOUTUBE_RSS = f"https://www.youtube.com/feeds/videos.xml?channel_id={os.getenv('YOUTUBE_CHANNEL_ID')}"
STATUS_FILE = "storage/last_video.json"

# ---------- دریافت آخرین ویدیو ذخیره شده ----------
def get_last_video_id():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("last_video_id", "")
    return ""

# ---------- ذخیره آخرین ویدیو ----------
def set_last_video_id(video_id):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_video_id": video_id}, f, ensure_ascii=False, indent=2)

# ---------- چک کردن و ارسال ویدیوی جدید ----------
async def check_new_youtube_video(context: ContextTypes.DEFAULT_TYPE):
    last_video_id = get_last_video_id()
    feed = feedparser.parse(YOUTUBE_RSS)
    entries = feed.entries
    if not entries:
        return

    # آخرین ویدیو
    video = entries[0]
    video_id = video.yt_videoid
    title = video.title
    link = video.link
    description = getattr(video, "summary", "")

    if video_id != last_video_id:
        # متن نهایی با امضا
        text = f"🎬 ویدیوی جدید منتشر شد!\n\n📌 تیتر: {title}\n\n📝 توضیحات: {description}\n\n🔗 لینک: {link}\n\n{get_signature()}"
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
        set_last_video_id(video_id)
