# main.py
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

import storage
from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID, DEFAULT_TZ, DEFAULT_AUTO_TEXT, DEFAULT_AUTO_INTERVAL_MIN
from keyboards import (
    CB_MAIN, CB_POST_MENU, CB_AUTO_MENU, CB_TZ_MENU,
    CB_SIG_SHOW, CB_AUTO_SEND_RESET, CB_AUTO_STOP,
    CB_AUTO_INTERVAL_SHOW, CB_AUTO_TEXT_SHOW, CB_TZ_SHOW,
)
import menus
import jobs
import conversations


def ensure_defaults():
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
    storage.set_bool("auto_enabled", storage.get_bool("auto_enabled", False))


async def start(update: Update, context):
    if not update.effective_user or update.effective_user.id != ADMIN_ID:
        await update.effective_message.reply_text("⛔️ دسترسی ندارید.")
        return
    ensure_defaults()
    await menus.show_main_menu(update, "✅ ربات آماده است.\nمنو اصلی:")


def build_app() -> Application:
    ensure_defaults()
    if not BOT_TOKEN or not ADMIN_ID or not CHANNEL_ID:
        raise RuntimeError("ENV ناقص است: BOT_TOKEN / ADMIN_ID / CHANNEL_ID را تنظیم کن.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # منو (کلیک‌ها)
    pattern = "^(MAIN|POST_MENU|AUTO_MENU|TZ_MENU|SIG_SHOW|AUTO_SEND_RESET|AUTO_STOP|AUTO_INTERVAL_SHOW|AUTO_TEXT_SHOW|TZ_SHOW)$"
    app.add_handler(CallbackQueryHandler(menus.menu_router, pattern=pattern))

    # ConversationHandlerها را در فایل conversations.py اضافه می‌کنیم (مرحله بعد)
    app.add_handlers(conversations.build_conversations())

    # Job RSS همیشه روشن
    app.job_queue.run_repeating(jobs.youtube_rss_job, interval=60, first=10, name=jobs.YTRSS_JOB_NAME)

    # Restore auto job
    if storage.get_bool("auto_enabled", False):
        interval_min = storage.get_int("auto_interval_minutes", DEFAULT_AUTO_INTERVAL_MIN)
        app.job_queue.run_repeating(jobs.auto_post_job, interval=interval_min * 60, first=interval_min * 60, name=jobs.AUTO_JOB_NAME)

    return app


def main():
    app = build_app()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
