import json, time, os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN", "8522183948:AAGG4Xu0Z08bNatNACjqZnWOvrGKV_gsIMQ")

ADMIN_IDS = [40012360]
PRIVATE_GROUP_ID = -1001317486268
TARGET_CHANNEL_ID = -10013065291690

CONFIG_FILE = "config.json"
STATS_FILE = "stats.json"

def load_json(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

config = load_json(CONFIG_FILE) or {"interval_hours": 1, "auto_msgs": ["📢 1", "📢 2"], "banned_words": ["spam"]}
stats = load_json(STATS_FILE) or {"messages": {}, "total": 0}

def update_stats(chat_id, text=""):
    day_key = datetime.now().strftime("%Y-%m-%d")
    stats["messages"].setdefault(day_key, {"count": 0, "users": set()})
    stats["messages"][day_key]["count"]
