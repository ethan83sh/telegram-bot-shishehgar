# keyboards.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

CB_MAIN = "MAIN"

CB_POST_MENU = "POST_MENU"
CB_POST_TEXT = "POST_TEXT"
CB_POST_PHOTO = "POST_PHOTO"
CB_POST_VIDEO = "POST_VIDEO"
CB_POST_LINK = "POST_LINK"
CB_SIG_SHOW = "SIG_SHOW"
CB_SIG_SET = "SIG_SET"

CB_AUTO_MENU = "AUTO_MENU"
CB_AUTO_SEND_RESET = "AUTO_SEND_RESET"
CB_AUTO_STOP = "AUTO_STOP"
CB_AUTO_INTERVAL_SHOW = "AUTO_INTERVAL_SHOW"
CB_AUTO_INTERVAL_SET = "AUTO_INTERVAL_SET"
CB_AUTO_TEXT_SHOW = "AUTO_TEXT_SHOW"
CB_AUTO_TEXT_SET = "AUTO_TEXT_SET"

CB_LIVE_START = "LIVE_START"

CB_TZ_MENU = "TZ_MENU"
CB_TZ_SHOW = "TZ_SHOW"
CB_TZ_SET = "TZ_SET"


def kb_back_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ بازگشت به منو اصلی", callback_data=CB_MAIN)]])

def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 ارسال پست", callback_data=CB_POST_MENU)],
        [InlineKeyboardButton("⏱ پست خودکار", callback_data=CB_AUTO_MENU)],
        [InlineKeyboardButton("🔴 پست لایو", callback_data=CB_LIVE_START)],
        [InlineKeyboardButton("🕒 تایم‌زون", callback_data=CB_TZ_MENU)],
    ])

def kb_post_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 پست متنی", callback_data=CB_POST_TEXT)],
        [InlineKeyboardButton("🖼 پست عکس", callback_data=CB_POST_PHOTO)],
        [InlineKeyboardButton("🎞 پست ویدیو", callback_data=CB_POST_VIDEO)],
        [InlineKeyboardButton("🔗 پست لینک", callback_data=CB_POST_LINK)],
        [InlineKeyboardButton("👁 مشاهده امضا", callback_data=CB_SIG_SHOW)],
        [InlineKeyboardButton("✏️ تغییر امضا", callback_data=CB_SIG_SET)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=CB_MAIN)],
    ])

def kb_auto_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 ارسال خودکار (ریست از الان + ارسال فوری)", callback_data=CB_AUTO_SEND_RESET)],
        [InlineKeyboardButton("🛑 توقف ارسال خودکار", callback_data=CB_AUTO_STOP)],
        [InlineKeyboardButton("⏲ مشاهده بازه", callback_data=CB_AUTO_INTERVAL_SHOW)],
        [InlineKeyboardButton("✏️ تغییر بازه", callback_data=CB_AUTO_INTERVAL_SET)],
        [InlineKeyboardButton("👁 مشاهده متن خودکار", callback_data=CB_AUTO_TEXT_SHOW)],
        [InlineKeyboardButton("✏️ تغییر متن خودکار", callback_data=CB_AUTO_TEXT_SET)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=CB_MAIN)],
    ])

def kb_tz_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👁 مشاهده زمان‌ها", callback_data=CB_TZ_SHOW)],
        [InlineKeyboardButton("✏️ تغییر تایم‌زون", callback_data=CB_TZ_SET)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=CB_MAIN)],
    ])
