import os
from telegram import Update
from telegram.ext import ContextTypes

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
HASHTAGS = os.getenv("DEFAULT_HASHTAGS", "")


async def start_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # ریست کامل state
    context.user_data.clear()
    context.user_data["mode"] = "new_post"
    context.user_data["step"] = "type"

    await query.message.reply_text(
        "نوع پست را انتخاب کن:\n"
        "1️⃣ عکس\n"
        "2️⃣ ویدیو\n"
        "3️⃣ لینک"
    )


async def handle_post_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # امنیت: فقط وقتی در مود new_post هست
    if context.user_data.get("mode") != "new_post":
        return

    step = context.user_data.get("step")

    # مرحله انتخاب نوع
    if step == "type":
        choice = update.message.text

        if choice not in ["1", "2", "3"]:
            await update.message.reply_text("فقط 1 یا 2 یا 3 بفرست")
            return

        context.user_data["type"] = choice
        context.user_data["step"] = "media"
        await update.message.reply_text("فایل یا لینک را ارسال کن")

    # مرحله دریافت مدیا
    elif step == "media":
        context.user_data["media"] = update.message
        context.user_data["step"] = "text"
        await update.message.reply_text("متن پست را بفرست")

    # مرحله نهایی
    elif step == "text":
        final_text = update.message.text + "\n\n" + HASHTAGS
        media = context.user_data["media"]
        post_type = context.user_data["type"]

        if post_type == "1":
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=media.photo[-1].file_id,
                caption=final_text
            )

        elif post_type == "2":
            await context.bot.send_video(
                chat_id=CHANNEL_ID,
                video=media.video.file_id,
                caption=final_text
            )

        elif post_type == "3":
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=final_text + "\n\n" + media.text
            )

        # پاکسازی کامل state
        context.user_data.clear()

        await update.message.reply_text("ارسال شد ✅")
