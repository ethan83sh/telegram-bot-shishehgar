# handlers/scheduled.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import json
import os

# مسیر ذخیره‌سازی لایوها
STORAGE_FILE = "storage/scheduled_lives.json"

# ================= مدیریت فایل =================
def load_lives():
    if not os.path.exists(STORAGE_FILE):
        return []
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_lives(lives):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(lives, f, ensure_ascii=False, indent=2)

# ================= منوی لایوها =================
def build_lives_menu(lives):
    keyboard = []
    for i, live in enumerate(lives):
        text = f"{live['date']} {live['time']} - {live['title']}"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"live_{i}")])
    return InlineKeyboardMarkup(keyboard) if keyboard else None

# ================= نمایش لایوهای برنامه‌ریزی شده =================
async def show_scheduled_lives(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lives = load_lives()
    if not lives:
        await update.callback_query.message.reply_text("❌ هیچ لایو برنامه‌ریزی شده‌ای وجود ندارد.")
        return

    keyboard = build_lives_menu(lives)
    await update.callback_query.message.reply_text(
        "📅 لیست لایوهای پیش رو:",
        reply_markup=keyboard
    )

# ================= مدیریت انتخاب لایو =================
async def handle_live_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("live_"):
        index = int(data.split("_")[1])
        lives = load_lives()
        if index >= len(lives):
            await query.message.reply_text("❌ لایو پیدا نشد.")
            return

        live = lives[index]
        keyboard = [
            [InlineKeyboardButton("✏️ ویرایش", callback_data=f"edit_{index}")],
            [InlineKeyboardButton("🗑 حذف", callback_data=f"delete_{index}")]
        ]
        text = (
            f"🎬 لایو انتخاب شده:\n\n"
            f"📌 تیتر: {live['title']}\n"
            f"📅 تاریخ: {live['date']}\n"
            f"⏰ ساعت: {live['time']}\n"
            f"🔗 لینک: {live.get('link', '-')}\n"
            f"🖼️ عکس پوستر: {live.get('image', '-')}"
        )
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # حذف لایو
    elif data.startswith("delete_"):
        index = int(data.split("_")[1])
        lives = load_lives()
        if index < len(lives):
            removed = lives.pop(index)
            save_lives(lives)
            await query.message.reply_text(f"✅ لایو '{removed['title']}' حذف شد.")
        else:
            await query.message.reply_text("❌ لایو پیدا نشد.")

    # ویرایش لایو
    elif data.startswith("edit_"):
        index = int(data.split("_")[1])
        lives = load_lives()
        if index >= len(lives):
            await query.message.reply_text("❌ لایو پیدا نشد.")
            return

        context.user_data["mode"] = "edit_live"
        context.user_data["edit_index"] = index
        await query.message.reply_text(
            "✏️ متن جدید لایو را ارسال کن با فرمت:\n"
            "تیتر | YYYY-MM-DD | HH:MM | لینک | آدرس عکس"
        )

# ================= افزودن یا ویرایش لایو =================
async def handle_live_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if mode not in ["add_live", "edit_live"]:
        return

    text = update.message.text.strip()
    parts = [p.strip() for p in text.split("|")]
    if len(parts) != 5:
        await update.message.reply_text("❌ فرمت اشتباه است. لطفاً طبق دستورالعمل وارد کن.")
        return

    live_data = {
        "title": parts[0],
        "date": parts[1],
        "time": parts[2],
        "link": parts[3],
        "image": parts[4]
    }

    lives = load_lives()
    if mode == "add_live":
        lives.append(live_data)
        await update.message.reply_text(f"✅ لایو '{live_data['title']}' اضافه شد.")
    elif mode == "edit_live":
        index = context.user_data.get("edit_index")
        if index is not None and index < len(lives):
            lives[index] = live_data
            await update.message.reply_text(f"✅ لایو '{live_data['title']}' ویرایش شد.")
        context.user_data["edit_index"] = None

    save_lives(lives)
    context.user_data["mode"] = None

# ================= افزودن لایو جدید (از منو) =================
async def start_add_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "add_live"
    await update.callback_query.message.reply_text(
        "➕ افزودن لایو جدید:\n"
        "لطفاً متن را با فرمت زیر ارسال کن:\n"
        "تیتر | YYYY-MM-DD | HH:MM | لینک | آدرس عکس"
    )
