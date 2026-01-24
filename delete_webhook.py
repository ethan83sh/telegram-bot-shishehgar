import os
import requests

# ================= CONFIG =================
# اگر روی Railway یا هر سرور env variable زدی
TOKEN = os.getenv("BOT_TOKEN")

# اگر نمیخوای از ENV استفاده کنی، مستقیم توکن را بذار:
# TOKEN = "8522183948:AAGSCO9CoH0hJJOR8xpKP4DjDcqqcnS-3eA"

if not TOKEN:
    raise Exception("BOT_TOKEN مشخص نشده! لطفاً متغیر محیطی یا توکن را ست کن.")

# ================= DELETE WEBHOOK =================
url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"

try:
    response = requests.get(url)
    data = response.json()
    if data.get("ok"):
        print("✅ وبهوک با موفقیت حذف شد.")
        print("Response:", data)
    else:
        print("❌ حذف وبهوک موفقیت‌آمیز نبود.")
        print("Response:", data)

except Exception as e:
    print("❌ خطا هنگام حذف وبهوک:", e)
