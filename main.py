# main.py
import os
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from handlers.menu import main_menu
from handlers.manual_post import start_manual_post, handle_manual_flow
from handlers.auto_post import start_auto_post, handle_auto_flow
from handlers.live_post import start_live_post, handle_live_flow
from handlers.scheduled import show_scheduled_lives
from handlers.timezone import start_timezone_post, handle_timezone_flow
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

# ================= JOB QUEUE =================
# بررسی کانال یوتیوب هر 60 ثانیه
app.job_queue.run_repeating(
    check_new_youtube_video,
    interval=60,
    first=10
)

# ================= MESSAGE ROUTER =================
async def universal_message_router(update, context):
    mode = context.user_data.get("mode")

    if mode == "new_post":
        await handle_manual_flow(update, context)
    elif mode == "live_post":
        await handle_live_flow(update, context)
    elif mode == "auto_post":
        await handle_auto_flow(update, context)
    elif mode == "auto_set_interval":
        await handle_auto_flow(update, context)
    elif mode == "auto_set_text":
        await handle_auto_flow(update, context)
    elif mode == "timezone_set":
        await handle_timezone_flow(update, context)

# ================= HANDLERS =================
# دستور /start
app.add_handler(CommandHandler("start", start))

# پست دستی
app.add_handler(CallbackQueryHandler(start_manual_post, pattern="new_post"))

# پست خودکار
app.add_handler(CallbackQueryHandler(start_auto_post, pattern="auto_post"))
app.add_handler(
    CallbackQueryHandler(
        handle_auto_flow,
        pattern="^(auto_view_interval|auto_change_interval|auto_view_text|auto_change_text|auto_start|auto_stop)$"
    )
)

# پست لایو
app.add_handler(CallbackQueryHandler(start_live_post, pattern="live_post"))

# مشاهده لیست لایوهای برنامه‌ریزی شده
app.add_handler(CallbackQueryHandler(show_scheduled_lives, pattern="scheduled_lives"))

# تایم زون
app.add_handler(CallbackQueryHandler(start_timezone_post, pattern="timezone"))
app.add_handler(MessageHandler(filters.ALL, universal_message_router))

# ================= RUN =================
if __name__ == "__main__":
    print("Bot is starting...")
    app.run_polling()
