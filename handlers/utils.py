# handlers/utils.py
from datetime import datetime
import pytz

# تایم زون دیفالت: برلین آلمان
DEFAULT_TZ = pytz.timezone("Europe/Berlin")

def now_in_tz(tz=DEFAULT_TZ):
    """زمان فعلی در تایم زون مشخص"""
    return datetime.now(tz)

def convert_to_tz(dt, tz=DEFAULT_TZ):
    """تبدیل datetime به تایم زون مشخص"""
    if dt.tzinfo is None:
        # اگر naive بود → تایم زون دیفالت
        dt = tz.localize(dt)
    else:
        dt = dt.astimezone(tz)
    return dt
