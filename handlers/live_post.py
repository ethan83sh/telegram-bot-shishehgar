# handlers/live_post.py
import os
import json
from datetime import datetime
from pytz import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# مسیر فایل JSON و پوشه ذخیره پوستر
STORAGE_DIR = "storage"
JSON_FILE = os.path.join(STORAGE_DIR, "scheduled_lives.json")

# تایم زون برلین
TZ = timezone("Europe/Berlin")

# اطمینان از وجود پوشه storage
os.makedirs(STORAGE_DIR, exist_ok=True)

# ---------------- UTILS ----------------
def load_lives():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_lives(lives):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(lives, f, ensure_ascii=False, indent=2)

def now_in_tz():
    return datetime.now(TZ)

def format_live(live):
    dt = datetime.fromisoformat(live["datetime"])
    return f"🎬 {live['title']}\n🕒 {dt.strftime('%Y-%m-%d %H:%M')}\n🔗 {live['youtube_link']}"

# ---------------- MENU ----------------
def live_menu():
    keyboard = [
        [InlineKeyboardButton("➕ اضافه کردن لایو", callback_data="live_add")],
        [InlineKeyboardButton("📋 مشاهده لایوها", callback_data="live_list")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------------- START ----------------
async def start_live_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "🤖 مدیریت لایوها:",
        reply_markup=live_menu()
    )

# ---------------- LIST LIVE ----------------
async def show_scheduled_lives(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lives = load_lives()
    if not lives:
        await update.callback_query.message.reply_text("❌ هیچ لایوی برنامه‌ریزی نشده است")
        return

    # مرتب سازی بر اساس تاریخ
    lives_sorted = sorted(lives, key=lambda x: x["datetime"])

    keyboard = []
    text_lines = ["📅 لایوهای برنامه‌ریزی شده:"]
    for live in lives_sorted:
        text_lines.append(format_live(live))
        keyboard.append([
            InlineKeyboardButton(f"✏️ ویرایش {live['title']}", callback_data=f"live_edit_{live['id']}"),
            InlineKeyboardButton(f"🗑 حذف {live['title']}", callback_data=f"live_delete_{live['id']}")
        ])

    await update.callback_query.message.reply_text(
        "\n\n".join(text_lines),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- HANDLER FLOW ----------------
async def handle_live_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # اضافه کردن لایو جدید
    if data == "live_add":
        context.user_data["mode"] = "live_add_title"
        await query.message.reply_text("عنوان لایو جدید را وارد کن:")

    # نمایش لیست
    elif data == "live_list":
        await show_scheduled_lives(update, context)

    # ویرایش یا حذف با id
    elif data.startswith("live_edit_"):
        live_id = int(data.split("_")[-1])
        context.user_data["edit_live_id"] = live_id
        context.user_data["mode"] = "live_edit_title"
        await query.message.reply_text("عنوان جدید لایو را وارد کن:")

    elif data.startswith("live_delete_"):
        live_id = int(data.split("_")[-1])
        lives = load_lives()
        lives = [l for l in lives if l["id"] != live_id]
        save_lives(lives)
        await query.message.reply_text("✅ لایو حذف شد")

    # ورودی‌های متنی
    elif context.user_data.get("mode") == "live_add_title":
        context.user_data["new_live_title"] = update.message.text
        context.user_data["mode"] = "live_add_link"
        await update.message.reply_text("لینک یوتوب لایو را وارد کن:")

    elif context.user_data.get("mode") == "live_add_link":
        context.user_data["new_live_link"] = update.message.text
        context.user_data["mode"] = "live_add_poster"
        await update.message.reply_text("عکس پوستر لایو را ارسال کن:")

    elif context.user_data.get("mode") == "live_edit_title":
        live_id = context.user_data["edit_live_id"]
        new_title = update.message.text
        lives = load_lives()
        for l in lives:
            if l["id"] == live_id:
                l["title"] = new_title
        save_lives(lives)
        context.user_data["mode"] = None
        await update.message.reply_text("✅ عنوان لایو بروزرسانی شد")

    # دریافت عکس پوستر
    elif update.message.photo and context.user_data.get("mode") == "live_add_poster":
        photo = update.message.photo[-1]  # بزرگترین سایز
        file_path = os.path.join(STORAGE_DIR, f"poster_{int(datetime.timestamp(now_in_tz()))}.jpg")
        await photo.get_file().download_to_drive(file_path)

        # ساخت لایو جدید و ذخیره
        lives = load_lives()
        new_id = max([l["id"] for l in lives], default=0) + 1
        new_live = {
            "id": new_id,
            "title": context.user_data["new_live_title"],
            "datetime": now_in_tz().isoformat(),
            "poster": file_path,
            "youtube_link": context.user_data["new_live_link"]
        }
        lives.append(new_live)
        save_lives(lives)

        context.user_data["mode"] = None
        await update.message.reply_text("✅ لایو جدید اضافه شد")
