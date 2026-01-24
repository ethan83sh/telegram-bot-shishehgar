# handlers/stats.py
import os
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telegram import Update
from telegram.ext import ContextTypes

# ================= CONFIG TELETHON =================
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # عدد ID کانال

client = TelegramClient('bot_session', API_ID, API_HASH)

# ================= FUNCTION =================
async def channel_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await client.start()

        since = datetime.now(timezone.utc) - timedelta(hours=24)

        # شمارش‌ها
        text_count = 0
        photo_count = 0
        video_count = 0
        link_count = 0
        total_count = 0

        channel = await client.get_entity(CHANNEL_ID)

        async for message in client.iter_messages(channel):
            if message.date >= since:
                total_count += 1
                if message.text:
                    # اگر متن فقط لینک باشد
                    if message.text.startswith("http://") or message.text.startswith("https://"):
                        link_count += 1
                    else:
                        text_count += 1
                if message.photo:
                    photo_count += 1
                if message.video:
                    video_count += 1

        # پاسخ
        text = (
            f"📊 آمار ۲۴ ساعت گذشته کانال:\n\n"
            f"تعداد کل پست‌ها: {total_count}\n"
            f"پست متنی: {text_count}\n"
            f"پست عکس: {photo_count}\n"
            f"پست ویدیو: {video_count}\n"
            f"پست لینک: {link_count}"
        )

        await update.callback_query.message.reply_text(text)

    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ خطا در دریافت پیام‌ها: {e}")
