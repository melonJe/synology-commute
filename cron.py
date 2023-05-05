import json
import time
import requests
import schedule
import config as conf
from datetime import datetime
from peewee import JOIN
from app.database.db_Helper import Commute, Employee
from dateutil.relativedelta import relativedelta


def work_alert():
    now = datetime.utcnow() + relativedelta(hours=9)
    if now.weekday() in [5, 6]:
        # return
        pass
    requests.post(conf.INCOMING_COMMUTE_URL, "payload=" + json.dumps({"text": f"{now.date()} 출근 보고 부탁드립니다."}))


def leave_alert():
    now = datetime.utcnow() + relativedelta(hours=9)
    if now.weekday() in [5, 6]:
        # return
        pass
    requests.post(conf.INCOMING_COMMUTE_URL, "payload=" + json.dumps({"text": f"{now.date()} 퇴근 보고 부탁드립니다."}))


def alert_late():
    # TODO 대표님 이사님 제외
    now = datetime.utcnow() + relativedelta(hours=9)
    if now.weekday() in [5, 6]:
        return
    commute = (Commute.select(Commute.employee_id, Commute.come_at, Commute.leave_at, Commute.date)
               .where(Commute.date == now.date()))
    predicate = (Employee.employee_id == commute.c.employee_id)
    query = (Employee.select(Employee.employee_id, Employee.name, Employee.manager)
             .join(commute, on=predicate, join_type=JOIN.LEFT_OUTER)
             .where(commute.c.come_at.is_null())
             )

    employee_id_list = [item.employee_id for item in query]
    requests.post(conf.BOT_COMMUTE_URL,
                  "payload=" + json.dumps({"text": f"출근 보고 부탁드립니다.", "user_ids": employee_id_list}))


def excel_file_download():
    now = datetime.utcnow() + relativedelta(hours=9)
    if now.day != 6:
        return
    print('excel_file_download')
    pass


if __name__ == "__main__":
    schedule.every().day.at("08:40").do(work_alert)
    schedule.every().day.at("09:25").do(alert_late)
    schedule.every().day.at("18:00").do(leave_alert)

    schedule.every().day.at("09:00").do(excel_file_download)
    while True:
        print(datetime.now())
        schedule.run_pending()
        time.sleep(1)
