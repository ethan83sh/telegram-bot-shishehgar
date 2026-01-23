import os
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
DEFAULT_TEXT = "🌟 لایو شروع شد!\n\n\n🎯 موضوع: {title}\n\n\n📺 لینک مشاهده:\n {link}\n\n\n@E_Shishehgar"


# مرحله ۱: فعال‌سازی مود لایو
async def start_live_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    context.user_data["mode"] = "live_post"
    context.user_data["step"] = "poster"

    await query.message.reply_text("لطفاً پوستر لایو را بفرست (عکس یا لینک)")


# جریان دریافت داده‌ها
async def handle_live_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") != "live_post":
        return

    step = context.user_data.get("step")

    # مرحله پوستر
    if step == "poster":
        if update.message.photo:
            context.user_data["poster"] = update.message.photo[-1].file_id
        elif update.message.text and update.message.text.startswith("http"):
            context.user_data["poster"] = update.message.text
        else:
            await update.message.reply_text("لطفاً یک عکس یا لینک معتبر ارسال کن")
            return

        context.user_data["step"] = "title"
        await update.message.reply_text("تیتر یا موضوع لایو را وارد کن")

    # مرحله عنوان
    elif step == "title":
        context.user_data["title"] = update.message.text
        context.user_data["step"] = "link"
        await update.message.reply_text("لینک یوتیوب لایو را ارسال کن")

    # مرحله لینک
    elif step == "link":
        context.user_data["link"] = update.message.text
        context.user_data["step"] = "time"
        await update.message.reply_text("زمان لایو را وارد کن (YYYY-MM-DD HH:MM)")

    # مرحله زمان
    elif step == "time":
        try:
            dt = datetime.strptime(update.message.text, "%Y-%m-%d %H:%M")
        except:
            await update.message.reply_text("فرمت اشتباه است. مثال درست:\n2026-01-23 21:30")
            return

        delay = (dt - datetime.now()).total_seconds()
        if delay <= 0:
            await update.message.reply_text("زمان باید در آینده باشد")
            return

        # زمان‌بندی ارسال
        context.job_queue.run_once(
            send_live_post,
            delay,
            data=context.user_data.copy()
        )

        context.user_data.clear()
        await update.message.reply_text(f"پست لایو برای {dt} برنامه‌ریزی شد ✅")


# تابع ارسال نهایی
async def send_live_post(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data

    text = DEFAULT_TEXT.format(
        title=data["title"],
        link=data["link"]
    )

    poster = data["poster"]

    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=poster,
        caption=text
    )
