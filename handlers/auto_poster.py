import os

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
AUTO_INTERVAL = int(os.getenv("AUTO_INTERVAL"))
AUTO_MESSAGE = os.getenv("AUTO_MESSAGE")
HASHTAGS = os.getenv("DEFAULT_HASHTAGS")

async def auto_post_job(context):
    await context.bot.send_message(
        CHANNEL_ID,
        AUTO_MESSAGE + HASHTAGS
    )

def start_auto(app):
    app.job_queue.run_repeating(auto_post_job, interval=AUTO_INTERVAL, first=30)
