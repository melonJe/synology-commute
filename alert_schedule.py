import json
import time
import requests
import schedule
import config as conf
from datetime import datetime
from peewee import JOIN
from app.helper.db_helper import Commute, Employee
from dateutil.relativedelta import relativedelta

from app.helper.synology_chat_helper import send_message


def work_alert():
    now = datetime.utcnow() + relativedelta(hours=9)
    if now.weekday() in [5, 6]:
        return
    for url in conf.INCOMING_COMMUTE_URL:
        requests.post(url, "payload=" + json.dumps({"text": f"{now.date()} 출근 시간 알림."}))


def alert_late():
    now = datetime.utcnow() + relativedelta(hours=9)
    if now.weekday() in [5, 6]:
        return
    commute = (Commute.select(Commute.employee_id, Commute.come_at, Commute.leave_at, Commute.date)
               .where(Commute.date == now.date()))
    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager)
                .where(~ Employee.name.in_(conf.MANAGER)))
    predicate = (Employee.employee_id == commute.c.employee_id)
    query = (employee
             .join(commute, on=predicate, join_type=JOIN.LEFT_OUTER)
             .where(commute.c.come_at.is_null())
             )
    employee_id_list = [item.employee_id for item in query]
    if employee_id_list:
        requests.post(conf.BOT_COMMUTE_URL,
                      "payload=" + json.dumps({"text": f"출근 시간 알림.", "user_ids": employee_id_list}))


def leave_alert():
    now = datetime.utcnow() + relativedelta(hours=9)
    if now.weekday() in [5, 6]:
        return
    for url in conf.INCOMING_COMMUTE_URL:
        requests.post(url, "payload=" + json.dumps({"text": f"{now.date()} 퇴근 시간 알림."}))


def excel_file_download():
    now = datetime.utcnow() + relativedelta(hours=9)
    if now.day != 1:
        return

    employee = (Employee.select(Employee.employee_id).limit(1)
                .where(Employee.manager | (Employee.name.in_(conf.CEO)))
                .order_by(Employee.employee_id.asc())
                .get())
    end_at = now.date().replace(day=1)
    start_at = end_at - relativedelta(months=1)

    file_url = f'{conf.HOST_URL}/excel/months/1/{start_at.strftime("%Y-%m") + ".xlsx"}'
    send_message(conf.BOT_COMMUTE_URL, [employee.employee_id], file_url=file_url)


if __name__ == "__main__":
    schedule.every().day.at("08:40").do(work_alert)
    schedule.every().day.at("09:25").do(alert_late)
    schedule.every().day.at("18:00").do(leave_alert)
    schedule.every().day.at("09:00").do(excel_file_download)
    while True:
        try:
            schedule.run_pending()
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
        time.sleep(1)
