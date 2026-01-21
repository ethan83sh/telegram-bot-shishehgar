# bot.py - کامل بازنویسی شده برای PythonAnywhere + Telegram Bot
# مناسب برای کانال @E_Shishehgar و اخبار سیاسی ایران

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, abort
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن بات (از متغیر محیطی یا مستقیم)
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8522183948:AAGG4Xu0Z08bNatNACjqZnWOvrGKV_gsIMQ')

# ایجاد اپ Flask
app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# آیدی ادمین‌ها (ID خودت رو اضافه کن)
ADMIN_IDS = [123456789]  # آیدی تلگرام ادمین‌ها رو اینجا بذار

# دیتابیس ساده JSON برای ذخیره کاربران و پیام‌ها
USERS_FILE = 'users.json'
MESSAGES_FILE = 'messages.json'

def load_json(filename, default={}):
    """بارگذاری فایل JSON"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"خطا در بارگذاری {filename}: {e}")
        return default

def save_json(filename, data):
    """ذخیره فایل JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"خطا در ذخیره {filename}: {e}")

# دستور /start
async def start(update: Update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username or "نامشخص"
    
    # اضافه کردن کاربر به دیتابیس
    users = load_json(USERS_FILE)
    if str(user_id) not in users:
        users[str(user_id)] = {
            'username': username,
            'first_join': datetime.now().isoformat(),
            'messages_count': 0
        }
        save_json(USERS_FILE, users)
    
    welcome_msg = """
🤖 به بات خبری @E_Shishehgar خوش آمدید! 🇮🇷

📢 اخبار لحظه‌ای اعتراضات و تحولات سیاسی ایران
🔔 اعلان‌های فوری و گزارش‌های میدانی

دستورات:
/news - آخرین اخبار
/status - وضعیت بات
/help - راهنما
/admin - پنل ادمین (فقط ادمین)

💪 همراه ما باشید!
    """
    await update.message.reply_text(welcome_msg)

# دستور /help
async def help_command(update: Update, context):
    help_text = """
📋 راهنمای استفاده:

/start - شروع بات
/news - آخرین اخبار
/status - آمار بات
/help - نمایش این راهنما
/share - اشتراک‌گذاری بات

🔥 برای اخبار فوری فالو کنید: @E_Shishehgar
    """
    await update.message.reply_text(help_text)

# دستور /status
async def status(update: Update, context):
    users = load_json(USERS_FILE)
    messages = load_json(MESSAGES_FILE)
    
    status_text = f"""
📊 آمار بات (تا {datetime.now().strftime('%Y/%m/%d %H:%M')}):
👥 کاربران: {len(users)}
💬 پیام‌ها: {len(messages)}
⏰ آنلاین از: {datetime.now().strftime('%Y/%m/%d')}
    """
    await update.message.reply_text(status_text)

# دستور /admin (فقط ادمین)
async def admin_panel(update: Update, context):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ دسترسی ندارید!")
        return
    
    keyboard = [
        [InlineKeyboardButton("📤 ارسال پیام همگانی", callback_data='broadcast')],
        [InlineKeyboardButton("📈 آمار کامل", callback_data='full_stats')],
        [InlineKeyboardButton("🧹 پاک کردن دیتا", callback_data='clear_data')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🔧 پنل ادمین:", reply_markup=reply_markup)

# دستور /news (نمونه اخبار)
async def news(update: Update, context):
    news_items = [
        "🔥 گزارش جدید از اعتراضات تهران - ۱۴۰۴/۱۱/۰۱",
        "📰 بیانیه جدید اپوزیسیون - جزئیات کامل",
        "📹 ویدیو میدانی از شیراز - لحظاتی پیش",
        "🌍 واکنش‌های بین‌المللی به تحولات ایران"
    ]
    
    news_text = "📰 آخرین اخبار:\n\n" + "\n".join([f"• {item}" for item in news_items])
    await update.message.reply_text(news_text)

# هندلر پیام‌های عادی (اکو برای تست)
async def echo(update: Update, context):
    user_id = update.effective_user.id
    text = update.message.text
    
    # ذخیره پیام کاربر
    messages = load_json(MESSAGES_FILE)
    messages[str(user_id)] = messages.get(str(user_id), []) + [text]
    save_json(MESSAGES_FILE, messages)
    
    # پاسخ ساده
    await update.message.reply_text(f"📨 دریافت شد: {text[:50]}...")

# هندلر callback query ها
async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'broadcast':
        await query.edit_message_text("📤 در حال توسعه...")
    elif query.data == 'full_stats':
        users = load_json(USERS_FILE)
        stats = f"👥 کل کاربران: {len(users)}\n📱 فعال امروز: {len([u for u in users if 'active_today' in users[u]])}"
        await query.edit_message_text(stats)
    elif query.data == 'clear_data':
        save_json(USERS_FILE, {})
        save_json(MESSAGES_FILE, {})
        await query.edit_message_text("🧹 دیتابیس پاک شد!")

# دستور /share
async def share(update: Update, context):
    share_link = "https://t.me/E_Shishehgar_bot?start=ref"
    await update.message.reply_text(f"🔗 لینک اشتراک:\n{share_link}")

# ثبت هندلرها
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("status", status))
dispatcher.add_handler(CommandHandler("admin", admin_panel))
dispatcher.add_handler(CommandHandler("news", news))
dispatcher.add_handler(CommandHandler("share", share))
dispatcher.add_handler(CallbackQueryHandler(button_callback))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# webhook endpoint
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def index():
    return 'بات @E_Shishehgar فعال است! 🚀'

# اجرای بات
if __name__ == '__main__':
    # برای تست محلی
    logger.info("شروع بات در حالت polling...")
    from telegram.ext import Application
    app = Application.builder().token(TOKEN).build()
    
    # اضافه کردن هندلرها به app
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    # ... بقیه هندلرها
    
    app.run_polling()
    
    # برای PythonAnywhere از gunicorn استفاده کن:
    # gunicorn --bind 0.0.0.0:8000 bot:app
