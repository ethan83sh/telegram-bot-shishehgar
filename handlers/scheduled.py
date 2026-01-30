# handlers/scheduled.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import json
import os

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

    if not data.startswith("li
