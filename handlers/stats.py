# handlers/stats.py
import os
from datetime import datetime, timedelta
from telethon import TelegramClient
from telegram import Update
from telegram.ext import ContextTypes

# ================= CONFIG =================
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # مثال: -1001234567890

# نام session
SESSION_NAME = "bot_session"

# ================= TELETHON CLIENT =================
# فقط load session موجود، نیازی به input نیست
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# ================= FUNCTION =================
async def channel_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = []
    since = datetime.now() - timedelta(hours=24)

    try:
        await client.start()  # از session موجود استفاده می‌کند

        # گرفتن entity کانال
        channel = await client.get_entity(CHANNEL_ID)

        # خواندن پیام‌های 24 ساعت گذشته
        async for message in client.iter_messages(channel, reverse=True):
            if message.date >= since and message.text:
                messages.append(f"{message.date.strftime('%Y-%m-%d %H:%M')} | {message.text}")

        # آماده‌سازی پیام پاسخ
        if not messages:
            reply_text = "در 24 ساعت گذشته هیچ پستی در کانال وجود ندارد."
        else:
            if len(messages) > 20:
                messages = messages[:20]
                messages.append("... پیام‌های بیشتر موجود است ...")
            reply_text = "📊 پست‌های 24 ساعت گذشته:\n\n" + "\n\n".join(messages)

        # ارسال به کاربر
        await update.callback_query.message.reply_text(reply_text)

    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ خطا در دریافت پیام‌ها: {e}")
