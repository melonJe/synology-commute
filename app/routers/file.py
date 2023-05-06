from fastapi import APIRouter
import pandas as pd
import config as conf

from peewee import JOIN
from fastapi import Form, APIRouter
from datetime import datetime

from app.Exceptions.HttpException import CustomException
from app.helper.db_helper import Commute, Employee
from typing_extensions import Annotated
from dateutil.relativedelta import relativedelta
from typing import Union

from app.helper.security_helper import check_token
from app.helper.synology_chat_helper import send_message
from app.service.file import get_excel_file

router = APIRouter(prefix="/files", tags=["files"], responses={404: {"description": "Not found"}})


@router.get("/excel/{filename}")
def download_excel_file(filename: str, username: Union[str, None] = None,
                        start_at: Union[str, None] = None, end_at: Union[str, None] = None):
    # TODO token valid
    if start_at:
        start_at = datetime.strptime(start_at, '%Y%m%d')
    if end_at:
        end_at = datetime.strptime(end_at, '%Y%m%d')

    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = (Commute.select(employee.c.name, Commute.come_at, Commute.leave_at, Commute.date)
             .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))

    if username:
        query = query.where(Commute.employee_id == Employee.select(Employee.employee_id).limit(1).where(
            Employee.name == username).get())
    if start_at:
        query = query.where(Commute.date >= start_at)
    if end_at:
        query = query.where(Commute.date < end_at)
    if not start_at and not end_at:
        start_at = datetime.now().date().replace(day=1) - relativedelta(months=3)
        query = query.where(Commute.date >= start_at)
    query_dict = list(query.order_by(Commute.date.asc()).dicts())
    name_set = set(item['name'] for item in query_dict)
    df_dict = {name: pd.DataFrame([item for item in query_dict if item['name'] == name]) for name in name_set}
    return get_excel_file(filename, df_dict)


@router.get("/excel/months/{month}/{filename}")
def download_excel_file(filename: str, month: Union[int, None] = None):
    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = (Commute.select(employee.c.name, Commute.come_at, Commute.leave_at, Commute.date)
             .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))

    if month:
        now = datetime.utcnow() + relativedelta(hours=9)
        query = query.where(
            (Commute.date >= now.date().replace(day=1) - relativedelta(months=month)) & (Commute.date < now))

    query_dict = list(query.order_by(Commute.date.asc()).dicts())
    name_set = set(item['name'] for item in query_dict)
    df_dict = {name: pd.DataFrame([item for item in query_dict if item['name'] == name]) for name in name_set}
    return get_excel_file(filename, df_dict)


@router.post("/excel-bot")
def download_excel_for_bot(token: Annotated[str, Form()], text: Annotated[str, Form()],
                           user_id: Annotated[int, Form()]):
    # TODO intercepter 활용하여 모든 API 사용 할 때 DB에 사용자 저장

    check_token(token, conf.SLASH_COMMUTE_TOKEN)
    employee = Employee.select(Employee.name).limit(1).where(Employee.employee_id == user_id).get()
    # if employee.name != 'mhkim':
    #     raise CustomException(message='have no control over excel file download', status_code=403)

    # TODO USER, MONTH 로 API 나누기

    parameter = text.split(' ')
    filename = '_excel.xlsx'
    if len(parameter) >= 4:
        filename = '_' + parameter[3] + filename
    if len(parameter) >= 3:
        filename = '_' + parameter[2] + filename
    if len(parameter) >= 2:
        filename = parameter[1] + filename
    if len(parameter) >= 1:
        send_message(conf.BOT_COMMUTE_URL, [user_id], file_url=f'{conf.API_URL}/files/excel/excel.xlsx')
        return True

    file_url = f'{conf.API_URL}/files/excel/{filename}?'
    if len(parameter) >= 2 and parameter[1]:
        if parameter[1].isdecimal():
            send_message(conf.BOT_COMMUTE_URL, [user_id],
                         file_url=f"{conf.API_URL}/excel/months/{parameter[1]}/{filename}")
            return True
        else:
            file_url = file_url + 'username=' + parameter[3]
    if len(parameter) >= 3 and parameter[2]:
        if len(parameter[2]) != 8:
            raise CustomException(message=f'Invalid formatted `start_at`', status_code=409)
        file_url = file_url + '&' + 'start_at=' + parameter[2]
    if len(parameter) >= 4 and parameter[3]:
        if len(parameter[3]) != 8:
            raise CustomException(message=f'Invalid formatted `end_at`', status_code=409)
        file_url = file_url + '&' + 'end_at=' + parameter[3]
    send_message(conf.BOT_COMMUTE_URL, [user_id], file_url=file_url)
    return True
