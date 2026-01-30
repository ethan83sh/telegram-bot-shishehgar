# handlers/manual_post.py
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.signature import get_signature

# ---------- منوی پست دستی ----------
def manual_menu():
    keyboard = [
        [InlineKeyboardButton("📝 متن", callback_data="manual_text")],
        [InlineKeyboardButton("🖼️ عکس", callback_data="manual_photo")],
        [InlineKeyboardButton("🎬 ویدیو", callback_data="manual_video")],
        [InlineKeyboardButton("🔗 لینک", callback_data="manual_link")],
        [InlineKeyboardButton("🖊 مشاهده امضا", callback_data="view_signature")],
        [InlineKeyboardButton("✍️ تغییر امضا", callback_data="change_signature")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------- شروع پست دستی ----------
async def start_manual_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "📤 مدیریت پست دستی:",
        reply_markup=manual_menu()
    )

# ---------- هندلر اصلی پست دستی ----------
async def handle_manual_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # مشاهده و تغییر امضا
    if data == "view_signature":
        from handlers.signature import view_signature
        await view_signature(update, context)
        return
    elif data == "change_signature":
        from handlers.signature import change_signature
        await change_signature(update, context)
        return

    # تعیین حالت پست
    if data in ["manual_text", "manual_photo", "manual_video", "manual_link"]:
        context.user_data["mode"] = data
        await query.message.reply_text(
            "لطفاً محتوای پست را ارسال کنید:"
        )
        return

    # دریافت محتوا
    mode = context.user_data.get("mode")
    if not mode:
        return

    signature = get_signature()
    text_to_send = ""

    if mode == "manual_text":
        text_to_send = f"{update.message.text}\n\n{signature}"
        await update.message.reply_text(text_to_send)

    elif mode == "manual_photo":
        # عکس از کاربر دریافت می‌شود
        if update.message.photo:
            photo_file = update.message.photo[-1].file_id
            await update.message.reply_photo(photo=photo_file, caption=update.message.caption + f"\n\n{signature}" if update.message.caption else signature)
        else:
            await update.message.reply_text("❌ لطفاً یک عکس ارسال کنید")
            return

    elif mode == "manual_video":
        # ویدیو از کاربر دریافت می‌شود
        if update.message.video:
            video_file = update.message.video.file_id
            await update.message.reply_video(video=video_file, caption=update.message.caption + f"\n\n{signature}" if update.message.caption else signature)
        else:
            await update.message.reply_text("❌ لطفاً یک ویدیو ارسال کنید")
            return

    elif mode == "manual_link":
        text_to_send = f"{update.message.text}\n\n{signature}"
        await update.message.reply_text(text_to_send)

    # پاک کردن حالت پس از ارسال
    context.user_data["mode"] = None
    await update.message.reply_text("✅ پست با موفقیت ارسال شد")
