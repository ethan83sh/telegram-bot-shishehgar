# bot.py
import os
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from handlers.menu import main_menu
from handlers.post_creator import start_new_post, handle_post_flow
from handlers.auto_poster import start_auto, handle_auto_menu, handle_auto_flow
from handlers.live_post import start_live_post, handle_live_flow
from handlers.scheduled import show_scheduled_lives
from handlers.stats import channel_stats

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

    if mode == "new_post":
        await handle_post_flow(update, context)
    elif mode == "live_post":
        await handle_live_flow(update, context)
    elif mode == "auto_post":
        await handle_auto_flow(update, context)

# ================= HANDLERS =================
# دستور /start
app.add_handler(CommandHandler("start", start))

# Scheduled live (مشاهده لیست لایوهای برنامه‌ریزی شده)
app.add_handler(CallbackQueryHandler(show_scheduled_lives, pattern="scheduled_lives"))

# پست دستی
app.add_handler(CallbackQueryHandler(start_new_post, pattern="new_post"))

# پست خودکار
app.add_handler(CallbackQueryHandler(start_auto, pattern="auto_post"))
app.add_handler(
    CallbackQueryHandler(
        handle_auto_menu,
        pattern="^(view_interval|change_interval|view_text|change_text|reset_start|stop_auto)$"
    )
)

# پست لایو
app.add_handler(CallbackQueryHandler(start_live_post, pattern="live_post"))

# دکمه‌های منوی آمار
app.add_handler(CallbackQueryHandler(channel_stats, pattern="stats"))


# فقط یک MessageHandler برای همه پیام‌های متنی
app.add_handler(MessageHandler(filters.ALL, universal_message_router))

# ================= RUN =================
app.run_polling()
