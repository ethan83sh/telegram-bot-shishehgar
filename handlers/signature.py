# handlers/signature.py
import os
import json
from telegram import Update
from telegram.ext import ContextTypes

# مسیر فایل ذخیره امضا
SIGNATURE_FILE = "storage/signature.json"

# مقدار پیش‌فرض جدید
DEFAULT_SIGNATURE = "
#شاهزاده_رضا_پهلوی
#انقلاب_شیروخورشید
#ایرانو_پس_میگیریم
#همکاری_ملی
#MIGA
#KingRezaPahlavi

───────────────── 
 ℘ @OfficialRezaPahlavi ℘ 
───────────────── 
 ℘ IranoPasMigirim.com ℘ 
───────────────── 
instagram.com/officialrezapahlavi 
───────────────── 

@Iran_Tajdar
".strip()

# خواندن امضا از فایل json یا بازگشت به پیش‌فرض
def get_signature():
    if os.path.exists(SIGNATURE_FILE):
        try:
            with open(SIGNATURE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("signature", DEFAULT_SIGNATURE)
        except:
            return DEFAULT_SIGNATURE
    return DEFAULT_SIGNATURE

# ذخیره امضا
def set_signature(text: str):
    with open(SIGNATURE_FILE, "w", encoding="utf-8") as f:
        json.dump({"signature": text}, f, ensure_ascii=False, indent=2)

# مشاهده امضا
async def view_signature(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sig = get_signature()
    await update.callback_query.message.reply_text(f"🖊️ امضای فعلی:\n{sig}")

# تغییر امضا
async def change_signature(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "set_signature"
    await update.callback_query.message.reply_text(
        "✍️ لطفاً امضای جدید را ارسال کن:"
    )

# هندلر ورودی امضا
async def handle_signature_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") == "set_signature":
        text = update.message.text
        set_signature(text)
        context.user_data["mode"] = None
        await update.message.reply_text("✅ امضای جدید ذخیره شد")
