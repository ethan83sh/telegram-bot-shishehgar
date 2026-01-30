# handlers/scheduled.py
from telegram import Update
from telegram.ext import ContextTypes
from handlers.live_post import live_posts

async def show_scheduled_lives(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not live_posts:
        await update.callback_query.message.reply_text("❌ لایوی برنامه‌ریزی نشده")
    else:
        msg = ""
        for i, lp in enumerate(live_posts, 1):
            msg += f"{i}. {lp['datetime'].strftime('%Y-%m-%d %H:%M')} - {lp['link']}\n"
        await update.callback_query.message.reply_text(msg)
