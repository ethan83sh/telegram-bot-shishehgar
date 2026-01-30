from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Main
CB_MAIN = "MAIN"

# Post
CB_POST_MENU = "POST_MENU"
CB_POST_TEXT = "POST_TEXT"
CB_POST_PHOTO = "POST_PHOTO"
CB_POST_VIDEO = "POST_VIDEO"
CB_POST_LINK = "POST_LINK"
CB_SIG_SHOW = "SIG_SHOW"
CB_SIG_SET = "SIG_SET"

# Auto
CB_AUTO_MENU = "AUTO_MENU"
CB_AUTO_SEND_RESET = "AUTO_SEND_RESET"
CB_AUTO_STOP = "AUTO_STOP"
CB_AUTO_INTERVAL_SHOW = "AUTO_INTERVAL_SHOW"
CB_AUTO_INTERVAL_SET = "AUTO_INTERVAL_SET"
CB_AUTO_TEXT_SHOW = "AUTO_TEXT_SHOW"
CB_AUTO_TEXT_SET = "AUTO_TEXT_SET"

# Timezone
CB_TZ_MENU = "TZ_MENU"
CB_TZ_SHOW = "TZ_SHOW"
CB_TZ_SET = "TZ_SET"

# Live menu
CB_LIVE_MENU = "LIVE_MENU"
CB_LIVE_NEW = "LIVE_NEW"
CB_LIVE_LIST = "LIVE_LIST"

# Live list navigation
# LIVE_LIST:idx:<n>
# Live item ops:
# LIVE_DEL:<id>
# LIVE_EDIT:<id>
# LIVE_EDIT_FIELD:<id>:<field>

def kb_back_main():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ بازگشت به منو اصلی", callback_data=CB_MAIN)]])

def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 ارسال پست", callback_data=CB_POST_MENU)],
        [InlineKeyboardButton("⏱ پست خودکار", callback_data=CB_AUTO_MENU)],
        [InlineKeyboardButton("🔴 پست لایو", callback_data=CB_LIVE_MENU)],
        [InlineKeyboardButton("🕒 تایم‌زون", callback_data=CB_TZ_MENU)],
    ])

def kb_post_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 پست متنی", callback_data=CB_POST_TEXT)],
        [InlineKeyboardButton("🖼 پست عکس", callback_data=CB_POST_PHOTO)],
        [InlineKeyboardButton("🎞 پست ویدیو", callback_data=CB_POST_VIDEO)],
        [InlineKeyboardButton("🔗 پست لینک", callback_data=CB_POST_LINK)],
        [InlineKeyboardButton("👁 مشاهده امضا", callback_data=CB_SIG_SHOW)],
        [InlineKeyboardButton("✏️ تغییر امضا", callback_data=CB_SIG_SET)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=CB_MAIN)],
    ])

def kb_auto_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 ارسال خودکار (ریست از الان + ارسال فوری)", callback_data=CB_AUTO_SEND_RESET)],
        [InlineKeyboardButton("🛑 توقف ارسال خودکار", callback_data=CB_AUTO_STOP)],
        [InlineKeyboardButton("⏲ مشاهده بازه", callback_data=CB_AUTO_INTERVAL_SHOW)],
        [InlineKeyboardButton("✏️ تغییر بازه", callback_data=CB_AUTO_INTERVAL_SET)],
        [InlineKeyboardButton("👁 مشاهده متن خودکار", callback_data=CB_AUTO_TEXT_SHOW)],
        [InlineKeyboardButton("✏️ تغییر متن خودکار", callback_data=CB_AUTO_TEXT_SET)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=CB_MAIN)],
    ])

def kb_tz_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👁 مشاهده زمان‌ها", callback_data=CB_TZ_SHOW)],
        [InlineKeyboardButton("✏️ تغییر تایم‌زون", callback_data=CB_TZ_SET)],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=CB_MAIN)],
    ])

def kb_live_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ارسال لایو جدید", callback_data=CB_LIVE_NEW)],
        [InlineKeyboardButton("📋 مشاهده لایو های پیش رو", callback_data="LIVE_LIST:idx:0")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data=CB_MAIN)],
    ])

def kb_live_nav(idx: int, total: int, live_id: str):
    prev_idx = max(idx - 1, 0)
    next_idx = min(idx + 1, max(total - 1, 0))
    buttons = []
    row = []
    row.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"LIVE_LIST:idx:{prev_idx}"))
    row.append(InlineKeyboardButton(f"{idx+1}/{total}", callback_data="NOP"))
    row.append(InlineKeyboardButton("بعدی ➡️", callback_data=f"LIVE_LIST:idx:{next_idx}"))
    buttons.append(row)

    buttons.append([
        InlineKeyboardButton("🗑 حذف لایو", callback_data=f"LIVE_DEL:{live_id}"),
        InlineKeyboardButton("✏️ تغییر لایو", callback_data=f"LIVE_EDIT:{live_id}"),
    ])
    buttons.append([InlineKeyboardButton("⬅️ بازگشت به منوی لایو", callback_data=CB_LIVE_MENU)])
    return InlineKeyboardMarkup(buttons)

def kb_live_edit_fields(live_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("پوستر", callback_data=f"LIVE_EDIT_FIELD:{live_id}:poster")],
        [InlineKeyboardButton("تیتر", callback_data=f"LIVE_EDIT_FIELD:{live_id}:title")],
        [InlineKeyboardButton("دیسکریپشن", callback_data=f"LIVE_EDIT_FIELD:{live_id}:desc")],
        [InlineKeyboardButton("لینک", callback_data=f"LIVE_EDIT_FIELD:{live_id}:link")],
        [InlineKeyboardButton("زمان (تاریخ/ساعت)", callback_data=f"LIVE_EDIT_FIELD:{live_id}:dt")],
        [InlineKeyboardButton("⬅️ بازگشت به لیست", callback_data="LIVE_LIST:idx:0")],
    ])
