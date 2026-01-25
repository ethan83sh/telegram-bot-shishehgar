# make_session.py
import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# ================= CONFIG =================
API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH"))

# مسیر فایل session که توی ریل وی استفاده میشه
SESSION_FILE = os.getenv("TG_SESSION_PATH", "handlers/bot_session.session")

# ================= FUNCTION =================
async def main():
    print("در حال ساخت session برای Telethon...")

    # از StringSession استفاده می‌کنیم تا session رو داخل فایل ذخیره کنیم
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        # شماره خودت رو وارد کن (تو ریل وی هم میتونه از متغیر محیطی بخونه)
        PHONE = os.getenv("TG_PHONE")
        if not PHONE:
            raise Exception("TG_PHONE تنظیم نشده است. شماره تلگرام رو به صورت +989xxxxxxxx وارد کن.")

        # شروع اتصال و لاگین
        await client.send_code_request(PHONE)
        code = os.getenv("TG_CODE")
        if not code:
            raise Exception("TG_CODE تنظیم نشده است. کد تایید تلگرام را در متغیر محیطی وارد کن.")

        # ورود به حساب
        await client.sign_in(phone=PHONE, code=code)

        # ذخیره session در فایل
        session_str = client.session.save()
        with open(SESSION_FILE, "w") as f:
            f.write(session_str)

        print(f"✅ فایل session ساخته شد و در مسیر {SESSION_FILE} ذخیره شد.")
        print("می‌توانی حالا TG_SESSION_PATH را در ریلی ست کنی و بات را اجرا کنی.")

# ================= RUN =================
if __name__ == "__main__":
    asyncio.run(main())
