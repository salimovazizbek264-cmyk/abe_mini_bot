# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "")  # masalan: @abevayn_channel
TIMEZONE = os.getenv("TIMEZONE", "Asia/Tashkent")

# Standart qiymatlar (keyinchalik admin panel orqali database'dagi
# "settings" jadvali orqali o'zgartiriladi)
DEFAULT_START_LIMIT = 1000
DEFAULT_GAME_TIMES = ["10:00", "20:00"]   # HH:MM formatida
GAME_WINDOW_MINUTES = 10                  # o'yin oynasi necha daqiqa ochiq turadi

PRIZE_1 = 3000
PRIZE_2 = 2000
PRIZE_3 = 1000

DB_PATH = "bot.db"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi! .env yoki Railway Variables'ga qo'shing.")
if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID topilmadi! .env yoki Railway Variables'ga qo'shing.")
