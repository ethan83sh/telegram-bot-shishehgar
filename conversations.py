# conversations.py
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import storage
from config import (
    ADMIN_ID,
    CHANNEL_ID,
    DEFAULT_TZ,
    DEFAULT_AUTO_TEXT,
    DEFAULT_AUTO_INTERVAL_MIN,
)
from keyboards import (
    CB_MAIN,
    CB_POST_TEXT,
    CB_POST_PHOTO,
    CB_POST_VIDEO,
    CB_POST_LINK,
    CB_SIG_SET,
    CB_AUTO_INTERVAL_SET,
    CB_AUTO_TEXT_SET,
    CB_TZ_SET,
    CB_LIVE_START,
    kb_back_main,
)
from telegram.constants import ParseMode


# ---------- States ----------
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
# --------------------------


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


# ---------------- Back handler ----------------
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fallback for inline "Back to main menu".
    Ends any active conversation.
    """
    if update.callback_query:
        q = update.callback_query
        await q.answer()
        await q.edit_message_text("منو اصلی:", reply_markup=kb_back_main())
        # توجه: kb_back_main فقط دکمه برگشت دارد؛ منوی اصلی را در menus.show_main_menu نمایش می‌دهیم.
        # اما چون اینجا ماژول conversations است، پیام ساده می‌دهیم و کاربر دکمه را می‌زند تا به MAIN برگردد.
    else:
        await update.effective_message.reply_text("برای بازگشت، دکمه «بازگشت به منو اصلی» را بزن.", reply_markup=kb_back_main())
    return ConversationHandler.END


# ---------------- Entry points (from buttons) ----------------
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


async def cb_start_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("پوستر لایو را ارسال کن (عکس):", reply_markup=kb_back_main())
    return S_LIVE_POSTER


# ---------------- Steps ----------------
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
    await update.message.reply_text("✅ بازه ذخیره شد. برای اعمال از همین لحظه روی «ارسال خودکار (ریست...)» بزن.", reply_markup=kb_back_main())
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


# ---- Live flow (بدون امضا، قالب ثابت) ----
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
        hh = int(hh)
        mm = int(mm)
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


# ---------------- Builder ----------------
def build_conversations():
    """
    Returns a list of handlers to be added to Application.
    """
    handlers = []

    handlers.append(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_post_text, pattern=f"^{CB_POST_TEXT}$")],
        states={S_POST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_post_text)]},
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$")],
        allow_reentry=True,
    ))

    handlers.append(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_post_photo, pattern=f"^{CB_POST_PHOTO}$")],
        states={
            S_PHOTO_FILE: [MessageHandler(filters.PHOTO & ~filters.COMMAND, step_photo_file)],
            S_PHOTO_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_photo_text)],
        },
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$")],
        allow_reentry=True,
    ))

    handlers.append(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_post_video, pattern=f"^{CB_POST_VIDEO}$")],
        states={
            S_VIDEO_FILE: [MessageHandler(filters.VIDEO & ~filters.COMMAND, step_video_file)],
            S_VIDEO_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_video_text)],
        },
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$")],
        allow_reentry=True,
    ))

    handlers.append(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_post_link, pattern=f"^{CB_POST_LINK}$")],
        states={
            S_LINK_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_link_value)],
            S_LINK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_link_text)],
        },
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$")],
        allow_reentry=True,
    ))

    handlers.append(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_sig_set, pattern=f"^{CB_SIG_SET}$")],
        states={S_SIG_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_sig_set)]},
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$")],
        allow_reentry=True,
    ))

    handlers.append(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_auto_interval_set, pattern=f"^{CB_AUTO_INTERVAL_SET}$")],
        states={S_AUTO_INTERVAL_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_auto_interval_set)]},
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$")],
        allow_reentry=True,
    ))

    handlers.append(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_auto_text_set, pattern=f"^{CB_AUTO_TEXT_SET}$")],
        states={S_AUTO_TEXT_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_auto_text_set)]},
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$")],
        allow_reentry=True,
    ))

    handlers.append(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_tz_set, pattern=f"^{CB_TZ_SET}$")],
        states={S_TZ_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_tz_set)]},
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$")],
        allow_reentry=True,
    ))

    handlers.append(ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_start_live, pattern=f"^{CB_LIVE_START}$")],
        states={
            S_LIVE_POSTER: [MessageHandler(filters.PHOTO & ~filters.COMMAND, step_live_poster)],
            S_LIVE_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_live_title)],
            S_LIVE_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_live_desc)],
            S_LIVE_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_live_link)],
            S_LIVE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_live_time)],
        },
        fallbacks=[CallbackQueryHandler(back_to_main, pattern=f"^{CB_MAIN}$")],
        allow_reentry=True,
    ))

    return handlers

