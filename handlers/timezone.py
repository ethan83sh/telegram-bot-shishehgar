# handlers/timezone.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import pytz
import datetime

# ---------- منوی تایم زون ----------
def timezone_menu():
    keyboard = [
        [InlineKeyboardButton("⏱ مشاهده زمان سرور", callback_data="tz_view")],
        [InlineKeyboardButton("✏️ تغییر زمان سرور", callback_data="tz_change")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------- شروع ----------
async def start_timezone_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی تایم زون"""
    await update.callback_query.message.reply_text(
        "🌐 مدیریت زمان سرور:",
        reply_markup=timezone_menu()
    )

# ---------- هندلر اصلی ----------
async def handle_timezone_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # مشاهده زمان فعلی
    if data == "tz_view":
        tz_name = context.user_data.get("timezone", "Europe/Berlin")  # دیفالت برلین
        tz = pytz.timezone(tz_name)
        now = datetime.datetime.now(tz)
        await query.message.reply_text(
            f"⏱ زمان فعلی سرور ({tz_name}): {now.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    # تغییر تایم زون
    elif data == "tz_change":
        context.user_data["mode"] = "set_timezone"
        await query.message.reply_text(
            "نام منطقه زمانی جدید را ارسال کن (مثلاً Europe/Berlin):"
        )

    # دریافت نام تایم زون جدید
    elif context.user_data.get("mode") == "set_timezone":
        tz_name = update.message.text
        try:
            tz = pytz.timezone(tz_name)
            context.user_data["timezone"] = tz_name
            context.user_data["mode"] = None
            await update.message.reply_text(f"✅ تایم زون جدید ثبت شد: {tz_name}")
        except Exception:
            await update.message.reply_text(
                "❌ نام منطقه معتبر نیست، دوباره تلاش کن."
            )
