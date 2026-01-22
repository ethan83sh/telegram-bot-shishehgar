import os
from telegram import Update
from telegram.ext import ContextTypes

user_states = {}

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
HASHTAGS = os.getenv("DEFAULT_HASHTAGS")

async def start_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_states[update.effective_user.id] = {"step": "type"}
    await update.callback_query.message.reply_text(
        "نوع پست:\n1- عکس\n2- ویدیو\n3- لینک"
    )

async def handle_post_flow(update: Update, context):
    uid = update.effective_user.id
    state = user_states.get(uid)
    if not state: return

    if state["step"] == "type":
        state["type"] = update.message.text
        state["step"] = "media"
        await update.message.reply_text("فایل یا لینک را ارسال کن")

    elif state["step"] == "media":
        state["media"] = update.message
        state["step"] = "text"
        await update.message.reply_text("متن پست را بفرست")

    elif state["step"] == "text":
        final_text = update.message.text + HASHTAGS
        media = state["media"]

        if state["type"] == "1":
            await context.bot.send_photo(CHANNEL_ID, media.photo[-1].file_id, caption=final_text)
        elif state["type"] == "2":
            await context.bot.send_video(CHANNEL_ID, media.video.file_id, caption=final_text)
        else:
            await context.bot.send_message(CHANNEL_ID, final_text + "\n\n\n" + media.text)

        user_states.pop(uid)
        await update.message.reply_text("ارسال شد ✅")

from handlers.stats import log_post
log_post()

