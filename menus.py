# menus.py
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

import storage
from config import DEFAULT_TZ, DEFAULT_AUTO_TEXT, DEFAULT_AUTO_INTERVAL_MIN
from keyboards import (
    CB_MAIN, CB_POST_MENU, CB_AUTO_MENU, CB_TZ_MENU,
    CB_SIG_SHOW, CB_AUTO_INTERVAL_SHOW, CB_AUTO_TEXT_SHOW, CB_TZ_SHOW,
    CB_AUTO_SEND_RESET, CB_AUTO_STOP,
    kb_main, kb_post_menu, kb_auto_menu, kb_tz_menu, kb_back_main
)
import jobs


async def show_main_menu(update: Update, text: str = "منو اصلی:"):
    if update.callback_query:
        q = update.callback_query
        await q.answer()
        await q.edit_message_text(text=text, reply_markup=kb_main())
    else:
        await update.message.reply_text(text, reply_markup=kb_main())


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
