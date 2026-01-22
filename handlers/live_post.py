import os
from telegram.ext import ContextTypes, CallbackContext
from telegram import Update
from datetime import datetime
import asyncio

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
DEFAULT_TEXT = "🌟 لایو شروع شد!\n🎯 موضوع: {title}\n📺 لینک مشاهده: {link}"

user_live_states = {}

# مرحله ۱: شروع گرفتن اطلاعات
async def start_live_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_live_states[update.effective_user.id] = {"step": "poster"}
    await update.message.reply_text("لطفاً پوستر لایو را بفرستید (عکس یا لینک)")

# مرحله بعدی: دریافت عکس یا لینک
async def handle_live_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    state = user_live_states.get(uid)
    if not state:
        return

    step = state["step"]

    if step == "poster":
        # ذخیره عکس یا لینک
        if update.message.photo:
            state["poster"] = update.message.photo[-1].file_id
        elif update.message.text.startswith("http"):
            state["poster"] = update.message.text
        else:
            await update.message.reply_text("لطفاً یک عکس یا لینک معتبر ارسال کنید")
            return
        state["step"] = "title"
        await update.message.reply_text("تیتر یا موضوع لایو را وارد کنید")

    elif step == "title":
        state["title"] = update.message.text
        state["step"] = "link"
        await update.message.reply_text("لینک یوتیوب لایو را ارسال کنید")

    elif step == "link":
        state["link"] = update.message.text
        state["step"] = "time"
        await update.message.reply_text("زمان لایو را وارد کنید (فرمت YYYY-MM-DD HH:MM)")

    elif step == "time":
        try:
            dt = datetime.strptime(update.message.text, "%Y-%m-%d %H:%M")
            state["time"] = dt
        except:
            await update.message.reply_text("فرمت اشتباه است. لطفاً دوباره وارد کنید")
            return

        # همه اطلاعات کامل است → زمان‌بندی ارسال
        delay = (dt - datetime.now()).total_seconds()
        if delay < 0:
            await update.message.reply_text("زمان گذشته است! لطفاً زمان آینده وارد کنید")
            return

        # schedule job
        context.job_queue.run_once(send_live_post, delay, data=state)
        await update.message.reply_text(f"پست لایو برای {dt} برنامه‌ریزی شد ✅")
        user_live_states.pop(uid)

# تابع ارسال پست
async def send_live_post(context: CallbackContext):
    data = context.job.data
    text = DEFAULT_TEXT.format(title=data["title"], link=data["link"])
    poster = data["poster"]

    if poster.startswith("http"):  # لینک عکس
        await context.bot.send_photo(CHANNEL_ID, poster, caption=text)
    else:  # فایل_id عکس تلگرام
        await context.bot.send_photo(CHANNEL_ID, poster, caption=text)
