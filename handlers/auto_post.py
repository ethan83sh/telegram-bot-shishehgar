# handlers/auto_post.py
from telegram import Update
from telegram.ext import ContextTypes

async def start_auto_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "🤖 بخش پست خودکار (در حال ساخت)"
    )

async def handle_auto_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
