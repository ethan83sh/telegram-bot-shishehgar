# handlers/auto_post.py
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.signature import get_signature

# مسیر فایل ذخیره تنظیمات خودکار
AUTO_FILE = "storage/auto_settings.json"

# ---------- بارگذاری تنظیمات ----------
def load_auto_settings():
    if os.path.exists(AUTO_FILE):
        with open(AUTO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # تنظیمات پیش‌فرض
    return {
        "interval": 13 * 60,  # دقیقه (13 ساعت)
        "text": "این یک پست خودکار است",
        "active": False
    }

# ---------- ذخیره تنظیمات ----------
def save_auto_settings(settings):
    with open(AUTO_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

# ---------- منوی پست خودکار ----------
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

# ---------- شروع ----------
async def start_auto_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "🤖 مدیریت پست خودکار:",
        reply_markup=auto_menu()
    )

# ---------- هندلر اصلی ----------
async def handle_auto_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    settings = load_auto_settings()

    # مشاهده بازه
    if data == "auto_view_interval":
        await query.message.reply_text(f"⏱ بازه فعلی: {settings['interval']} دقیقه")
        return

    # تغییر بازه
    if data == "auto_change_interval":
        context.user_data["mode"] = "auto_set_interval"
        await query.message.reply_text("عدد بازه جدید را بر حسب دقیقه وارد کن:")
        return

    # مشاهده متن
    if data == "auto_view_text":
        await query.message.reply_text(f"📝 متن فعلی:\n\n{settings['text']}")
        return

    # تغییر متن
    if data == "auto_change_text":
        context.user_data["mode"] = "auto_set_text"
        await query.message.reply_text("متن جدید پست خودکار را ارسال کن:")
        return

    # شروع ارسال خودکار
    if data == "auto_start":
        settings["active"] = True
        save_auto_settings(settings)
        await query.message.reply_text("▶️ ارسال خودکار فعال شد (تایمر ریست شد)")
        return

    # توقف ارسال خودکار
    if data == "auto_stop":
        settings["active"] = False
        save_auto_settings(settings)
        await query.message.reply_text("⛔ ارسال خودکار متوقف شد")
        return

    # ---------- دریافت ورودی عدد بازه ----------
    mode = context.user_data.get("mode")
    if mode == "auto_set_interval":
        try:
            minutes = int(update.message.text)
            settings["interval"] = minutes
            save_auto_settings(settings)
            context.user_data["mode"] = None
            await update.message.reply_text(f"✅ بازه جدید ثبت شد: {minutes} دقیقه")
        except:
            await update.message.reply_text("❌ فقط عدد وارد کن")
        return

    # ---------- دریافت متن جدید ----------
    if mode == "auto_set_text":
        settings["text"] = update.message.text
        save_auto_settings(settings)
        context.user_data["mode"] = None
        await update.message.reply_text("✅ متن جدید ثبت شد")
