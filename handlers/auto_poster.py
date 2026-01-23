from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta


def init_auto(context):
    """
    مقادیر پیش‌فرض Auto Poster را در bot_data ایجاد می‌کند
    """
    if "auto_interval" not in context.bot_data:
        context.bot_data["auto_interval"] = 60  # دقیقه
    if "auto_text" not in context.bot_data:
        context.bot_data["auto_text"] = "این پیام خودکار است."
    if "auto_job" not in context.bot_data:
        context.bot_data["auto_job"] = None
    if "auto_start_time" not in context.bot_data:
        context.bot_data["auto_start_time"] = None

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


async def start_auto(update, context):
    query = update.callback_query
    await query.answer()

    # اضافه کردن این خط برای init
    init_auto(context)

    # ست کردن مود برای Router
    context.user_data["mode"] = "auto_post"

    await query.message.reply_text(
        "منوی پست خودکار:",
        reply_markup=auto_menu()
    )

async def auto_post_job(context: ContextTypes.DEFAULT_TYPE):
    text = context.bot_data["auto_text"]
    CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
    await context.bot.send_message(CHANNEL_ID, text)


def schedule_auto_job(context, start_time: datetime):
    init_auto(context)

    interval = context.bot_data["auto_interval"] * 60  # ثانیه
    if start_time:
        context.bot_data["auto_start_time"] = start_time
    else:
        start_time = context.bot_data.get("auto_start_time") or datetime.now()

    now = datetime.now()
    delay = (start_time - now).total_seconds()
    if delay < 0:
        delay = interval - ((now - start_time).total_seconds() % interval)

    # لغو job قبلی
    job = context.bot_data.get("auto_job")
    if job:
        job.schedule_removal()

    # برنامه‌ریزی job تکرارشونده
    job = context.job_queue.run_repeating(
        auto_post_job,
        interval=interval,
        first=delay
    )
    context.bot_data["auto_job"] = job
