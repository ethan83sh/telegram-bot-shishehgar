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
SESSION_FILE = "bot_session.session"       # مسیر فایل session ساخته شده

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# ================= FUNCTION =================
async def channel_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await client.start()

        since = datetime.now(timezone.utc) - timedelta(hours=24)

        # شمارش‌ها
        stats = {
            "متنی": 0,
            "عکس": 0,
            "ویدیو": 0,
            "لینک": 0
        }
        total_count = 0

        channel = await client.get_entity(CHANNEL_ID)

        async for message in client.iter_messages(channel):
            if message.date >= since:
                total_count += 1
                # پست عکس
                if message.photo:
                    stats["عکس"] += 1
                # پست ویدیو
                if message.video:
                    stats["ویدیو"] += 1
                # متن و لینک
                if message.text:
                    if message.text.startswith("http://") or message.text.startswith("https://"):
                        stats["لینک"] += 1
                    else:
                        stats["متنی"] += 1

        # آماده کردن متن جدول‌وار با ایموجی
        text = (
            f"📊 آمار ۲۴ ساعت گذشته کانال:\n\n"
            f"📝 پست متنی: {stats['متنی']}\n"
            f"🖼️ پست عکس: {stats['عکس']}\n"
            f"🎬 پست ویدیو: {stats['ویدیو']}\n"
            f"🔗 پست لینک: {stats['لینک']}\n"
            f"📌 تعداد کل پست‌ها: {total_count}"
        )

        await update.callback_query.message.reply_text(text)

    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ خطا در دریافت پیام‌ها: {e}")
