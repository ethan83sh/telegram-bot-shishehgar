# handlers/auto_post.py
import os
import json
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, Job

STATUS_FILE = "handlers/auto_post_status.json"

# ================= CONFIG =================
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# بارگذاری وضعیت
def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {"interval": 13*60*60, "text": "متن پیشفرض پست خودکار", "next_send": None, "active": True}

# ذخیره وضعیت
def save_status(data):
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f)

# ================= HANDLERS =================
async def start_auto_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "auto_menu"
    await update.callback_query.message.reply_text(
        "📌 منوی پست خودکار",
        reply_markup=None  # بعداً میشه inline کیبورد اضافه کرد
    )

async def handle_auto_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    status = load_status()

    # مشاهده بازه زمانی
    if mode == "view_interval":
        hours = status["interval"] / 3600
        await update.message.reply_text(f"⏱️ بازه زمانی فعلی: {hours} ساعت")

    # تغییر بازه زمانی
    elif mode == "change_interval":
        try:
            hours = float(update.message.text)
            status["interval"] = int(hours * 3600)
            save_status(status)
            await update.message.reply_text(f"✅ بازه زمانی به {hours} ساعت تغییر کرد")
            context.user_data["mode"] = "auto_menu"
        except:
            await update.message.reply_text("❌ مقدار اشتباه است")

    # مشاهده متن پست خودکار
    elif mode == "view_text":
        await update.message.reply_text(f"📝 متن پست خودکار فعلی:\n{status['text']}")

    # تغییر متن پست خودکار
    elif mode == "change_text":
        status["text"] = update.message.text
        save_status(status)
        await update.message.reply_text("✅ متن پست خودکار تغییر کرد")
        context.user_data["mode"] = "auto_menu"

    # ارسال دستی (ریست تایمر)
    elif mode == "send_now":
        await send_auto_post(context)
        status["next_send"] = (datetime.utcnow() + timedelta(seconds=status["interval"])).isoformat()
        save_status(status)
        context.user_data["mode"] = "auto_menu"
        await update.message.reply_text("✅ پست خودکار ارسال شد و تایمر ریست شد")

    # استاپ
    elif mode == "stop_auto":
        status["active"] = False
        save_status(status)
        context.user_data["mode"] = "auto_menu"
        await update.message.reply_text("⏹️ ارسال خودکار متوقف شد")

# ================= JOB =================
async def send_auto_post(context: ContextTypes.DEFAULT_TYPE):
    status = load_status()
    if not status.get("active", True):
        return

    text = status.get("text", "متن پیشفرض پست خودکار")
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)

    # ریست تایمر بعد از ارسال
    status["next_send"] = (datetime.utcnow() + timedelta(seconds=status["interval"])).isoformat()
    save_status(status)
