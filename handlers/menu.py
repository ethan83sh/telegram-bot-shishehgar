# handlers/menu.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [InlineKeyboardButton("✏️ پست دستی", callback_data="manual_post")],
        [InlineKeyboardButton("🤖 پست خودکار", callback_data="auto_post")],
        [InlineKeyboardButton("🎬 لایو", callback_data="live_post")],
        [InlineKeyboardButton("⏰ تایم زون", callback_data="timezone")],
        [InlineKeyboardButton("🖊️ مشاهده / تغییر امضا", callback_data="signature")],
    ]
    return InlineKeyboardMarkup(keyboard)
