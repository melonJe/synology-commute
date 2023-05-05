import json
import time
import requests
import schedule
import config as conf
from datetime import datetime
from peewee import JOIN

from app.database.db_Helper import Commute, User


def alert():
    now = datetime.now()
    if now.weekday() in [5, 6]:
        return
    requests.post(conf.INCOMING_COMMUTE_URL, "payload=" + json.dumps({"text": f"{now.date()} 보고 부탁드립니다."}))


def alert_late():
    # TODO 대표님 이사님 제외
    now = datetime.now()
    if now.weekday() in [5, 6]:
        return
    commute = (Commute.select(Commute.user_id, Commute.come_at, Commute.leave_at, Commute.date)
               .where(Commute.date == now.date()))
    predicate = (User.user_id == commute.c.user_id)
    query = (User.select(User.user_id, User.username, User.manager)
             .join(commute, on=predicate, join_type=JOIN.LEFT_OUTER)
             .where(commute.c.come_at.is_null())
             )

    user_id_list = [item.user_id for item in query]
    requests.post(conf.BOT_COMMUTE_URL, "payload=" + json.dumps({"text": f"출근 보고 부탁드립니다.", "user_ids": user_id_list}))


def excel_file_download():
    pass


if __name__ == "__main__":
    schedule.every().day.at("08:40").do(alert)
    schedule.every().day.at("09:25").do(alert_late)
    schedule.every().day.at("18:00").do(alert)
    while True:
        schedule.run_pending()
        time.sleep(1)
