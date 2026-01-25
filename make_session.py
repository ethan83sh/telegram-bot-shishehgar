# make_session.py
import os
from telethon import TelegramClient

# ================= CONFIG =================
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH"))
SESSION_FILE = "bot_session.session"  # مسیر فایل session که ساخته می‌شود

# ================= CLIENT =================
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

async def main():
    await client.start()  # از شما شماره و کد تایید را یک‌بار می‌خواهد
    print(f"✅ Session ساخته شد و ذخیره شد: {SESSION_FILE}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
