import sqlite3
from telegram import Update
from telegram.ext import ContextTypes

conn = sqlite3.connect("stats.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER)")
conn.commit()

def log_post():
    c.execute("INSERT INTO posts VALUES (NULL)")
    conn.commit()

async def channel_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c.execute("SELECT COUNT(*) FROM posts")
    count = c.fetchone()[0]
    await update.callback_query.message.reply_text(
        f"تعداد کل پست‌ها: {count}"
    )
