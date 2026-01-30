# handlers/manual_post.py
from telegram import Update
from telegram.ext import ContextTypes

async def start_manual_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "📌 بخش ارسال پست معمولی (در حال ساخت)"
    )

async def handle_manual_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

