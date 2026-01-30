# handlers/menu.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("📝 ارسال پست معمولی", callback_data="manual_post"),
        ],
        [
            InlineKeyboardButton("🤖 پست خودکار", callback_data="auto_post"),
        ],
        [
            InlineKeyboardButton("🔴 پست لایو", callback_data="live_post"),
        ],
        [
            InlineKeyboardButton("⏰ تنظیم تایم‌زون", callback_data="timezone"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)

