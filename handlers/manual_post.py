# handlers/manual_post.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.signature import get_signature

async def start_manual_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("متن", callback_data="manual_text")],
        [InlineKeyboardButton("عکس", callback_data="manual_photo")],
        [InlineKeyboardButton("ویدیو", callback_data="manual_video")],
        [InlineKeyboardButton("لینک", callback_data="manual_link")],
        [InlineKeyboardButton("مشاهده امضا", callback_data="view_signature")],
        [InlineKeyboardButton("تغییر امضا", callback_data="change_signature")],
    ]
    await update.callback_query.message.reply_text(
        "📌 انتخاب نوع پست دستی:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_manual_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode = context.user_data.get("mode")

    # اینجا می‌تونی حالت‌ها و دریافت پیام کاربر رو مدیریت کنی
    if query:
        data = query.data
        if data == "view_signature":
            sig = get_signature()
            await query.message.reply_text(f"امضای فعلی:\n\n{sig}")
        elif data == "change_signature":
            context.user_data["mode"] = "set_signature"
            await query.message.reply_text("متن امضای جدید را ارسال کن:")
        else:
            context.user_data["mode"] = "new_post"
            await query.message.reply_text(f"حالت {data} انتخاب شد، متن/عکس/لینک را ارسال کن.")

    elif mode == "set_signature" and update.message:
        from handlers.signature import save_signature
        save_signature(update.message.text)
        context.user_data["mode"] = None
        await update.message.reply_text("✅ امضا با موفقیت تغییر کرد.")
