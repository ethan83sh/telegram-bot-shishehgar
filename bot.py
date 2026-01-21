import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8522183948:AAGG4Xu0Z08bNatNACjqZnWOvrGKV_gsIMQ"

ADMIN_IDS = [40012360]
PRIVATE_GROUP_ID = -1001317486268
TARGET_CHANNEL_ID = -10013065291690

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except:
        cfg = {
            "interval_hours": 1,
            "auto_msgs": ["📢 تکراری 1", "📢 تکراری 2"],
            "banned_words": ["spam", "تبلیغ"]
        }
    
    # auto_interval رو همیشه بساز
    cfg["auto_interval"] = cfg["interval_hours"] * 3600
    return cfg

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

config = load_config()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀\n/admin")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        return await update.message.reply_text("❌")
    
    keyboard = [
        [InlineKeyboardButton("⏰", callback_data="set_interval")],
        [InlineKeyboardButton("📝1", callback_data="msg1")],
        [InlineKeyboardButton("📝2", callback_data="msg2")],
        [InlineKeyboardButton("🚫", callback_data="banned")],
        [InlineKeyboardButton("✅", callback_data="save")]
    ]
    text = f"""تنظیمات:
⏰: {config['interval_hours']}س
1: {config['auto_msgs'][0][:20]}...
2: {config['auto_msgs'][1][:20]}...
🚫: {', '.join(config['banned_words'])}"""
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "set_interval":
        context.user_data['edit'] = 'interval'
        await query.message.reply_text(f"ساعت: {config['interval_hours']}")
    elif query.data == "msg1":
        context.user_data['edit'] = 'msg1'
        await query.message.reply_text(f"1: {config['auto_msgs'][0]}")
    elif query.data == "msg2":
        context.user_data['edit'] = 'msg2'
        await query.message.reply_text(f"2: {config['auto_msgs'][1]}")
    elif query.data == "banned":
        context.user_data['edit'] = 'banned'
        await query.message.reply_text(f"🚫: {', '.join(config['banned_words'])}")
    elif query.data == "save":
        save_config(config)
        await query.edit_message_text("✅ ذخیره!")
    else:
        await query.answer()

async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'edit' not in context.user_data:
        return
    
    key = context.user_data.pop('edit')
    text = update.message.text.strip()
    
    if key == 'interval':
        try:
            hours = int(text)
            config['interval_hours'] = hours
            config['auto_interval'] = hours * 3600
            await update.message.reply_text(f"✅ {hours}س")
        except:
            await update.message.reply_text("❌ عدد!")
    elif key == 'msg1':
        config['auto_msgs'][0] = text
        await update.message.reply_text("✅1")
    elif key == 'msg2':
        config['auto_msgs'][1] = text
        await update.message.reply_text("✅2")
    elif key == 'banned':
        config['banned_words'] = [w.strip() for w in text.split(',') if w.strip()]
        await update.message.reply_text("✅🚫")
    
    await update.message.reply_text("/admin")

async def manage_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").lower()
    if any(word in text for word in config['banned_words']):
        try:
            await update.message.delete()
        except:
            pass

async def private_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id != PRIVATE_GROUP_ID:
        return
    formatted = f"📰 {update.message.text}\n#کانال"
    try:
        await context.bot.send_message(TARGET_CHANNEL_ID, formatted)
        await update.message.reply_text("✅")
    except Exception as e:
        await update.message.reply_text(f"❌{e}")

async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    for msg in config['auto_msgs']:
        try:
            await context.bot.send_message(TARGET_CHANNEL_ID, msg)
        except:
            pass

def main():
    global config
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manage_messages))
    app.add_handler(MessageHandler(filters.Chat(PRIVATE_GROUP_ID), private_to_channel))
    
    job_queue = app.job_queue
    job_queue.run_repeating(auto_post, interval=config['auto_interval'], first=30)

    print("🚀 OK!")
    app.run_polling()

if __name__ == "__main__":
    main()
