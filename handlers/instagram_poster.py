# handlers/instagram_poster.py
import os
from instagrapi import Client

INSTAGRAM_USERNAME = os.getenv("IG_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("IG_PASSWORD")

# ایجاد اتصال به اینستاگرام
def get_instagram_client():
    cl = Client()
    cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    return cl

def post_to_instagram(image_path: str, caption: str):
    """
    ارسال پست به اینستاگرام
    :param image_path: مسیر فایل عکس
    :param caption: متن پست
    """
    cl = get_instagram_client()
    cl.photo_upload(image_path, caption)
