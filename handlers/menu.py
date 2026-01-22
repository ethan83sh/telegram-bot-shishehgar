from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [InlineKeyboardButton("📤 ارسال پست", callback_data="new_post")],
        [InlineKeyboardButton("⏱ پست خودکار", callback_data="auto_post")],
        [InlineKeyboardButton("📊 آمار", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)
