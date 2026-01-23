from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes

# Default values
AUTO_INTERVAL = 60  # دقیقه
AUTO_TEXT = "این پیام خودکار است."
AUTO_JOB = None
AUTO_START_TIME = None  # datetime

def auto_menu():
    keyboard = [
        [InlineKeyboardButton("🔍 مشاهده بازه زمانی", callback_data="view_interval")],
        [InlineKeyboardButton("✏️ تغییر بازه زمانی", callback_data="change_interval")],
        [InlineKeyboardButton("🔍 مشاهده متن پیام", callback_data="view_text")],
        [InlineKeyboardButton("✏️ تغییر متن پیام", callback_data="change_text")],
        [InlineKeyboardButton("⏰ ریست زمان اولین پیام", callback_data="reset_start")],
        [InlineKeyboardButton("🛑 استاپ ارسال پیام خودکار", callback_data="stop_auto")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # ست کردن مود برای Router اگر لازم باشه
    context.user_data["mode"] = "auto_post"

    await query.message.reply_text(
        "منوی پست خودکار:",
        reply_markup=auto_menu()
    )
