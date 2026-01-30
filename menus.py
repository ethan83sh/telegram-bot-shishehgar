from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

import storage
import jobs
from config import DEFAULT_TZ, DEFAULT_AUTO_TEXT, DEFAULT_AUTO_INTERVAL_MIN
from keyboards import (
    CB_MAIN,
    CB_POST_MENU, CB_AUTO_MENU, CB_TZ_MENU,
    CB_SIG_SHOW,
    CB_AUTO_INTERVAL_SHOW, CB_AUTO_TEXT_SHOW, CB_TZ_SHOW,
    CB_AUTO_SEND_RESET, CB_AUTO_STOP,
    CB_LIVE_MENU,
    kb_main, kb_post_menu, kb_auto_menu, kb_tz_menu, kb_live_menu,
    kb_back_main, kb_live_nav, kb_live_edit_fields,
)

async def show_main_menu(update: Update, text: str = "منو اصلی:"):
    if update.callback_query:
        q = update.callback_query
        await q.answer()
        await q.edit_message_text(text=text, reply_markup=kb_main())
    else:
        await update.message.reply_text(text, reply_markup=kb_main())

def _sorted_live_events():
    events = jobs.load_live_events()
    def keyf(e):
        try:
            return datetime.fromisoformat(e["dt"])
        except Exception:
            return datetime.max
    return sorted(events, key=keyf)

async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "NOP":
        return

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

    if data == CB_LIVE_MENU:
        await q.edit_message_text("🔴 منوی لایو:", reply_markup=kb_live_menu())
        return

    # ---- Simple views ----
    if data == CB_SIG_SHOW:
        sig = storage.get_str("signature_text", "@Iran_Tajdar")
        await q.edit_message_text(f"امضای فعلی:\n{sig}\n✅", reply_markup=kb_post_menu())
        return

    if data == CB_AUTO_INTERVAL_SHOW:
        interval_min = storage.get_int("auto_interval_minutes", DEFAULT_AUTO_INTERVAL_MIN)
        await q.edit_message_text(f"بازه فعلی: {interval_min} دقیقه ✅", reply_markup=kb_auto_menu())
        return

    if data == CB_AUTO_TEXT_SHOW:
        txt = storage.get_str("auto_text", DEFAULT_AUTO_TEXT)
        await q.edit_message_text("متن پست خودکار در پیام بعد ارسال شد ✅", reply_markup=kb_auto_menu())
        await q.message.reply_text(txt, reply_markup=kb_back_main())
        return

    if data == CB_TZ_SHOW:
        tz_name = storage.get_str("timezone", DEFAULT_TZ)
        now_utc = datetime.utcnow()
        await q.edit_message_text(
            f"TZ فعلی: {tz_name}\nUTC: {now_utc:%Y-%m-%d %H:%M}\n✅",
            reply_markup=kb_tz_menu(),
        )
        return

    # ---- Auto actions ----
    if data == CB_AUTO_SEND_RESET:
        await q.edit_message_text("در حال ارسال فوری و ریست زمان‌بندی... ⏳")
        await jobs.auto_send_reset_now(context)
        interval_min = storage.get_int("auto_interval_minutes", DEFAULT_AUTO_INTERVAL_MIN)
        await q.edit_message_text(
            f"✅ ارسال فوری انجام شد و ارسال خودکار از الان ریست شد.\n(هر {interval_min} دقیقه)",
            reply_markup=kb_auto_menu(),
        )
        return

    if data == CB_AUTO_STOP:
        await jobs.auto_stop(context)
        await q.edit_message_text("ارسال خودکار متوقف شد ✅", reply_markup=kb_auto_menu())
        return

    # ---- Live list one-by-one ----
    if data.startswith("LIVE_LIST:idx:"):
        events = _sorted_live_events()
        if not events:
            await q.edit_message_text("هیچ لایوی در صف نیست ✅", reply_markup=kb_live_menu())
            return

        try:
            idx = int(data.split(":")[-1])
        except Exception:
            idx = 0

        idx = max(0, min(idx, len(events) - 1))
        e = events[idx]

        await q.edit_message_text(
            f"🔴 لایو پیش‌رو\n\n"
            f"🕒 زمان: {e['dt']}\n"
            f"🎯 موضوع: {e['title']}\n"
            f"📺 لینک: {e['link']}\n",
            reply_markup=kb_live_nav(idx, len(events), e["id"]),
        )
        return

    if data.startswith("LIVE_DEL:"):
        live_id = data.split(":", 1)[1]

        # حذف از DB
        events = jobs.load_live_events()
        events = [e for e in events if e.get("id") != live_id]
        jobs.save_live_events(events)

        # حذف job از صف (schedule_removal) [web:12]
        for j in context.application.job_queue.get_jobs_by_name(jobs.live_job_name(live_id)):
            j.schedule_removal()

        await q.edit_message_text("✅ لایو از صف حذف شد.", reply_markup=kb_live_menu())
        return

    if data.startswith("LIVE_EDIT:"):
        live_id = data.split(":", 1)[1]
        await q.edit_message_text("کدام بخش را می‌خواهی تغییر بدهی؟", reply_markup=kb_live_edit_fields(live_id))
        return

    # تغییر فیلدها را conversations.py انجام می‌دهد
    if data.startswith("LIVE_EDIT_FIELD:"):
        # اینجا فقط پیام بدهیم؛ Conversation مربوطه آن را می‌گیرد
        await q.edit_message_text("در حال ورود به حالت تغییر... ⏳", reply_markup=kb_back_main())
        return
