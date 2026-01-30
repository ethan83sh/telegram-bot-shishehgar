# handlers/auto_post.py
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ================= مسیر فایل‌ها =================
STORAGE_DIR = "storage"
AUTO_TEXT_FILE = os.path.join(STORAGE_DIR, "auto_text.txt")
SIGNATURE_FILE = os.path.join(STORAGE_DIR, "signature.txt")
JSON_FILE = os.path.join(STORAGE_DIR, "auto_settings.json")

# ================= بارگذاری دیفالت =================
def load_default_text():
    if os.path.exists(AUTO_TEXT_FILE):
        with open(AUTO_TEXT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "این یک پست خودکار است"

def load_default_signature():
    if os.path.exists(SIGNATURE_FILE):
        with open(SIGNATURE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "@YourChannel"

# ================= بارگذاری و ذخیره JSON =================
def load_settings():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # اگر فایل وجود نداشت → استفاده از دیفالت و ساخت JSON
    settings = {
        "interval": 13 * 60,  # پیش‌فرض 13 ساعت
        "text": load_default_text(),
        "signature": load_default_signature(),
        "active": False
    }
    save_settings(settings)
    return settings

def save_settings(settings):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

# ================= منوی پست خودکار =================
def auto_menu():
    keyboard = [
        [InlineKeyboardButton("⏱ مشاهده بازه زمانی", callback_data="auto_view_interval")],
        [InlineKeyboardButton("✏️ تغییر بازه زمانی", callback_data="auto_change_interval")],
        [InlineKeyboardButton("📝 مشاهده متن پست", callback_data="auto_view_text")],
        [InlineKeyboardButton("✍️ تغییر متن پست", callback_data="auto_change_text")],
        [InlineKeyboardButton("🖋 مشاهده امضا", callback_data="auto_view_signature")],
        [InlineKeyboardButton("✏️ تغییر امضا", callback_data="auto_change_signature")],
        [InlineKeyboardButton("▶️ ارسال پست خودکار", callback_data="auto_start")],
        [InlineKeyboardButton("⛔ توقف ارسال خودکار", callback_data="auto_stop")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ================= شروع منو =================
async def start_auto_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "🤖 مدیریت پست خودکار:",
        reply_markup=auto_menu()
    )

# ================= هندلر اصلی =================
async def handle_auto_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = load_settings()
    query = update.callback_query
    data = query.data if query else None

    # مشاهده بازه
    if data == "auto_view_interval":
        await query.message.reply_text(f"⏱ بازه فعلی: {settings['interval']} دقیقه")

    # تغییر بازه
    elif data == "auto_change_interval":
        context.user_data["mode"] = "auto_set_interval"
        await query.message.reply_text("عدد بازه جدید را بر حسب دقیقه وارد کن:")

    # مشاهده متن
    elif data == "auto_view_text":
        await query.message.reply_text(f"📝 متن فعلی:\n\n{settings['text']}")

    # تغییر متن
    elif data == "auto_change_text":
        context.user_data["mode"] = "auto_set_text"
        await query.message.reply_text("متن جدید پست خودکار را ارسال کن:")

    # مشاهده امضا
    elif data == "auto_view_signature":
        await query.message.reply_text(f"🖋 امضای فعلی:\n\n{settings['signature']}")

    # تغییر امضا
    elif data == "auto_change_signature":
        context.user_data["mode"] = "auto_set_signature"
        await query.message.reply_text("امضای جدید را ارسال کن:")

    # شروع ارسال خودکار
    elif data == "auto_start":
        settings["active"] = True
        save_settings(settings)
        await query.message.reply_text("▶️ ارسال خودکار فعال شد (تایمر ریست شد)")

    # توقف ارسال خودکار
    elif data == "auto_stop":
        settings["active"] = False
        save_settings(settings)
        await query.message.reply_text("⛔ ارسال خودکار متوقف شد")

    # ورودی عدد بازه
    elif context.user_data.get("mode") == "auto_set_interval":
        try:
            minutes = int(update.message.text)
            settings["interval"] = minutes
            save_settings(settings)
            context.user_data["mode"] = None
            await update.message.reply_text(f"✅ بازه جدید ثبت شد: {minutes} دقیقه")
        except:
            await update.message.reply_text("❌ فقط عدد وارد کن")

    # ورودی متن
    elif context.user_data.get("mode") == "auto_set_text":
        settings["text"] = update.message.text
        save_settings(settings)
        context.user_data["mode"] = None
        await update.message.reply_text("✅ متن جدید ثبت شد")

    # ورودی امضا
    elif context.user_data.get("mode") == "auto_set_signature":
        settings["signature"] = update.message.text
        save_settings(settings)
        context.user_data["mode"] = None
        await update.message.reply_text("✅ امضای جدید ثبت شد")

# ================= دریافت متن کامل پست =================
def get_auto_post_text():
    settings = load_settings()
    return f"{settings['text']}\n\n{settings['signature']}"
