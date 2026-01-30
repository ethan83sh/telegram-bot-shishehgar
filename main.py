# main.py
import os
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters
from handlers.manual_post import start_manual_post, handle_manual_flow
from handlers.auto_post import start_auto_post, handle_auto_flow
from handlers.live_post import start_live_post, handle_live_flow
from handlers.timezone import start_timezone_post, handle_timezone_flow
from handlers.scheduled import show_scheduled_lives
from handlers.youtube_poster import check_new_youtube_video

# -----------------------------------
# TOKEN
# -----------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not set")

# -----------------------------------
# Application (نسخه جدید بدون Updater)
# -----------------------------------
app = Application.builder().token(BOT_TOKEN).build()

# -----------------------------------
# Handlerها
# -----------------------------------

# Manual Post
app.add_handler(CallbackQueryHandler(start_manual_post, pattern="manual_menu"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_flow))

# Auto Post
app.add_handler(CallbackQueryHandler(start_auto_post, pattern="auto_menu"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_auto_flow))

# Live Post
app.add_handler(CallbackQueryHandler(start_live_post, pattern="live_menu"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_live_flow))

# Timezone Post
app.add_handler(CallbackQueryHandler(start_timezone_post, pattern="timezone_menu"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_timezone_flow))

# Scheduled Lives
app.add_handler(CallbackQueryHandler(show_scheduled_lives, pattern="scheduled_menu"))

# -----------------------------------
# JobQueue
# -----------------------------------
# بررسی یوتیوب هر 60 ثانیه
app.job_queue.run_repeating(check_new_youtube_video, interval=60, first=10)

# -----------------------------------
# اجرای بات
# -----------------------------------
if __name__ == "__main__":
    print("🤖 Bot is starting...")
    app.run_polling()
