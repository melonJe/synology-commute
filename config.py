import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
INCOMING_COMMUTE_URL = os.getenv("INCOMING_COMMUTE_URL")
OUTGOING_COMMUTE_TOKEN = os.getenv("OUTGOING_COMMUTE_TOKEN")
BOT_COMMUTE_URL = os.getenv("BOT_COMMUTE_URL")
BOT_COMMUTE_TOKEN = os.getenv("BOT_COMMUTE_TOKEN")
API_URL = os.getenv("API_URL")
SLASH_COMMUTE_TOKEN = os.getenv("SLASH_COMMUTE_TOKEN")
