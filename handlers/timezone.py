# handlers/timezone.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import pytz

# دیفالت تایم‌زون
DEFAULT_TZ = "Europe/Berlin"

# ذخیره در حافظه (بعداً می‌بریم روی فایل)
tz_settings = {
    "timezone": DEFAULT_TZ
}

# ---------- منوی تایم‌زون ----------
def timezone_menu():
    keyboard = [
        [InlineKeyboardButton("🕒 مشاهده زمان سرور", callback_data="tz_view")],
        [InlineKeyboardButton("🌍 تغییر تایم‌زون", callback_data="tz_change")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------- شروع ----------
async def start_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "⏰ مدیریت تایم‌زون:",
        reply_markup=timezone_menu()
    )

# ---------- هندلر ----------
async def handle_timezone_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # مشاهده زمان
    if data == "tz_view":
        tz_name = tz_settings["timezone"]
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        await query.message.reply_text(f"🕒 زمان فعلی سرور:\n{now}\n({tz_name})")

    # تغییر تایم‌زون
    elif data == "tz_change":
        context.user_data["mode"] = "set_timezone"
        await query.message.reply_text(
            "نام تایم‌زون را وارد کن (مثال: Europe/Berlin یا Asia/Tehran):"
        )

    # دریافت ورودی
    elif context.user_data.get("mode") == "set_timezone":
        tz_name = update.message.text.strip()
        try:
            pytz.timezone(tz_name)
            tz_settings["timezone"] = tz_name
            context.user_data["mode"] = None
            await update.message.reply_text(f"✅ تایم‌زون تنظیم شد روی: {tz_name}")
        except:
            await update.message.reply_text("❌ تایم‌زون نامعتبر است")
