# handlers/auto_post.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

DEFAULT_INTERVAL = 13 * 60  # 13 ساعت به دقیقه
DEFAULT_TEXT = "این یک پست خودکار است"

auto_settings = {
    "interval": DEFAULT_INTERVAL,
    "text": DEFAULT_TEXT,
    "active": False
}

def auto_menu():
    keyboard = [
        [InlineKeyboardButton("⏱ مشاهده بازه زمانی", callback_data="auto_view_interval")],
        [InlineKeyboardButton("✏️ تغییر بازه زمانی", callback_data="auto_change_interval")],
        [InlineKeyboardButton("📝 مشاهده متن پست", callback_data="auto_view_text")],
        [InlineKeyboardButton("✍️ تغییر متن پست", callback_data="auto_change_text")],
        [InlineKeyboardButton("▶️ ارسال پست خودکار", callback_data="auto_start")],
        [InlineKeyboardButton("⛔ توقف ارسال خودکار", callback_data="auto_stop")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_auto_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "🤖 مدیریت پست خودکار:",
        reply_markup=auto_menu()
    )

async def handle_auto_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        data = query.data
        if data == "auto_view_interval":
            await query.message.reply_text(f"⏱ بازه فعلی: {auto_settings['interval']} دقیقه")
        elif data == "auto_change_interval":
            context.user_data["mode"] = "auto_set_interval"
            await query.message.reply_text("عدد بازه جدید را بر حسب دقیقه وارد کن:")
        elif data == "auto_view_text":
            await query.message.reply_text(f"📝 متن فعلی:\n\n{auto_settings['text']}")
        elif data == "auto_change_text":
            context.user_data["mode"] = "auto_set_text"
            await query.message.reply_text("متن جدید پست خودکار را ارسال کن:")
        elif data == "auto_start":
            auto_settings["active"] = True
            await query.message.reply_text("▶️ ارسال خودکار فعال شد (تایمر ریست شد)")
        elif data == "auto_stop":
            auto_settings["active"] = False
            await query.message.reply_text("⛔ ارسال خودکار متوقف شد")
    else:
        mode = context.user_data.get("mode")
        if mode == "auto_set_interval" and update.message:
            try:
                minutes = int(update.message.text)
                auto_settings["interval"] = minutes
                context.user_data["mode"] = None
                await update.message.reply_text(f"✅ بازه جدید ثبت شد: {minutes} دقیقه")
            except:
                await update.message.reply_text("❌ فقط عدد وارد کن")
        elif mode == "auto_set_text" and update.message:
            auto_settings["text"] = update.message.text
            context.user_data["mode"] = None
            await update.message.reply_text("✅ متن جدید ثبت شد")
