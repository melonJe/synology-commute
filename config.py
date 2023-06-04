import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

WORK_TOKEN = list(map(str.strip, os.getenv("WORK_TOKEN").split(','))) if os.getenv("WORK_TOKEN") else None

LEAVE_TOKEN = list(map(str.strip, os.getenv("LEAVE_TOKEN").split(','))) if os.getenv("LEAVE_TOKEN") else None

BOT_COMMUTE_URL = os.getenv("BOT_COMMUTE_URL")
BOT_COMMUTE_TOKEN = os.getenv("BOT_COMMUTE_TOKEN")
HOST_URL = os.getenv("HOST_URL")

SLASH_EXCEL_TOKEN = list(map(str.strip, os.getenv("SLASH_EXCEL_TOKEN").split(','))) if os.getenv("SLASH_EXCEL_TOKEN") else None

X_API_KEY = list(map(str.strip, os.getenv("X_API_KEY").split(','))) if os.getenv("X_API_KEY") else None
