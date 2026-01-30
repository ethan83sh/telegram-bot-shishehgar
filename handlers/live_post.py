# handlers/live_post.py
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import pytz

from handlers.timezone import tz_settings

# ---------- شروع لایو ----------
async def start_live_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "live_time"
    await update.callback_query.message.reply_text(
        "⏰ ساعت شروع لایو را وارد کن (فرمت: HH:MM مثال: 21:30)"
    )

# ---------- فلو ----------
async def handle_live_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")

    # مرحله 1: ساعت
    if mode == "live_time":
        try:
            time_str = update.message.text.strip()
            hour, minute = map(int, time_str.split(":"))

            tz = pytz.timezone(tz_settings["timezone"])
            now = datetime.now(tz)

            live_datetime = now.replace(hour=hour, minute=minute, second=0)

            if live_datetime < now:
                live_datetime += timedelta(days=1)

            context.user_data["live_datetime"] = live_datetime
            context.user_data["mode"] = "live_title"

            await update.message.reply_text(
                "📌 تیتر لایو را بفرست:"
            )

        except:
            await update.message.reply_text("❌ فرمت ساعت اشتباه است")

    # مرحله 2: تیتر
    elif mode == "live_title":
        context.user_data["live_title"] = update.message.text
        context.user_data["mode"] = "live_link"

        await update.message.reply_text(
            "🔗 لینک لایو یوتوب را بفرست:"
        )

    # مرحله 3: لینک
    elif mode == "live_link":
        title = context.user_data["live_title"]
        link = update.message.text
        live_time = context.user_data["live_datetime"]

        final_text = (
            "🎬 ویدیوی جدید منتشر شد!\n\n"
            f"📌 تیتر: {title}\n\n"
            "🔗 لینک:\n"
            f"{link}\n\n"
            "@Iran_Tajdar"
        )

        await context.bot.send_message(
            chat_id=context.bot_data["CHANNEL_ID"],
            text=final_text
        )

        context.user_data.clear()
        await update.message.reply_text("✅ پست لایو ارسال شد")
