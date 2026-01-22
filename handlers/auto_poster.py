import os
from telegram import InputFile

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
AUTO_INTERVAL = int(os.getenv("AUTO_INTERVAL"))
AUTO_MESSAGE = os.getenv("AUTO_MESSAGE")
HASHTAGS = os.getenv("DEFAULT_HASHTAGS")
AUTO_IMAGE = os.getenv("AUTO_IMAGE")  # لینک یا path

async def auto_post_job(context):
    final_text = AUTO_MESSAGE + HASHTAGS

    if AUTO_IMAGE:  # اگر عکس تنظیم شده
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=AUTO_IMAGE,
            caption=final_text
        )
    else:  # فقط متن
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=final_text
        )

def start_auto(app):
    app.job_queue.run_repeating(auto_post_job, interval=AUTO_INTERVAL, first=30)
