import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.auto_poster import start_auto, handle_auto_menu, handle_auto_flow


# Handlers imports
from handlers.menu import main_menu
from handlers.post_creator import start_new_post, handle_post_flow
from handlers.auto_poster import start_auto
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

# ================= ROUTER =================

async def message_router(update, context):
    mode = context.user_data.get("mode")

    if mode == "new_post":
        await handle_post_flow(update, context)

    elif mode == "live_post":
        await handle_live_flow(update, context)

# ================= HANDLERS =================

app.add_handler(CommandHandler("start", start))

app.add_handler(
    CallbackQueryHandler(show_scheduled_lives, pattern="scheduled_lives")
)
app.add_handler(CallbackQueryHandler(start_new_post, pattern="new_post"))
app.add_handler(CallbackQueryHandler(start_auto, pattern="auto_post"))
app.add_handler(CallbackQueryHandler(start_live_post, pattern="live_post"))
app.add_handler(CallbackQueryHandler(channel_stats, pattern="stats"))

# فقط یک MessageHandler
app.add_handler(MessageHandler(filters.ALL, message_router))

# دکمه پست خودکار
app.add_handler(CallbackQueryHandler(start_auto, pattern="auto_post"))

# دکمه‌های منوی Auto Poster
app.add_handler(
    CallbackQueryHandler(handle_auto_menu,
                         pattern="^(view_interval|change_interval|view_text|change_text|reset_start|stop_auto)$")
)

# پیام‌های متنی برای تغییرات
app.add_handler(MessageHandler(filters.ALL, handle_auto_flow))


# ================= RUN =================

app.run_polling()
