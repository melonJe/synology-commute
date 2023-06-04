import json
import time
import traceback

import requests
import schedule
from dateutil.relativedelta import relativedelta

import config as conf
from datetime import datetime, timedelta
from peewee import JOIN
from app.helper.db_helper import Commute, Employee

from app.helper.synology_chat_helper import send_message


def work_alert():
    now = datetime.utcnow() + timedelta(hours=9)
    if now.weekday() in (5, 6):
        return
    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    employee_id_list = [item.employee_id for item in employee]
    employee_id_list = [29]
    if employee_id_list:
        requests.post(conf.BOT_COMMUTE_URL, "payload=" + json.dumps({"text": f"출근 시간 알림", "user_ids": employee_id_list}))


def leave_alert():
    now = datetime.utcnow() + timedelta(hours=9)
    if now.weekday() in (5, 6):
        return
    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    employee_id_list = [item.employee_id for item in employee]
    if employee_id_list:
        requests.post(conf.BOT_COMMUTE_URL, "payload=" + json.dumps({"text": f"{now.date()} 퇴근 시간 알림", "user_ids": employee_id_list}))


def alert_late():
    now = datetime.utcnow() + timedelta(hours=9)
    if now.weekday() in (5, 6):
        return
    commute = (Commute.select().where(Commute.date == now.date()))
    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager).where(~Employee.manager))
    predicate = (Employee.c.employee_id == commute.c.employee_id)
    query = (employee
             .join(commute, on=predicate, join_type=JOIN.LEFT_OUTER)
             .where(commute.c.come_at.is_null())
             )
    employee_id_list = [item.employee_id for item in query]
    if employee_id_list:
        requests.post(conf.BOT_COMMUTE_URL, "payload=" + json.dumps({"text": f"출근 시간 알림", "user_ids": employee_id_list}))


def excel_file_download():
    now = datetime.utcnow() + timedelta(hours=9)
    if now.weekday() == 0 and now.month != (now + timedelta(days=7)).month:
        start_at = now.date().replace(month=1)
    elif now.day == 1:
        start_at = now.date() - relativedelta(months=1)
    else:
        return

    employee = (Employee.select(Employee.employee_id)
                .where(Employee.manager)
                .order_by(Employee.employee_id.asc()))
    recipient = [item.employee_id for item in employee]
    file_url = f'{conf.HOST_URL}/api/files/excel/{start_at.strftime("%Y-%m") + ".xlsx"}?start_at={start_at.strftime("%Y%m%d")}'
    if recipient:
        send_message(conf.BOT_COMMUTE_URL, recipient, file_url=file_url)


if __name__ == "__main__":
    schedule.every().day.at("08:40").do(work_alert)
    schedule.every().day.at("09:25").do(alert_late)
    schedule.every().day.at("18:00").do(leave_alert)
    schedule.every().day.at("09:00").do(excel_file_download)
    while True:
        schedule.run_pending()
        time.sleep(1)
