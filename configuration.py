import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
SYNOLOGY_TOKEN = os.getenv("SYNOLOGY_TOKEN")
BOT_URL = os.getenv("BOT_URL")
COMMUTE_CHAT_URL = os.getenv("COMMUTE_CHAT_URL")
