from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ---------- منوی تایم زون ----------
def timezone_menu():
    keyboard = [
        [InlineKeyboardButton("⏱ مشاهده زمان سرور", callback_data="tz_view")],
        [InlineKeyboardButton("✏️ تغییر زمان سرور", callback_data="tz_change")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------- شروع ----------
async def start_timezone_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "🌐 مدیریت زمان سرور:",
        reply_markup=timezone_menu()
    )

# ---------- هندلر اصلی ----------
async def handle_timezone_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "tz_view":
        import pytz, datetime
        tz = pytz.timezone("Europe/Berlin")  # دیفالت برلین
        now = datetime.datetime.now(tz)
        await query.message.reply_text(f"⏱ زمان فعلی سرور: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    elif data == "tz_change":
        context.user_data["mode"] = "set_timezone"
        await query.message.reply_text("نام منطقه زمانی جدید را ارسال کن (مثلاً Europe/Berlin):")
    elif context.user_data.get("mode") == "set_timezone":
        import pytz, datetime
        tz_name = update.message.text
        try:
            tz = pytz.timezone(tz_name)
            context.user_data["timezone"] = tz_name
            context.user_data["mode"] = None
            await update.message.reply_text(f"✅ تایم زون جدید ثبت شد: {tz_name}")
        except:
            await update.message.reply_text("❌ نام منطقه معتبر نیست، دوباره تلاش کن.")
