# handlers/auto_poster.py
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# -----------------------------
# منوی Auto Poster
# -----------------------------
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

# -----------------------------
# مقداردهی اولیه bot_data
# -----------------------------
def init_auto(context):
    if "auto_interval" not in context.bot_data:
        context.bot_data["auto_interval"] = 60  # دقیقه
    if "auto_text" not in context.bot_data:
        context.bot_data["auto_text"] = "این پیام خودکار است."
    if "auto_job" not in context.bot_data:
        context.bot_data["auto_job"] = None
    if "auto_start_time" not in context.bot_data:
        context.bot_data["auto_start_time"] = None

# -----------------------------
# دکمه پست خودکار
# -----------------------------
async def start_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    init_auto(context)
    context.user_data["mode"] = "auto_post"

    # JobQueue اولیه
    start_time = context.bot_data.get("auto_start_time") or datetime.now()
    schedule_auto_job(context, start_time)

    await query.message.reply_text(
        "منوی پست خودکار:",
        reply_markup=auto_menu()
    )


# -----------------------------
# مدیریت کلیک منو
# -----------------------------
async def handle_auto_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    init_auto(context)
    data = query.data

    if data == "view_interval":
        interval = context.bot_data["auto_interval"]
        await query.message.reply_text(f"بازه زمانی فعلی: {interval} دقیقه")
    elif data == "change_interval":
        context.user_data["awaiting_interval"] = True
        await query.message.reply_text("لطفاً بازه زمانی جدید (دقیقه) را ارسال کن")
    elif data == "view_text":
        text = context.bot_data["auto_text"]
        await query.message.reply_text(f"متن فعلی پیام:\n{text}")
    elif data == "change_text":
        context.user_data["awaiting_text"] = True
        await query.message.reply_text("لطفاً متن جدید پیام خودکار را ارسال کن")
    elif data == "reset_start":
        context.user_data["awaiting_reset"] = True
        await query.message.reply_text("لطفاً زمان شروع (مثال: 21:00) را وارد کن")
    elif data == "stop_auto":
        job = context.bot_data.get("auto_job")
        if job:
            job.schedule_removal()
            context.bot_data["auto_job"] = None
        await query.message.reply_text("ارسال پیام خودکار متوقف شد ✅")

# -----------------------------
# دریافت پیام کاربر
# -----------------------------
async def handle_auto_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_auto(context)

    # تغییر بازه
if context.user_data.get("awaiting_interval"):
    minutes = int(update.message.text)
    context.bot_data["auto_interval"] = minutes
    context.user_data.pop("awaiting_interval")
    await update.message.reply_text(f"✅ بازه زمانی تغییر کرد به {minutes} دقیقه")
    start_time = context.bot_data.get("auto_start_time") or datetime.now()
    schedule_auto_job(context, start_time)
    return

# تغییر متن
if context.user_data.get("awaiting_text"):
    text = update.message.text
    context.bot_data["auto_text"] = text
    context.user_data.pop("awaiting_text")
    await update.message.reply_text("✅ متن پیام خودکار تغییر کرد")
    return

# ریست زمان
if context.user_data.get("awaiting_reset"):
    h, m = map(int, update.message.text.split(":"))
    now = datetime.now()
    start_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if start_time < now:
        start_time += timedelta(days=1)
    context.user_data.pop("awaiting_reset")
    schedule_auto_job(context, start_time)
    await update.message.reply_text(f"✅ زمان اولین پیام ریست شد: {start_time.strftime('%Y-%m-%d %H:%M')}")
    return

# -----------------------------
# ارسال واقعی پیام
# -----------------------------
async def auto_post_job(context: ContextTypes.DEFAULT_TYPE):
    text = context.bot_data["auto_text"]
    CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
    await context.bot.send_message(CHANNEL_ID, text)

# -----------------------------
# زمان‌بندی JobQueue
# -----------------------------
def schedule_auto_job(context, start_time: datetime):
    init_auto(context)

    interval = context.bot_data.get("auto_interval", 60) * 60  # دقیقه → ثانیه

    # لغو Job قبلی
    job = context.bot_data.get("auto_job")
    if job:
        job.schedule_removal()

    now = datetime.now()
    delay = (start_time - now).total_seconds()
    if delay < 0:
        # اگر زمان گذشته، اجرای بعدی بر اساس بازه
        delay = interval - ((now - start_time).total_seconds() % interval)

    # Job جدید
    job = context.job_queue.run_repeating(
        auto_post_job,
        interval=interval,
        first=delay
    )

    context.bot_data["auto_job"] = job
    context.bot_data["auto_start_time"] = start_time

