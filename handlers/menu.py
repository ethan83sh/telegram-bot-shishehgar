# handlers/menu.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [InlineKeyboardButton("📝 پست دستی", callback_data="new_post")],
        [InlineKeyboardButton("🤖 پست خودکار", callback_data="auto_post")],
        [InlineKeyboardButton("🎬 پست لایو", callback_data="live_post")],
        [InlineKeyboardButton("🌐 تایم‌زون", callback_data="timezone")],
        [InlineKeyboardButton("📅 لایوهای برنامه‌ریزی شده", callback_data="scheduled_lives")]
    ]
    return InlineKeyboardMarkup(keyboard)
