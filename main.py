# main.py
import os
import asyncio
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from handlers.menu import main_menu
from handlers.manual_post import start_manual_post, handle_manual_flow
from handlers.auto_post import start_auto_post, handle_auto_flow, get_auto_post_text
from handlers.live_post import start_live_post, handle_live_flow
from handlers.scheduled import show_scheduled_lives
from handlers.youtube_poster import check_new_youtube_video

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not TOKEN:
    raise Exception("BOT_TOKEN not set")

# ================= APP =================
app = Application.builder().token(TOKEN).build()

# ================= START =================
async def start(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "پنل مدیریت محتوا",
        reply_markup=main_menu()
    )

# ================= MESSAGE ROUTER =================
async def universal_message_router(update, context):
    mode = context.user_data.get("mode")
    if mode in ["manual_post_text", "manual_post_photo", "manual_post_video", "manual_post_link"]:
        await handle_manual_flow(update, context)
    elif mode in ["auto_set_interval", "auto_set_text", "auto_set_signature"]:
        await handle_auto_flow(update, context)
    elif mode == "live_post":
        await handle_live_flow(update, context)

# ================= HANDLERS =================
# دستور /start
app.add_handler(CommandHandler("start", start))

# منوهای دستی
app.add_handler(CallbackQueryHandler(start_manual_post, pattern="new_post"))

# منوهای خودکار
app.add_handler(CallbackQueryHandler(start_auto_post, pattern="auto_post"))
app.add_handler(
    CallbackQueryHandler(handle_auto_flow, pattern="^(auto_view_interval|auto_change_interval|auto_view_text|auto_change_text|auto_view_signature|auto_change_signature|auto_start|auto_stop)$")
)

# منوی لایو
app.add_handler(CallbackQueryHandler(start_live_post, pattern="live_post"))

# Scheduled live
app.add_handler(CallbackQueryHandler(show_scheduled_lives, pattern="scheduled_lives"))

# پیام‌ها
app.add_handler(MessageHandler(filters.ALL, universal_message_router))

# ================= JOBS =================
# ---- چک و ارسال خودکار یوتیوب ----
app.job_queue.run_repeating(check_new_youtube_video, interval=60, first=10)

# ---- پست خودکار با تایمر ریست شونده ----
auto_task = {"job": None}  # نگه داشتن Job برای امکان ریست

async def auto_post_job(context):
    from handlers.auto_post import load_settings
    settings = load_settings()
    if settings.get("active"):
        text = get_auto_post_text()
        channel_id = int(os.getenv("CHANNEL_ID"))
        await context.bot.send_message(chat_id=channel_id, text=text)
        print("✅ پست خودکار ارسال شد")

def start_auto_timer(app):
    from handlers.auto_post import load_settings
    settings = load_settings()
    interval = settings.get("interval", 13 * 60)

    # اگر Job قبلی فعال بود حذف می‌کنیم
    if auto_task["job"]:
        auto_task["job"].schedule_removal()

    auto_task["job"] = app.job_queue.run_repeating(
        auto_post_job,
        interval=interval * 60,  # دقیقه → ثانیه
        first=interval * 60  # شروع بعد از interval
    )

# ================= RUN =================
# شروع Job خودکار پس از استارت بات
async def on_startup(app):
    start_auto_timer(app)

app.post_init = on_startup
app.run_polling()
