# main.py
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

import storage
import youtube_rss

# ---------- ENV ----------
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
YOUTUBE_CHANELL_ID = os.getenv("YOUTUBE_CHANELL_ID", "")  # (همان اسم خودت)
# YOUTUBE_API_KEY فعلاً لازم نیست چون RSS استفاده می‌کنیم
# ------------------------

# ---------- Defaults ----------
DEFAULT_TZ = "Europe/Berlin"
DEFAULT_AUTO_INTERVAL_MIN = 13 * 60

DEFAULT_AUTO_TEXT = """با درود به همراهان گرامی،
اگر به تحلیل‌های خبری، بررسی‌های سیاسی‌اجتماعی، و آشنایی با قانون اساسی علاقه‌مندید، دعوت می‌کنم روزانه مهمان برنامه‌های من باشید:
برای مشاهده تمام راه های ارتباطی با من روی لینک زیر کلیک نمایید
[https://linktr.ee/Shishehgar](https://linktr.ee/Shishehgar)
با تشکر
احسان شیشه گر


#شاهزاده_رضا_پهلوی
#انقلاب_شیروخورشید
#ایرانو_پس_میگیریم
#همکاری_ملی
#MIGA
#KingRezaPahlavi

───────────────── 
 ℘ @OfficialRezaPahlavi ℘ 
───────────────── 
 ℘ IranoPasMigirim.com ℘ 
───────────────── 
instagram.com/officialrezapahlavi 
───────────────── 
 
@Iran_Tajdar"""
# -----------------------------

# ---------- Conversation states ----------
P_PHOTO_FILE, P_PHOTO_TEXT = range(2)
P_VIDEO_FILE, P_VIDEO_TEXT = range(2)
P_LINK_VALUE, P_LINK_TEXT = range(2)

L_POSTER, L_TITLE, L_DESC, L_LINK, L_TIME = range(5)
# ---------------------------------------

def is_admin(update: Update) -> bool:
    return bool(update.effective_user and update.effective_user.id == ADMIN_ID)

async def deny_if_not_admin(update: Update) -> bool:
    if not is_admin(update):
        if update.message:
            await update.message.reply_text("⛔️ دسترسی ندارید.")
        return True
    return False

def get_tz() -> ZoneInfo:
    tz_name = storage.get_str("timezone", DEFAULT_TZ)
    try:
        return ZoneInfo(tz_name)
    except Exception:
        storage.set_str("timezone", DEFAULT_TZ)
        return ZoneInfo(DEFAULT_TZ)

def ensure_defaults() -> None:
    if storage.get_str("timezone", "") == "":
        storage.set_str("timezone", DEFAULT_TZ)
    if storage.get_str("signature_text", "") == "":
        storage.set_str("signature_text", "@Iran_Tajdar")
    if storage.get_int("auto_interval_minutes", 0) <= 0:
        storage.set_int("auto_interval_minutes", DEFAULT_AUTO_INTERVAL_MIN)
    if storage.get_str("auto_text", "") == "":
        storage.set_str("auto_text", DEFAULT_AUTO_TEXT)
    if storage.get_json("yt_last_ids", None) is None:
        storage.set_list("yt_last_ids", [])
    if storage.get_bool("auto_enabled", False) not in (True, False):
        storage.set_bool("auto_enabled", False)

def build_caption(text: str) -> str:
    sig = storage.get_str("signature_text", "@Iran_Tajdar")
    text = (text or "").strip()
    return f"{text}\n\n{sig}".strip()

# ---------------- Basic commands ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    ensure_defaults()
    await update.message.reply_text("✅ ربات آماده است. دستورها: /post_text /post_photo /post_video /post_link /live_post /auto_send_reset /auto_stop /tz_show /tz_set")

async def post_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    if not context.args:
        await update.message.reply_text("متن را بعد از دستور بفرست: /post_text ...")
        return
    text = " ".join(context.args)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=build_caption(text), parse_mode=ParseMode.HTML)
    await update.message.reply_text("پست متنی با موفقیت ارسال شد ✅")

# ---------------- Photo flow ----------------
async def post_photo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    await update.message.reply_text("عکس را ارسال کن (بدون کپشن).")
    return P_PHOTO_FILE

async def post_photo_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        await update.message.reply_text("لطفاً فقط عکس بفرست.")
        return P_PHOTO_FILE
    context.user_data["photo_file_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("✅ عکس دریافت شد. حالا متن پست را بفرست.")
    return P_PHOTO_TEXT

async def post_photo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    file_id = context.user_data.get("photo_file_id")
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=file_id, caption=build_caption(text))
    await update.message.reply_text("پست عکس با موفقیت به کانال ارسال شد ✅")
    return ConversationHandler.END

# ---------------- Video flow ----------------
async def post_video_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    await update.message.reply_text("ویدیو را ارسال کن (بدون کپشن).")
    return P_VIDEO_FILE

async def post_video_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.video:
        await update.message.reply_text("لطفاً فقط ویدیو بفرست.")
        return P_VIDEO_FILE
    context.user_data["video_file_id"] = update.message.video.file_id
    await update.message.reply_text("✅ ویدیو دریافت شد. حالا متن پست را بفرست.")
    return P_VIDEO_TEXT

async def post_video_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    file_id = context.user_data.get("video_file_id")
    await context.bot.send_video(chat_id=CHANNEL_ID, video=file_id, caption=build_caption(text))
    await update.message.reply_text("پست ویدیو با موفقیت به کانال ارسال شد ✅")
    return ConversationHandler.END

# ---------------- Link flow ----------------
async def post_link_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    await update.message.reply_text("لینک را ارسال کن.")
    return P_LINK_VALUE

async def post_link_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = (update.message.text or "").strip()
    if not link.startswith("http"):
        await update.message.reply_text("لینک معتبر بفرست (با http یا https).")
        return P_LINK_VALUE
    context.user_data["link_value"] = link
    await update.message.reply_text("✅ لینک دریافت شد. حالا متن پست را بفرست.")
    return P_LINK_TEXT

async def post_link_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    link = context.user_data.get("link_value", "")
    final = build_caption(f"{text}\n\n{link}".strip())
    await context.bot.send_message(chat_id=CHANNEL_ID, text=final)
    await update.message.reply_text("پست لینک با موفقیت به کانال ارسال شد ✅")
    return ConversationHandler.END

# ---------------- Signature ----------------
async def signature_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    sig = storage.get_str("signature_text", "@Iran_Tajdar")
    await update.message.reply_text(f"امضای فعلی:\n{sig}\n\n✅")

async def signature_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    text = update.message.text.replace("/signature_set", "", 1).strip()
    if not text:
        await update.message.reply_text("متن امضا را بعد از دستور بفرست: /signature_set ...")
        return
    storage.set_str("signature_text", text)
    await update.message.reply_text("✅ امضا با موفقیت ذخیره شد.")

# ---------------- Timezone ----------------
async def tz_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    tz_name = storage.get_str("timezone", DEFAULT_TZ)
    now_utc = datetime.utcnow()
    now_local = datetime.now(get_tz())
    await update.message.reply_text(f"TZ فعلی: {tz_name}\nUTC: {now_utc:%Y-%m-%d %H:%M}\nLocal: {now_local:%Y-%m-%d %H:%M}\n✅")

async def tz_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    if not context.args:
        await update.message.reply_text("مثال: /tz_set Europe/Berlin")
        return
    tz_name = context.args[0].strip()
    try:
        ZoneInfo(tz_name)
    except Exception:
        await update.message.reply_text("⛔️ تایم‌زون نامعتبر است. مثال: Europe/Berlin")
        return
    storage.set_str("timezone", tz_name)
    await update.message.reply_text("✅ تایم‌زون ذخیره شد.")

# ---------------- Live post flow ----------------
async def live_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    await update.message.reply_text("پوستر لایو را ارسال کن (عکس).")
    return L_POSTER

async def live_poster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        await update.message.reply_text("لطفاً فقط عکس پوستر بفرست.")
        return L_POSTER
    context.user_data["live_poster_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("✅ پوستر دریافت شد. حالا تیتر لایو را بفرست.")
    return L_TITLE

async def live_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = (update.message.text or "").strip()
    if not title:
        await update.message.reply_text("تیتر خالی است. دوباره بفرست.")
        return L_TITLE
    context.user_data["live_title"] = title
    await update.message.reply_text("✅ تیتر دریافت شد. حالا دیسکریپشن را بفرست.")
    return L_DESC

async def live_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    desc = (update.message.text or "").strip()
    context.user_data["live_desc"] = desc
    await update.message.reply_text("✅ دیسکریپشن دریافت شد. حالا لینک مشاهده را بفرست.")
    return L_LINK

async def live_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = (update.message.text or "").strip()
    if not link.startswith("http"):
        await update.message.reply_text("لینک معتبر بفرست (با http یا https).")
        return L_LINK
    context.user_data["live_link"] = link
    await update.message.reply_text("✅ لینک دریافت شد. حالا ساعت را بفرست (مثال: 21:30). تاریخ همان امروز است.")
    return L_TIME

async def live_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = (update.message.text or "").strip()
    try:
        hh, mm = t.split(":")
        hh = int(hh); mm = int(mm)
        if hh < 0 or hh > 23 or mm < 0 or mm > 59:
            raise ValueError()
    except Exception:
        await update.message.reply_text("فرمت ساعت غلط است. مثال: 21:30")
        return L_TIME

    tz = get_tz()
    now_local = datetime.now(tz)
    live_dt = now_local.replace(hour=hh, minute=mm, second=0, microsecond=0)

    title = context.user_data.get("live_title", "")
    desc = context.user_data.get("live_desc", "")
    link = context.user_data.get("live_link", "")
    poster_id = context.user_data.get("live_poster_id")

    text = (
        "🌟 لایو شروع شد!\n\n"
        f"🎯 موضوع: {title}\n\n"
        f"{desc}\n\n"
        "📺 لینک مشاهده:\n"
        f"{link}\n\n"
        "@IRan_Tajdar"
    ).strip()

    # ارسال پوستر + متن قالبی (بدون امضا)
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=poster_id, caption=text)
    await update.message.reply_text(f"اطلاع‌رسانی لایو ارسال شد ✅ (ساعت ثبت‌شده: {live_dt:%H:%M} {storage.get_str('timezone', DEFAULT_TZ)})")
    return ConversationHandler.END

# ---------------- Auto post (JobQueue) ----------------
AUTO_JOB_NAME = "auto_post_job"
YTRSS_JOB_NAME = "youtube_rss_job"

async def auto_post_job(context: ContextTypes.DEFAULT_TYPE):
    text = storage.get_str("auto_text", DEFAULT_AUTO_TEXT)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)

async def auto_send_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    jq = context.application.job_queue
    # حذف job قبلی
    for j in jq.get_jobs_by_name(AUTO_JOB_NAME):
        j.schedule_removal()

    interval_min = storage.get_int("auto_interval_minutes", DEFAULT_AUTO_INTERVAL_MIN)
    jq.run_repeating(auto_post_job, interval=interval_min * 60, first=interval_min * 60, name=AUTO_JOB_NAME)
    storage.set_bool("auto_enabled", True)

    next_at = datetime.utcnow() + timedelta(minutes=interval_min)
    storage.set_str("auto_next_run_at_utc", next_at.isoformat())

    await update.message.reply_text(f"ارسال خودکار فعال شد ✅ (هر {interval_min} دقیقه، از الان ریست شد)")

async def auto_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    jq = context.application.job_queue
    for j in jq.get_jobs_by_name(AUTO_JOB_NAME):
        j.schedule_removal()
    storage.set_bool("auto_enabled", False)
    await update.message.reply_text("ارسال خودکار متوقف شد ✅")

async def auto_interval_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    interval_min = storage.get_int("auto_interval_minutes", DEFAULT_AUTO_INTERVAL_MIN)
    await update.message.reply_text(f"بازه فعلی: {interval_min} دقیقه ✅")

async def auto_interval_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    if not context.args:
        await update.message.reply_text("مثال: /auto_interval_set 780")
        return
    try:
        v = int(context.args[0])
        if v < 1:
            raise ValueError()
    except Exception:
        await update.message.reply_text("عدد معتبر بفرست (حداقل 1 دقیقه).")
        return
    storage.set_int("auto_interval_minutes", v)
    await update.message.reply_text("✅ بازه ذخیره شد. اگر ارسال خودکار روشن است، /auto_send_reset را بزن تا از همین لحظه با بازه جدید شروع شود.")

async def auto_text_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    await update.message.reply_text(storage.get_str("auto_text", DEFAULT_AUTO_TEXT))

async def auto_text_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    text = update.message.text.replace("/auto_text_set", "", 1).strip()
    if not text:
        await update.message.reply_text("متن را بعد از دستور بفرست: /auto_text_set ...")
        return
    storage.set_str("auto_text", text)
    await update.message.reply_text("✅ متن پست خودکار ذخیره شد.")

# ---------------- YouTube RSS job ----------------
async def youtube_rss_job(context: ContextTypes.DEFAULT_TYPE):
    if not YOUTUBE_CHANELL_ID:
        return
    feed_url = youtube_rss.channel_feed_url(YOUTUBE_CHANELL_ID)
    entries = youtube_rss.parse_entries(feed_url)

    sent = storage.get_list("yt_last_ids", [])
    sent_set = set(sent)

    new_sent = 0
    for vid, title, link in entries[:10]:
        if vid in sent_set:
            continue

        msg = f"🎬 ویدیوی جدید:\n{title}\n{link}".strip()
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)

        sent_set.add(vid)
        sent.insert(0, vid)
        new_sent += 1

    # محدودسازی لیست برای جلوگیری از بزرگ شدن DB
    sent = sent[:200]
    storage.set_list("yt_last_ids", sent)

# ---------------- Main ----------------
def build_app() -> Application:
    ensure_defaults()
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post_text", post_text))

    app.add_handler(CommandHandler("signature_show", signature_show))
    app.add_handler(CommandHandler("signature_set", signature_set))

    app.add_handler(CommandHandler("tz_show", tz_show))
    app.add_handler(CommandHandler("tz_set", tz_set))

    app.add_handler(CommandHandler("auto_send_reset", auto_send_reset))
    app.add_handler(CommandHandler("auto_stop", auto_stop))
    app.add_handler(CommandHandler("auto_interval_show", auto_interval_show))
    app.add_handler(CommandHandler("auto_interval_set", auto_interval_set))
    app.add_handler(CommandHandler("auto_text_show", auto_text_show))
    app.add_handler(CommandHandler("auto_text_set", auto_text_set))

    # Conversations: photo/video/link/live
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("post_photo", post_photo_start)],
        states={
            P_PHOTO_FILE: [MessageHandler(filters.PHOTO & ~filters.COMMAND, post_photo_file)],
            P_PHOTO_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_photo_text)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("post_video", post_video_start)],
        states={
            P_VIDEO_FILE: [MessageHandler(filters.VIDEO & ~filters.COMMAND, post_video_file)],
            P_VIDEO_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_video_text)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("post_link", post_link_start)],
        states={
            P_LINK_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_link_value)],
            P_LINK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_link_text)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("live_post", live_start)],
        states={
            L_POSTER: [MessageHandler(filters.PHOTO & ~filters.COMMAND, live_poster)],
            L_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, live_title)],
            L_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, live_desc)],
            L_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, live_link)],
            L_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, live_time)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    ))

    # Start RSS job همیشه روشن
    app.job_queue.run_repeating(youtube_rss_job, interval=60, first=10, name=YTRSS_JOB_NAME)

    # اگر auto_enabled بود بعد از ری‌استارت هم دوباره روشن شود
    if storage.get_bool("auto_enabled", False):
        interval_min = storage.get_int("auto_interval_minutes", DEFAULT_AUTO_INTERVAL_MIN)
        app.job_queue.run_repeating(auto_post_job, interval=interval_min * 60, first=interval_min * 60, name=AUTO_JOB_NAME)

    return app

def main():
    if not BOT_TOKEN or not ADMIN_ID or not CHANNEL_ID:
        raise RuntimeError("ENV ناقص است: BOT_TOKEN / ADMIN_ID / CHANNEL_ID را تنظیم کن.")
    app = build_app()
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
