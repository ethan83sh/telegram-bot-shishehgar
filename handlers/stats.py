# handlers/stats.py
import os
from datetime import datetime, timedelta
from telethon import TelegramClient
from telegram import Update
from telegram.ext import ContextTypes

# ================= CONFIG TELETHON =================
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # نام کاربری کانال یا -100xxxxxxxxx

# ================= TELETHON CLIENT =================
# استفاده از Bot Token، بدون نیاز به شماره و input
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ================= FUNCTION =================
async def channel_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    since = datetime.now() - timedelta(hours=24)
    messages = []

    try:
        # گرفتن entity کانال
        channel = await client.get_entity(CHANNEL_USERNAME)

        # خواندن پیام‌ها به ترتیب ارسال
        async for message in client.iter_messages(channel, reverse=True):
            if message.date >= since and message.text:
                messages.append(f"{message.date.strftime('%Y-%m-%d %H:%M')} | {message.text}")

        # بررسی تعداد پیام‌ها
        if not messages:
            reply_text = "در 24 ساعت گذشته هیچ پستی در کانال وجود ندارد."
        else:
            # جمع‌بندی و محدود کردن طول پیام (اختیاری)
            if len(messages) > 20:
                messages = messages[:20]  # فقط ۲۰ پیام آخر
                messages.append("... پیام‌های بیشتر موجود است ...")
            reply_text = "📊 پست‌های 24 ساعت گذشته:\n\n" + "\n\n".join(messages)

        # ارسال به کاربر
        await update.callback_query.message.reply_text(reply_text)

    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ خطا در دریافت پیام‌ها: {e}")
