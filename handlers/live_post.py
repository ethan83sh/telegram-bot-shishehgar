# handlers/live_post.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import pytz

live_posts = []

async def start_live_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📌 اضافه کردن لایو جدید", callback_data="add_live")],
        [InlineKeyboardButton("📝 مشاهده لایوهای آینده", callback_data="view_live")],
    ]
    await update.callback_query.message.reply_text(
        "🎬 مدیریت پست لایو:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_live_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        data = query.data
        if data == "add_live":
            context.user_data["mode"] = "set_live"
            await query.message.reply_text("لطفاً لینک و متن لایو را ارسال کن:")
        elif data == "view_live":
            if not live_posts:
                await query.message.reply_text("❌ لایوی برنامه‌ریزی نشده")
            else:
                msg = ""
                for i, lp in enumerate(live_posts, 1):
                    msg += f"{i}. {lp['datetime'].strftime('%Y-%m-%d %H:%M')} - {lp['link']}\n"
                await query.message.reply_text(msg)
    elif context.user_data.get("mode") == "set_live" and update.message:
        parts = update.message.text.split("\n")
        if len(parts) >= 2:
            live_posts.append({
                "link": parts[0],
                "text": parts[1],
                "datetime": datetime.now(pytz.timezone("Europe/Berlin"))
            })
            context.user_data["mode"] = None
            await update.message.reply_text("✅ لایو با موفقیت اضافه شد")
