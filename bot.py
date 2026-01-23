import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Handlers
from handlers.menu import main_menu
from handlers.auto_poster import start_auto
from handlers.stats import channel_stats


async def universal_message_router(update, context):
    mode = context.user_data.get("mode")

    if mode == "new_post":
        await handle_post_flow(update, context)

    elif mode == "live_post":
        await handle_live_flow(update, context)


TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))


app.add_handler(MessageHandler(filters.ALL, universal_message_router))

app = Application.builder().token(TOKEN).build()

# شروع ربات
async def start(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "پنل مدیریت محتوا",
        reply_markup=main_menu()
    )

# Handlers
app.add_handler(CommandHandler("start", start))

# پست دستی
app.add_handler(CallbackQueryHandler(start_new_post, pattern="new_post"))
app.add_handler(MessageHandler(filters.ALL, handle_post_flow))

# پست خودکار
app.add_handler(CallbackQueryHandler(start_auto, pattern="auto_post"))

# پست لایو
app.add_handler(CallbackQueryHandler(start_live_post, pattern="live_post"))
app.add_handler(MessageHandler(filters.ALL, handle_live_flow))

# آمار
app.add_handler(CallbackQueryHandler(channel_stats, pattern="stats"))

app.run_polling()
