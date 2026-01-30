# handlers/timezone.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import pytz
from datetime import datetime

TIMEZONE = "Europe/Berlin"

async def start_timezone_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 مشاهده زمان سرور", callback_data="view_tz")],
        [InlineKeyboardButton("✏️ تغییر زمان سرور", callback_data="change_tz")],
    ]
    await update.callback_query.message.reply_text(
        "⏱ مدیریت تایم‌زون:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_timezone_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    global TIMEZONE
    if query:
        data = query.data
        if data == "view_tz":
            tz = pytz.timezone(TIMEZONE)
            now = datetime.now(tz)
            await query.message.reply_text(f"⏰ زمان سرور فعلی: {now.strftime('%Y-%m-%d %H:%M')}")
        elif data == "change_tz":
            context.user_data["mode"] = "set_tz"
            await query.message.reply_text("نام منطقه زمانی جدید را وارد کن:")
    elif context.user_data.get("mode") == "set_tz" and update.message:
        try:
            pytz.timezone(update.message.text)
            TIMEZONE = update.message.text
            context.user_data["mode"] = None
            await update.message.reply_text(f"✅ تایم‌زون جدید ثبت شد: {TIMEZONE}")
        except:
            await update.message.reply_text("❌ نام تایم‌زون اشتباه است")
