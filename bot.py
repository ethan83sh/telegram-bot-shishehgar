import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.menu import main_menu
from handlers.post_creator import start_new_post, handle_post_flow
from handlers.auto_poster import start_auto
from handlers.stats import channel_stats

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

app = Application.builder().token(TOKEN).build()

async def start(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("کنترل پنل مدیریت محتوا", reply_markup=main_menu())

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(start_new_post, pattern="new_post"))
app.add_handler(CallbackQueryHandler(channel_stats, pattern="stats"))
app.add_handler(MessageHandler(filters.ALL, handle_post_flow))

start_auto(app)
app.run_polling()
