# config.py
import os

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
YOUTUBE_CHANELL_ID = os.getenv("YOUTUBE_CHANELL_ID", "")

DEFAULT_TZ = "Europe/Berlin"
DEFAULT_AUTO_INTERVAL_MIN = 13 * 60

DEFAULT_SIGNATURE = "@Iran_Tajdar"

DEFAULT_AUTO_TEXT = """با درود به همراهان گرامی،
اگر به تحلیل‌های خبری، بررسی‌های سیاسی‌اجتماعی، و آشنایی با قانون اساسی علاقه‌مندید، دعوت می‌کنم روزانه مهمان برنامه‌های من باشید:
برای مشاهده تمام راه های ارتباطی با من روی لینک زیر کلیک نمایید
[https://linktr.ee/Shishehgar](https://linktr.ee/Shishehgar)
با تشکر
احسان شیشه گر


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
 
@Iran_Tajdar"""
