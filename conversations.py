from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import storage
import jobs
from config import (
    ADMIN_ID, CHANNEL_ID,
    DEFAULT_TZ, DEFAULT_AUTO_TEXT, DEFAULT_AUTO_INTERVAL_MIN,
)
from keyboards import (
    CB_MAIN,
    CB_POST_TEXT, CB_POST_PHOTO, CB_POST_VIDEO, CB_POST_LINK,
    CB_SIG_SET,
    CB_AUTO_INTERVAL_SET, CB_AUTO_TEXT_SET,
    CB_TZ_SET,
    CB_LIVE_NEW,
    kb_back_main,
)

# -------- States --------
S_POST_TEXT = 10
S_PHOTO_FILE, S_PHOTO_TEXT = 20, 21
S_VIDEO_FILE, S_VIDEO_TEXT = 30, 31
S_LINK_VALUE, S_LINK_TEXT = 40, 41
S_SIG_SET = 50
S_AUTO_INTERVAL_SET = 60
S_AUTO_TEXT_SET = 61
S_TZ_SET = 70

# Live new flow
S_LIVE_TODAY_Q = 80
S_LIVE_DATE = 81
S_LIVE_TIME = 82
S_LIVE_POSTER = 83
S_LIVE_TITLE = 84
S_LIVE_DESC = 85
S_LIVE_LINK = 86

# Live edit flow
S_LIVE_EDIT_INPUT = 90
# ------------------------

def is_admin(update: Update) -> bool:
    return bool(update.effective_user and update.effective_user.id == ADMIN_ID)

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

def kb_yes_no_today():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ بله (امروز)", callback_data="LIVE_TODAY:YES"),
            InlineKeyboardButton("❌ خیر", callback_data="LIVE_TODAY:NO"),
        ],
        [InlineKeyboardButton("⬅️ بازگشت به منو اصلی", callback_data=CB_MAIN)],
    ])

def _make_live_id() -> str:
    return f"L{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}"

def _load_events_sorted():
    events = jobs.load_live_events()
    def keyf(e):
        try:
            return datetime.fromisoformat(e["dt"])
        except Exception:
            return datetime.max
    return sorted(events, key=keyf)

def _find_event(live_id: str):
    events = jobs.load_live_events()
    for e in events:
        if e.get("id") == live_id:
            return e
    return None

def _upsert_event(updated):
    events = jobs.load_live_events()
    out = []
    found = False
    for e in events:
        if e.get("id") == updated.get("id"):
            out.append(updated)
            found = True
        else:
            out.append(e)
    if not found:
        out.append(updated)
    jobs.save_live_events(out)

def _remove_event(live_id: str):
    events = jobs.load_live_events()
    events = [e for e in events if e.get("id") != live_id]
    jobs.save_live_events(events)

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        q = update.callback_query
        await q.answer()
        await q.edit_message_text("برای رفتن به منوی اصلی، دکمه بازگشت را بزن.", reply_markup=kb_back_main())
    else:
        await update.effective_message.reply_text("برای بازگشت، دکمه را بزن.", reply_markup=kb_back_main())
    return ConversationHandler.END


# -------- Entry points (buttons) --------
async def cb_start_post_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("متن پست را بفرست:", reply_markup=kb_back_main())
    return S_POST_TEXT

async def cb_start_post_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("عکس را ارسال کن (بدون کپشن):", reply_markup=kb_back_main())
    return S_PHOTO_FILE

async def cb_start_post_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("ویدیو را ارسال کن (بدون کپشن):", reply_markup=kb_back_main())
    return S_VIDEO_FILE

async def cb_start_post_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("لینک را ارسال کن:", reply_markup=kb_back_main())
    return S_LINK_VALUE

async def cb_start_sig_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("متن امضا را بفرست:", reply_markup=kb_back_main())
    return S_SIG_SET

async def cb_start_auto_interval_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("عدد بازه را به دقیقه بفرست (مثال: 780):", reply_markup=kb_back_main())
    return S_AUTO_INTERVAL_SET

async def cb_start_auto_text_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("متن جدید پست خودکار را بفرست:", reply_markup=kb_back_main())
    return S_AUTO_TEXT_SET

async def cb_start_tz_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("تایم‌زون را بفرست (مثال: Europe/Berlin):", reply_markup=kb_back_main())
    return S_TZ_SET

# ---- Live new starts from LIVE_NEW button ----
async def cb_start_live_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    # پاک کردن داده‌های قبلی
    context.user_data.pop("live_new", None)
    await q.edit_message_text("آیا لایو برای امروز است؟", reply_markup=kb_yes_no_today())
    return S_LIVE_TODAY_Q

# ---- Live edit field starts from LIVE_EDIT_FIELD:<id>:<field> ----
async def cb_start_live_edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    _, live_id, field = q.data.split(":", 2)  # LIVE_EDIT_FIELD:<id>:<field>
    context.user_data["live_edit"] = {"id": live_id, "field": field}

    if field == "poster":
        await q.edit_message_text("پوستر جدید را ارسال کن (عکس):", reply_markup=kb_back_main())
    elif field == "title":
        await q.edit_message_text("تیتر جدید را بفرست:", reply_markup=kb_back_main())
    elif field == "desc":
        await q.edit_message_text("دیسکریپشن جدید را بفرست:", reply_markup=kb_back_main())
    elif field == "link":
        await q.edit_message_text("لینک جدید را بفرست:", reply_markup=kb_back_main())
    elif field == "dt":
        await q.edit_message_text("تاریخ و ساعت جدید را بفرست.\nفرمت تاریخ: YYYY-MM-DD\nسپس ساعت: HH:MM\n(در دو پیام جدا)", reply_markup=kb_back_main())
        context.user_data["live_edit"]["dt_step"] = "date"
    else:
        await q.edit_message_text("فیلد ناشناخته.", reply_markup=kb_back_main())
        return ConversationHandler.END

    return S_LIVE_EDIT_INPUT

# -------- Steps: Posts --------
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
    await update.message.reply_text("پست عکس با موفقیت ارسال شد ✅", reply_markup=kb_back_main())
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
    await update.message.reply_text("پست ویدیو با موفقیت ارسال شد ✅", reply_markup=kb_back_main())
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
    await update.message.reply_text("پست لینک با موفقیت ارسال شد ✅", reply_markup=kb_back_main())
    return ConversationHandler.END

# -------- Steps: Settings --------
async def step_sig_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("متن امضا خالی است. دوباره بفرست.")
        return S_SIG_SET
    storage.set_str("signature_text", text)
    await update.message.reply_text("✅ امضا ذخیره شد.", reply_markup=kb_back_main())
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
    await update.message.reply_text("✅ بازه ذخیره شد. برای اعمال، دکمه ارسال خودکار را بزن.", reply_markup=kb_back_main())
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

# -------- Live new flow steps --------
async def step_live_today_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    choice = q.data.split(":")[-1]  # YES/NO
    tz = get_tz()
    now_local = datetime.now(tz)

    live_new = {
        "tz": storage.get_str("timezone", DEFAULT_TZ),
        "date": None,
        "time": None,
        "poster_file_id": None,
        "title": "",
        "desc": "",
        "link": "",
    }

    if choice == "YES":
        live_new["date"] = now_local.strftime("%Y-%m-%d")
        context.user_data["live_new"] = live_new
        await q.edit_message_text("✅ امروز ثبت شد. حالا ساعت را بفرست (HH:MM):", reply_markup=kb_back_main())
        return S_LIVE_TIME

    # NO
    context.user_data["live_new"] = live_new
    await q.edit_message_text("تاریخ لایو را بفرست (YYYY-MM-DD):", reply_markup=kb_back_main())
    return S_LIVE_DATE

async def step_live_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_str = (update.message.text or "").strip()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        await update.message.reply_text("فرمت تاریخ غلط است. مثال: 2026-01-30")
        return S_LIVE_DATE

    context.user_data["live_new"]["date"] = date_str
    await update.message.reply_text("✅ تاریخ ثبت شد. حالا ساعت را بفرست (HH:MM):")
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

    context.user_data["live_new"]["time"] = t
    await update.message.reply_text("حالا پوستر لایو را ارسال کن (عکس):")
    return S_LIVE_POSTER

async def step_live_poster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً فقط عکس پوستر بفرست.")
        return S_LIVE_POSTER
    context.user_data["live_new"]["poster_file_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("✅ پوستر دریافت شد. حالا تیتر لایو را بفرست:")
    return S_LIVE_TITLE

async def step_live_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = (update.message.text or "").strip()
    if not title:
        await update.message.reply_text("تیتر خالی است. دوباره بفرست.")
        return S_LIVE_TITLE
    context.user_data["live_new"]["title"] = title
    await update.message.reply_text("✅ تیتر ثبت شد. حالا دیسکریپشن را بفرست:")
    return S_LIVE_DESC

async def step_live_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    desc = (update.message.text or "").strip()
    context.user_data["live_new"]["desc"] = desc
    await update.message.reply_text("✅ دیسکریپشن ثبت شد. حالا لینک مشاهده را بفرست:")
    return S_LIVE_LINK

async def step_live_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = (update.message.text or "").strip()
    if not link.startswith("http"):
        await update.message.reply_text("لینک معتبر بفرست (با http یا https).")
        return S_LIVE_LINK
    context.user_data["live_new"]["link"] = link

    # ساخت datetime آگاه به تایم‌زون
    tz = get_tz()
    date_str = context.user_data["live_new"]["date"]
    time_str = context.user_data["live_new"]["time"]
    yyyy, mm, dd = map(int, date_str.split("-"))
    hh, mi = map(int, time_str.split(":"))
    dt_local = datetime(yyyy, mm, dd, hh, mi, tzinfo=tz)

    # ساخت event
    live_id = _make_live_id()
    event = {
        "id": live_id,
        "dt": dt_local.isoformat(),
        "tz": storage.get_str("timezone", DEFAULT_TZ),
        "poster_file_id": context.user_data["live_new"]["poster_file_id"],
        "title": context.user_data["live_new"]["title"],
        "desc": context.user_data["live_new"]["desc"],
        "link": context.user_data["live_new"]["link"],
        "job_name": jobs.live_job_name(live_id),
        "created_at": datetime.utcnow().isoformat(),
    }

    # ذخیره در DB
    events = jobs.load_live_events()
    events.append(event)
    jobs.save_live_events(events)

    # زمان‌بندی ارسال راس زمان (run_once) [web:6]
    context.application.job_queue.run_once(
        jobs.live_send_job,
        when=dt_local,
        name=jobs.live_job_name(live_id),
        data=event,
    )

    await update.message.reply_text(
        f"✅ لایو در صف قرار گرفت.\nزمان ارسال: {event['dt']}",
        reply_markup=kb_back_main(),
    )
    return ConversationHandler.END


# -------- Live edit flow (field-based) --------
async def step_live_edit_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = context.user_data.get("live_edit", {})
    live_id = info.get("id")
    field = info.get("field")

    e = _find_event(live_id)
    if not e:
        await update.message.reply_text("⛔️ این لایو پیدا نشد.", reply_markup=kb_back_main())
        return ConversationHandler.END

    # پوستر
    if field == "poster":
        if not update.message.photo:
            await update.message.reply_text("لطفاً فقط عکس بفرست.")
            return S_LIVE_EDIT_INPUT
        e["poster_file_id"] = update.message.photo[-1].file_id
        _upsert_event(e)
        await update.message.reply_text("✅ پوستر آپدیت شد.", reply_markup=kb_back_main())
        return ConversationHandler.END

    # متنی‌ها
    txt = (update.message.text or "").strip()

    if field == "title":
        if not txt:
            await update.message.reply_text("تیتر خالی است. دوباره بفرست.")
            return S_LIVE_EDIT_INPUT
        e["title"] = txt
        _upsert_event(e)
        await update.message.reply_text("✅ تیتر آپدیت شد.", reply_markup=kb_back_main())
        return ConversationHandler.END

    if field == "desc":
        e["desc"] = txt
        _upsert_event(e)
        await update.message.reply_text("✅ دیسکریپشن آپدیت شد.", reply_markup=kb_back_main())
        return ConversationHandler.END

    if field == "link":
        if not txt.startswith("http"):
            await update.message.reply_text("لینک معتبر بفرست (با http یا https).")
            return S_LIVE_EDIT_INPUT
        e["link"] = txt
        _upsert_event(e)
        await update.message.reply_text("✅ لینک آپدیت شد.", reply_markup=kb_back_main())
        return ConversationHandler.END

    if field == "dt":
        tz = get_tz()
        step = info.get("dt_step", "date")

        if step == "date":
            try:
                datetime.strptime(txt, "%Y-%m-%d")
            except Exception:
                await update.message.reply_text("فرمت تاریخ غلط است. مثال: 2026-01-30")
                return S_LIVE_EDIT_INPUT
            context.user_data["live_edit"]["new_date"] = txt
            context.user_data["live_edit"]["dt_step"] = "time"
            await update.message.reply_text("✅ تاریخ ثبت شد. حالا ساعت را بفرست (HH:MM):")
            return S_LIVE_EDIT_INPUT
