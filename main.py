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
from handlers.timezone import show_timezone_menu, handle_timezone_flow

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
async def universal_router(update, context):
    mode = context.user_data.get("mode")

    if mode == "manual_post":
        await handle_manual_flow(update, context)
    elif mode == "auto_post":
        await handle_auto_flow(update, context)
    elif mode == "live_post":
        await handle_live_flow(update, context)
    elif mode == "timezone":
        await handle_timezone_flow(update, context)

# ================= HANDLERS =================
app.add_handler(CommandHandler("start", start))

app.add_handler(CallbackQueryHandler(start_manual_post, pattern="manual_post"))
app.add_handler(CallbackQueryHandler(start_auto_post, pattern="auto_post"))
app.add_handler(CallbackQueryHandler(start_live_post, pattern="live_post"))
app.add_handler(CallbackQueryHandler(show_timezone_menu, pattern="timezone"))

app.add_handler(MessageHandler(filters.ALL, universal_router))

# ================= RUN =================
app.run_polling()
