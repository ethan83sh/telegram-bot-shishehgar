from datetime import datetime, timedelta
from telegram.ext import ContextTypes

import storage
import youtube_rss
from config import (
    CHANNEL_ID,
    DEFAULT_AUTO_TEXT,
    DEFAULT_AUTO_INTERVAL_MIN,
    YOUTUBE_CHANELL_ID,
)

AUTO_JOB_NAME = "auto_post_job"
YTRSS_JOB_NAME = "youtube_rss_job"

def live_job_name(live_id: str) -> str:
    return f"live:{live_id}"

def _live_text(title: str, desc: str, link: str) -> str:
    return (
        "🌟 لایو شروع شد!\n\n"
        f"🎯 موضوع: {title}\n\n"
        f"{desc}\n\n"
        "📺 لینک مشاهده:\n"
        f"{link}\n\n"
        "@IRan_Tajdar"
    ).strip()

async def auto_post_job(context: ContextTypes.DEFAULT_TYPE):
    text = storage.get_str("auto_text", DEFAULT_AUTO_TEXT)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)

async def auto_send_reset_now(context: ContextTypes.DEFAULT_TYPE):
    # ارسال فوری
    await auto_post_job(context)

    jq = context.application.job_queue
    for j in jq.get_jobs_by_name(AUTO_JOB_NAME):
        j.schedule_removal()

    interval_min = storage.get_int("auto_interval_minutes", DEFAULT_AUTO_INTERVAL_MIN)
    jq.run_repeating(
        auto_post_job,
        interval=interval_min * 60,
        first=interval_min * 60,
        name=AUTO_JOB_NAME,
    )
    storage.set_bool("auto_enabled", True)
    storage.set_str("auto_next_run_at_utc", (datetime.utcnow() + timedelta(minutes=interval_min)).isoformat())

async def auto_stop(context: ContextTypes.DEFAULT_TYPE):
    jq = context.application.job_queue
    for j in jq.get_jobs_by_name(AUTO_JOB_NAME):
        j.schedule_removal()
    storage.set_bool("auto_enabled", False)

async def youtube_rss_job(context: ContextTypes.DEFAULT_TYPE):
    if not YOUTUBE_CHANELL_ID:
        return

    feed_url = youtube_rss.channel_feed_url(YOUTUBE_CHANELL_ID)
    entries = youtube_rss.parse_entries(feed_url)

    sent = storage.get_list("yt_last_ids", [])
    sent_set = set(sent)

    for vid, title, link in entries[:10]:
        if vid in sent_set:
            continue
        msg = f"🎬 ویدیوی جدید:\n{title}\n{link}".strip()
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
        sent.insert(0, vid)
        sent_set.add(vid)

    storage.set_list("yt_last_ids", sent[:200])

# ---- Live scheduling ----
async def live_send_job(context: ContextTypes.DEFAULT_TYPE):
    e = context.job.data  # event dict
    poster_id = e["poster_file_id"]
    text = _live_text(e["title"], e["desc"], e["link"])
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=poster_id, caption=text)

def load_live_events():
    return storage.get_json("live_events", [])

def save_live_events(events):
    storage.set_json("live_events", events)
