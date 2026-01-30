import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import storage
import youtube_rss

# ---------------- ENV ----------------
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
YOUTUBE_CHANELL_ID = os.getenv("YOUTUBE_CHANELL_ID", "")
# -------------------------------------

# ---------------- Defaults ----------------
DEFAULT_TZ = "Europe/Berlin"  # تایم‌زون پیشفرض
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
# ------------------------------------------


# ---------------- Menu callback keys ----------------
CB_MAIN = "MAIN"

CB_POST_MENU = "POST_MENU"
CB_POST_TEXT = "POST_TEXT"
CB_POST_PHOTO = "POST_PHOTO"
CB_POST_VIDEO = "POST_VIDEO"
CB_POST_LINK = "POST_LINK"
CB_SIG_SHOW = "SIG_SHOW"
CB_SIG_SET = "SIG_SET"

CB_AUTO_MENU = "AUTO_MENU"
CB_AUTO_SEND_RESET = "AUTO_SEND_RESET"
CB_AUTO_STOP = "AUTO_STOP"
CB_AUTO_INTERVAL_SHOW = "AUTO_INTERVAL_SHOW"
CB_AUTO_INTERVAL_SET = "AUTO_INTERVAL_SET"
CB_AUTO_TEXT_SHOW = "AUTO_TEXT_SHOW"
CB_AUTO_TEXT_SET = "AUTO_TEXT_SET"

CB_LIVE_START = "LIVE_START"

CB_TZ_MENU = "TZ_MENU"
CB_TZ_SHOW = "TZ_SHOW"
CB_TZ_SET = "TZ_SET"
# ----------------------------------------------------


# ---------------- Conversation states ----------------
S_POST_TEXT = 10

S_PHOTO_FILE = 20
S_PHOTO_TEXT = 21

S_VIDEO_FILE = 30
S_VIDEO_TEXT = 31

S_LINK_VALUE = 40
S_LINK_TEXT = 41

S_SIG_SET = 50

S_AUTO_INTERVAL_SET = 60
S_AUTO_TEXT_SET = 61

S_TZ_SET = 70

S_LIVE_POSTER = 80
S_LIVE_TITLE = 81
S_LIVE_DESC = 82
S_LIVE_LINK = 83
S_LIVE_TIME = 84
# ----------------------------------------------------


AUTO_JOB_NAME = "auto_post_job"
YTRSS_JOB_NAME = "youtube_rss_job"


# ---------------- Helpers ----------------
def is_admin(update: Update) -> bool:
    return bool(update.effective_user and update.effective_user.id == ADMIN_ID)

async def deny_if_not_admin(update: Update) -> bool:
    if not is_admin(update):
        if update.effective_message:
            await update.effective_message.reply_text("⛔️ دسترسی ندارید.")
        return True
    return False

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

def get_tz() -> ZoneInfo:
    tz_name = storage.get_str("timezone", DEFAULT_TZ)
    try:
        return ZoneInfo(tz_name)
    except Exception:
        storage.set_str("timezone", DEFAULT_TZ)
        return ZoneInfo(DEFAULT_TZ)

def build_caption(text: str) -> str:
    sig = storage.get_str("signature_text", "@Iran_Tajdar")
    text = (text or "").strip()
    return f"{text}\n\n{sig}".strip()

def kb_back_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ بازگشت به منو اصلی", callback_data=CB_MAIN)]])

def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 ارسال پست", callback_data=CB_POST_MENU)],
        [InlineKeyboardButton("⏱ پست خودکار", callback_data=CB_AUTO_MENU)],
        [InlineKeyboardButton("🔴 پست لایو", callback_data=CB_LIVE_START)],
        [InlineKeyboardButton("🕒 تایم‌زون", callback_data=CB_TZ_MENU)],
    ])

def kb_post_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 پست متنی", callback_data=CB_POST_TEXT)],
        [InlineKeyboardButton("🖼 پست عکس", callback_data=CB_POST_PHOTO)],
        [InlineKeyboardButton("🎞 پست ویدیو", callback_data=CB_POST_VIDEO)],
        [InlineKeyboardButton("🔗 پست لینک", callback_data=CB_POST_LINK)],
        [InlineKeyboardButton("👁 مشاهده امضا", callback_data=CB_SIG_SHOW)],
        [InlineKeyboardButton("✏️ تغییر امضا", callback_data=CB_SIG_SET)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=CB_MAIN)],
    ])

def kb_auto_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 ارسال خودکار (ریست از الان)", callback_data=CB_AUTO_SEND_RESET)],
        [InlineKeyboardButton("🛑 توقف ارسال خودکار", callback_data=CB_AUTO_STOP)],
        [InlineKeyboardButton("⏲ مشاهده بازه", callback_data=CB_AUTO_INTERVAL_SHOW)],
        [InlineKeyboardButton("✏️ تغییر بازه", callback_data=CB_AUTO_INTERVAL_SET)],
        [InlineKeyboardButton("👁 مشاهده متن خودکار", callback_data=CB_AUTO_TEXT_SHOW)],
        [InlineKeyboardButton("✏️ تغییر متن خودکار", callback_data=CB_AUTO_TEXT_SET)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=CB_MAIN)],
    ])

def kb_tz_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👁 مشاهده زمان‌ها", callback_data=CB_TZ_SHOW)],
        [InlineKeyboardButton("✏️ تغییر تایم‌زون", callback_data=CB_TZ_SET)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=CB_MAIN)],
    ])

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str = "منو اصلی:"):
    if update.callback_query:
        q = update.callback_query
        await q.answer()
        await q.edit_message_text(text=text, reply_markup=kb_main())
    else:
        await update.message.reply_text(text, reply_markup=kb_main())

# ----------------------------------------------------


# ---------------- Jobs ----------------
async def auto_post_job(context: ContextTypes.DEFAULT_TYPE):
    text = storage.get_str("auto_text", DEFAULT_AUTO_TEXT)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)

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

# ----------------------------------------------------


# ---------------- Start & Menu router ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return
    ensure_defaults()
    await show_main_menu(update, context, "✅ ربات آماده است.\nمنو اصلی:")

async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return

    q = update.callback_query
    await q.answer()

    data = q.data

    if data == CB_MAIN:
        await q.edit_message_text("منو اصلی:", reply_markup=kb_main())
        return

    if data == CB_POST_MENU:
        await q.edit_message_text("📤 منوی ارسال پست:", reply_markup=kb_post_menu())
        return

    if data == CB_AUTO_MENU:
        await q.edit_message_text("⏱ منوی پست خودکار:", reply_markup=kb_auto_menu())
        return

    if data == CB_TZ_MENU:
        await q.edit_message_text("🕒 منوی تایم‌زون:", reply_markup=kb_tz_menu())
        return

    # actions that don't need conversation
    if data == CB_SIG_SHOW:
        sig = storage.get_str("signature_text", "@Iran_Tajdar")
        await q.edit_message_text(f"امضای فعلی:\n{sig}", reply_markup=kb_post_menu())
        return

    if data == CB_AUTO_INTERVAL_SHOW:
        interval_min = storage.get_int("auto_interval_minutes", DEFAULT_AUTO_INTERVAL_MIN)
        await q.edit_message_text(f"بازه فعلی: {interval_min} دقیقه ✅", reply_markup=kb_auto_menu())
        return

    if data == CB_AUTO_TEXT_SHOW:
        txt = storage.get_str("auto_text", DEFAULT_AUTO_TEXT)
        await q.edit_message_text("متن پست خودکار در پیام بعد ارسال می‌شود ✅", reply_markup=kb_auto_menu())
        await q.message.reply_text(txt, reply_markup=kb_back_main())
        return

    if data == CB_TZ_SHOW:
        tz_name = storage.get_str("timezone", DEFAULT_TZ)
        now_utc = datetime.utcnow()
        now_local = datetime.now(get_tz())
        await q.edit_message_text(
            f"TZ فعلی: {tz_name}\nUTC: {now_utc:%Y-%m-%d %H:%M}\nLocal: {now_local:%Y-%m-%d %H:%M}\n✅",
            reply_markup=kb_tz_menu(),
        )
        return

    if data == CB_AUTO_SEND_RESET:
        jq = context.application.job_queue
        for j in jq.get_jobs_by_name(AUTO_JOB_NAME):
            j.schedule_removal()

        interval_min = storage.get_int("auto_interval_minutes", DEFAULT_AUTO_INTERVAL_MIN)
        jq.run_repeating(auto_post_job, interval=interval_min * 60, first=interval_min * 60, name=AUTO_JOB_NAME)
        storage.set_bool("auto_enabled", True)

        next_at = datetime.utcnow() + timedelta(minutes=interval_min)
        storage.set_str("auto_next_run_at_utc", next_at.isoformat())

        await q.edit_message_text(f"ارسال خودکار فعال شد ✅ (هر {interval_min} دقیقه، از الان ریست شد)", reply_markup=kb_auto_menu())
        return

    if data == CB_AUTO_STOP:
        jq = context.application.job_queue
        for j in jq.get_jobs_by_name(AUTO_JOB_NAME):
            j.schedule_removal()
        storage.set_bool("auto_enabled", False)
        await q.edit_message_text("ارسال خودکار متوقف شد ✅", reply_markup=kb_auto_menu())
        return

# ----------------------------------------------------


# ---------------- Conversations entry points (from buttons) ----------------
async def cb_start_post_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("متن پست را بفرست:", reply_markup=kb_back_main())
    return S_POST_TEXT

async def cb_start_post_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("عکس را ارسال کن (بدون کپشن):", reply_markup=kb_back_main())
    return S_PHOTO_FILE

async def cb_start_post_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("ویدیو را ارسال کن (بدون کپشن):", reply_markup=kb_back_main())
    return S_VIDEO_FILE

async def cb_start_post_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("لینک را ارسال کن:", reply_markup=kb_back_main())
    return S_LINK_VALUE

async def cb_start_sig_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("متن امضا را بفرست:", reply_markup=kb_back_main())
    return S_SIG_SET

async def cb_start_auto_interval_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("عدد بازه را به دقیقه بفرست (مثال: 780):", reply_markup=kb_back_main())
    return S_AUTO_INTERVAL_SET

async def cb_start_auto_text_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("متن جدید پست خودکار را بفرست:", reply_markup=kb_back_main())
    return S_AUTO_TEXT_SET

async def cb_start_tz_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("تایم‌زون را بفرست (مثال: Europe/Berlin):", reply_markup=kb_back_main())
    return S_TZ_SET

async def cb_start_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await deny_if_not_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("پوستر لایو را ارسال کن (عکس):", reply_markup=kb_back_main())
    return S_LIVE_POSTER

# ----------------------------------------------------


# ---------------- Conversation steps ----------------
async def step_post_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    await context.bot.send_message(chat_id=CHANNEL_ID, text=build_caption(text), parse_mode=ParseMode.HTML)
    await update.message.reply_text("پست متنی با موفقیت ارسال شد ✅", reply_markup=kb_back_main())
    return ConversationHandler.END

async def step_photo_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً فقط عکس بفرست.")
        return S_PHOTO_FILE
    context.user_data["photo_file_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("✅ عکس دریافت شد. حالا متن پست را بفرست.")
    return S_PHOTO_TEXT

async def step_photo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    file_id = context.user_data.get("photo_file_id")
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=file_id, caption=build_caption(text))
    await update.message.reply_text("پست عکس با موفقیت به کانال ارسال شد ✅", reply_markup=kb_back_main())
    return ConversationHandler.END

async def step_video_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.video:
        await update.message.reply_text("لطفاً فقط ویدیو بفرست.")
        return S_VIDEO_FILE
    context.user_data["video_file_id"] = update.message.video.file_id
    await update.message.reply_text("✅ ویدیو دریافت شد. حالا متن پست را بفرست.")
    return S_VIDEO_TEXT

async def step_video_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    file_id = context.user_data.get("video_file_id")
    await context.bot.send_video(chat_id=CHANNEL_ID, video=file_id, caption=build_caption(text))
    await update.message.reply_text("پست ویدیو با موفقیت به کانال ارسال شد ✅", reply_markup=kb_back_main())
    return ConversationHandler.END

async def step_link_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = (update.message.text or "").strip()
    if not link.startswith("http"):
        await update.message.reply_text("لینک معتبر بفرست (با http یا https).")
        return S_LINK_VALUE
    context.user_data["link_value"] = link
    await update.message.reply_text("✅ لینک دریافت شد. حالا متن پست را بفرست.")
    return S_LINK_TEXT

async def step_link_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    link = context.user_data.get("link_value", "")
    final = build_caption(f"{text}\n\n{link}".strip())
    await context.bot.send_message(chat_id=CHANNEL_ID, text=final)
    await update.message.reply_text("پست لینک با موفقیت به کانال ارسال شد ✅", reply_markup=kb_back_main())
    return ConversationHandler.END

async def step_sig_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("متن امضا خالی است. دوباره بفرست.")
        return S_SIG_SET
    storage.set_str("signature_text", text)
    await update.message.reply_text("✅ امضا با موفقیت ذخیره شد.", reply_markup=kb_back_main())
    return ConversationHandler.END

async def step_auto_interval_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()
    try:
        v = int(raw)
        if v < 1:
            raise ValueError()
    except Exception:
        await update.message.reply_text("عدد معتبر بفرست (حداقل 1 دقیقه).")
        return S_AUTO_INTERVAL_SET
    storage.set_int("auto_interval_minutes", v)
    await update.message.reply_text("✅ بازه ذخیره شد. برای اعمال از همین لحظه روی «ارسال خودکار (ریست از الان)» بزن.", reply_markup=kb_back_main())
    return ConversationHandler.END

async def step_auto_text_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("متن خالی است. دوباره بفرست.")
        return S_AUTO_TEXT_SET
    storage.set_str("auto_text", text)
    await update.message.reply_text("✅ متن پست خودکار ذخیره شد.", reply_markup=kb_back_main())
    return ConversationHandler.END

async def step_tz_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tz_name = (update.message.text or "").strip()
    try:
        ZoneInfo(tz_name)
    except Exception:
        await update.message.reply_text("⛔️ تایم‌زون نامعتبر است. مثال: Europe/Berlin")
        return S_TZ_SET
    storage.set_str("timezone", tz_name)
    await update.message.reply_text("✅ تایم‌زون ذخیره شد.", reply_markup=kb_back_main())
    return ConversationHandler.END

# ---- Live flow ----
async def step_live_poster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً فقط عکس پوستر بفرست.")
        return S_LIVE_POSTER
    context.user_data["live_poster_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("✅ پوستر دریافت شد. حالا تیتر لایو را بفرست.")
    return S_LIVE_TITLE

async def step_live_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = (update.message.text or "").strip()
    if not title:
        await update.message.reply_text("تیتر خالی است. دوباره بفرست.")
        return S_LIVE_TITLE
    context.user_data["live_title"] = title
    await update.message.reply_text("✅ تیتر دریافت شد. حالا دیسکریپشن را بفرست.")
    return S_LIVE_DESC

async def step_live_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    desc = (update.message.text or "").strip()
    context.user_data["live_desc"] = desc
    await update.message.reply_text("✅ دیسکریپشن دریافت شد. حالا لینک مشاهده را بفرست.")
    return S_LIVE_LINK

async def step_live_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = (update.message.text or "").strip()
    if not link.startswith("http"):
        await update.message.reply_text("لینک معتبر بفرست (با http یا https).")
        return S_LIVE_LINK
    context.user_data["live_link"] = link
    await update.message.reply_text("✅ لینک دریافت شد. حالا ساعت را بفرست (مثال: 21:30). تاریخ همان امروز است.")
    return S_LIVE_TIME

async def step_live_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = (update.message.text or "").strip()
    try:
        hh, mm = t.split(":")
        hh = int(hh); mm = int(mm)
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise ValueError()
    except Exception:
        await update.message.reply_text("فرمت ساعت غلط است. مثال: 21:30")
        return S_LIVE_TIME

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

    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=poster_id, caption=text)
    await update.message.reply_text(
        f"اطلاع‌رسانی لایو ارسال شد ✅ (ساعت ثبت‌شده: {live_dt:%H:%M} {storage.get_str('timezone', DEFAULT_TZ)})",
        reply_markup=kb_back_main(),
    )
    return ConversationHandler.END

# ---------------- Cancel / Back ----------------
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await show_main_menu(update, context, "منو اصلی:")
    else:
        await update.message.reply_text("منو اصلی:", reply_markup=kb_main())
    return ConversationHandler.END

# ------------------------------------------------


def build_app() -> Application:
    ensure_defaults()

    app = Application.builder().token(BOT_TOKEN).build()

    # /start
    app.add_handler(CommandHandler("start", start))

    # Main menu clicks
    app.add_handler(CallbackQueryHandler(menu_router, pattern="^(MAIN|POST_MENU|AUTO_MENU|TZ_MENU|SIG_SHOW|AUTO_SEND_RESET|AUTO_STOP|AUTO_INTERVAL_SHOW|AUTO_TEXT_SHOW|TZ_SHOW)$"))

    # Conversations (entry points are buttons)
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_post_text, pattern=f"^{CB_POST_TEXT}$")],
        states={S_POST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_post_text)]},
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$"), CommandHandler("start", start)],
        allow_reentry=True,
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_post_photo, pattern=f"^{CB_POST_PHOTO}$")],
        states={
            S_PHOTO_FILE: [MessageHandler(filters.PHOTO & ~filters.COMMAND, step_photo_file)],
            S_PHOTO_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_photo_text)],
        },
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$"), CommandHandler("start", start)],
        allow_reentry=True,
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_post_video, pattern=f"^{CB_POST_VIDEO}$")],
        states={
            S_VIDEO_FILE: [MessageHandler(filters.VIDEO & ~filters.COMMAND, step_video_file)],
            S_VIDEO_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_video_text)],
        },
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$"), CommandHandler("start", start)],
        allow_reentry=True,
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_post_link, pattern=f"^{CB_POST_LINK}$")],
        states={
            S_LINK_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_link_value)],
            S_LINK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_link_text)],
        },
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$"), CommandHandler("start", start)],
        allow_reentry=True,
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_sig_set, pattern=f"^{CB_SIG_SET}$")],
        states={S_SIG_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_sig_set)]},
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$"), CommandHandler("start", start)],
        allow_reentry=True,
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_auto_interval_set, pattern=f"^{CB_AUTO_INTERVAL_SET}$")],
        states={S_AUTO_INTERVAL_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_auto_interval_set)]},
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$"), CommandHandler("start", start)],
        allow_reentry=True,
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_auto_text_set, pattern=f"^{CB_AUTO_TEXT_SET}$")],
        states={S_AUTO_TEXT_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_auto_text_set)]},
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$"), CommandHandler("start", start)],
        allow_reentry=True,
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_tz_set, pattern=f"^{CB_TZ_SET}$")],
        states={S_TZ_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_tz_set)]},
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$"), CommandHandler("start", start)],
        allow_reentry=True,
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_live, pattern=f"^{CB_LIVE_START}$")],
        states={
            S_LIVE_POSTER: [MessageHandler(filters.PHOTO & ~filters.COMMAND, step_live_poster)],
            S_LIVE_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_live_title)],
            S_LIVE_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_live_desc)],
            S_LIVE_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_live_link)],
            S_LIVE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_live_time)],
        },
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$"), CommandHandler("start", start)],
        allow_reentry=True,
    ))

    # RSS job always on
    app.job_queue.run_repeating(youtube_rss_job, interval=60, first=10, name=YTRSS_JOB_NAME)

    # Restore auto job after restart
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
