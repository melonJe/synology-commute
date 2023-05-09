import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
INCOMING_COMMUTE_URL = os.getenv("INCOMING_COMMUTE_URL")
OUTGOING_COMMUTE_TOKEN = list(map(str.strip, os.getenv("OUTGOING_COMMUTE_TOKEN").split(','))) if os.getenv("OUTGOING_COMMUTE_TOKEN") else None
BOT_COMMUTE_URL = os.getenv("BOT_COMMUTE_URL")
BOT_COMMUTE_TOKEN = os.getenv("BOT_COMMUTE_TOKEN")
HOST_URL = os.getenv("HOST_URL")
SLASH_COMMUTE_TOKEN = list(map(str.strip, os.getenv("SLASH_COMMUTE_TOKEN").split(','))) if os.getenv("SLASH_COMMUTE_TOKEN") else None
MANAGER = list(map(str.strip, os.getenv("MANAGER").split(','))) if os.getenv("MANAGER") else None