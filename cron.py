import json
import os
import time
import requests
import schedule
from datetime import datetime
from dotenv import load_dotenv
from peewee import JOIN

from app.database.db_Helper import Commute, User

load_dotenv()


def alert():
    now = datetime.now()
    if now.weekday() in [5, 6]:
        return
    requests.post(
        os.getenv("COMMUTE_CHAT_URL"),
        "payload=" + json.dumps({"text": f"{now.date()} 출근 보고 부탁드립니다."}),
    )


def alert_late():
    now = datetime.now()
    if now.weekday() in [5, 6]:
        return
    commute = (Commute.select(Commute).where(Commute.date == now.date()))
    predicate = (User.user_id == commute.c.user_id)
    query = (
        User.select(User)
        .join(commute, on=predicate, join_type=JOIN.LEFT_OUTER)
        .where(commute.c.come_at.is_null())
    )

    user_id_list = [item.user_id for item in query]

    requests.post(
        os.getenv("BOT_URL"),
        "payload="
        + json.dumps(
            {
                "text": f"{now.date()} 출근 보고 부탁드립니다.",
                "user_ids": user_id_list
            }
        ),
    )


if __name__ == "__main__":
    schedule.every().days.at("08:40").do(alert)
    schedule.every().days.at("09:25").do(alert_late)
    while True:
        schedule.run_pending()
        time.sleep(1)
