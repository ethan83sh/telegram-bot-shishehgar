# handlers/stats.py
import os
from datetime import datetime, timedelta
from telethon import TelegramClient
from telegram import Update
from telegram.ext import ContextTypes

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

SESSION_NAME = "bot_session"

client = TelegramClient("bot_session", API_ID, API_HASH)

async def channel_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await client.start()

        from datetime import datetime, timedelta, timezone
            since = datetime.now(timezone.utc) - timedelta(hours=24)
        messages = []

        channel = await client.get_entity(CHANNEL_ID)

        async for message in client.iter_messages(channel):
            if message.date >= since and message.text:
                messages.append(f"{message.date.strftime('%Y-%m-%d %H:%M')} | {message.text}")


        if not messages:
            text = "در 24 ساعت گذشته هیچ پستی وجود ندارد."
        else:
            text = "📊 پست‌های 24 ساعت گذشته:\n\n" + "\n\n".join(messages[:20])

        await update.callback_query.message.reply_text(text)

    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ خطا در دریافت پیام‌ها: {e}")
