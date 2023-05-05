import uvicorn
import pandas as pd
import requests
import json
import tempfile
import config as conf
from peewee import JOIN
from io import BytesIO
from fastapi import Form, responses, APIRouter
from datetime import datetime
from app.database.db_Helper import Commute, Employee
from typing_extensions import Annotated
from dateutil.relativedelta import relativedelta
from typing import Union

router = APIRouter(prefix="/api", tags=["api"], responses={404: {"description": "Not found"}})


# app.include_router(user.router)
def send_message(synology_url: str, user_ids: list, payload: dict):
    try:
        payload.update({"user_ids": user_ids})
        requests.post(synology_url, "payload=" + json.dumps(payload))
    except Exception as error:
        print(error)


@router.post("")
def add_commute(token: Annotated[str, Form()], user_id: Annotated[int, Form()], username: Annotated[str, Form()],
                timestamp: Annotated[str, Form()], trigger_word: Annotated[str, Form()]):
    if token != conf.OUTGOING_COMMUTE_TOKEN:
        # TODO exception
        return

    date: datetime = (datetime.fromtimestamp(int(timestamp[:10])) if timestamp else datetime.utcnow())
    date = date + relativedelta(hours=9)

    if Employee.select().where(Employee.employee_id == user_id).count() < 1:
        Employee(employee_id=user_id, name=username).save()

    # TODO try exception
    if trigger_word == "출근":
        # TODO 이미 출근 처리 되었을 때
        Commute(employee_id=user_id, date=date.date(), come_at=date.time()).save()
        pass
    elif trigger_word == "퇴근":
        (Commute.update(leave_at=date.time())
         .where(Commute.employee_id == user_id and Commute.date == date.date())
         .execute())
        pass
    send_message(conf.BOT_COMMUTE_URL, [user_id], {"text": f"{date} {trigger_word} 기록 되었습니다."})
    return {username, date}


@router.get("/download/excel/{filename}")
def get_csv_data(filename: str, month: Union[int, None] = None, username: Union[str, None] = None,
                 start_at: Union[str, None] = None, end_at: Union[str, None] = None):
    # TODO token valid
    if start_at:
        start_at = datetime.strptime(start_at, '%Y%m%d')
    if end_at:
        end_at = datetime.strptime(end_at, '%Y%m%d')

    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = Commute.select(employee.c.name, Commute.come_at, Commute.leave_at, Commute.date) \
        .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER)

    if month:
        now = datetime.utcnow() + relativedelta(hours=9)
        start_at = now.date().replace(day=1) - relativedelta(months=month)
        end_at = now
    if username:
        query = query.where(
            Commute.employee_id == Employee.select(Employee.employee_id).limit(1).where(
                Employee.name == username).get())
    if start_at:
        query = query.where(Commute.date >= start_at)
    if end_at:
        query = query.where(Commute.date <= end_at)
    if not start_at and not end_at:
        start_at = datetime.now().date().replace(day=1) - relativedelta(months=3)
        query = query.where(Commute.date >= start_at)
    print(query)
    df = pd.DataFrame(list(query.dicts()))
    stream = BytesIO()
    df.to_excel(stream, index=False)
    pd.set_option('display.max.colwidth', 10)
    stream.seek(0)
    with tempfile.NamedTemporaryFile(mode="w+b", suffix=".xlsx", delete=False) as temp_file:
        temp_file.write(stream.read())
        return responses.FileResponse(
            temp_file.name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}",
                     "Access-Control-Expose-Headers": "Content-Disposition",
                     }
        )


@router.post("/excel-bot")
def excel_file_for_bot(token: Annotated[str, Form()], text: Annotated[str, Form()], user_id: Annotated[int, Form()]):
    # TODO intercepter 활용하여 모든 API 사용 할 때 DB에 사용자 저장
    # TODO token valid
    # TODO manger일 경우만
    # TODO 입력 값에 대한 valid

    # TODO text.split(' ') + [None] * (4 - len(text.split(' '))) 수정
    parameter = text.split(' ')
    name = start_at = end_at = ''
    filename = '_excel.xlsx'
    if len(parameter) >= 4:
        filename = '_' + parameter[3] + filename
    if len(parameter) >= 3:
        filename = '_' + parameter[2] + filename
    if len(parameter) >= 2:
        filename = parameter[1] + filename

    # TODO 본인? API 사용법
    file_url = f'http://54.180.187.156:59095/download/excel/{filename}?'
    if len(parameter) >= 2 and parameter[1]:
        if parameter[1].isdecimal():
            file_url = file_url + 'month=' + parameter[1]
            send_message(conf.BOT_COMMUTE_URL, [user_id], {"file_url": file_url})
            return True
        else:
            file_url = file_url + 'username=' + parameter[3]
    if len(parameter) >= 3 and parameter[2]:
        if len(parameter[2]) != 8:
            # TODO exception
            return
        file_url = file_url + '&' + 'start_at=' + parameter[2]
    if len(parameter) >= 4 and parameter[3]:
        if len(parameter[3]) != 8:
            # TODO exception
            return
        file_url = file_url + '&' + 'end_at=' + parameter[3]
    send_message(conf.BOT_COMMUTE_URL, [user_id], {"file_url": file_url})
    return True
