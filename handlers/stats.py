# handlers/stats.py
import os
from datetime import datetime, timedelta
from telethon import TelegramClient
from telegram import Update
from telegram.ext import ContextTypes

# ================= CONFIG TELETHON =================
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # نام کاربری کانال یا ID

# session_name می‌تواند هر چیزی باشد، برای example 'bot_session'
client = TelegramClient('bot_session', API_ID, API_HASH)

# ================= FUNCTION =================
async def channel_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await client.start()
    since = datetime.now() - timedelta(hours=24)
    messages = []

    try:
        channel = await client.get_entity(CHANNEL_USERNAME)

        async for message in client.iter_messages(channel, reverse=True):
            if message.date >= since:
                # اگر پیام متن دارد
                if message.text:
                    messages.append(f"{message.date.strftime('%Y-%m-%d %H:%M')} | {message.text}")

        if not messages:
            reply_text = "در 24 ساعت گذشته هیچ پستی در کانال وجود ندارد."
        else:
            # جمع‌بندی پیام‌ها
            reply_text = "📊 پست‌های 24 ساعت گذشته:\n\n" + "\n\n".join(messages)

        await update.callback_query.message.reply_text(reply_text)

    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ خطا در دریافت پیام‌ها: {e}")
