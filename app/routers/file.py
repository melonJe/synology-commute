import pandas as pd
from dateutil.relativedelta import relativedelta
from starlette.responses import HTMLResponse

import config as conf

from peewee import JOIN
from fastapi import Form, APIRouter
from datetime import datetime, timedelta

from app.Exceptions.HttpException import CustomException
from app.helper.db_helper import Commute, Employee
from typing_extensions import Annotated
from typing import Union

from app.helper.security_helper import check_token
from app.helper.sql_helper import where_time
from app.helper.synology_chat_helper import send_message
from app.helper.file_helper import get_excel_file

router = APIRouter(prefix="/api/files", tags=["files"], responses={404: {"description": "Not found"}})


@router.get("/excel/{filename}")
def download_excel_file(filename: str, start_at: Union[str, None] = None, end_at: str = (datetime.utcnow() - timedelta(hours=15)).strftime('%Y%m%d')):
    if not start_at:
        raise CustomException(message=f"`start_at` is required", status_code=400)
    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = (Commute.select(Commute.date.alias('날짜'), employee.c.name.alias('이름'), Commute.come_at.alias('출근'), Commute.leave_at.alias('퇴근'), Commute.location.alias('위치'))
             .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))

    where_time(query, start_at, end_at)

    date_frame = pd.date_range(start=start_at, end=end_at, name="날짜").to_frame(index=False)
    date_frame["요일"] = date_frame['날짜'].dt.strftime('%a')
    date_frame["날짜"] = pd.to_datetime(date_frame['날짜'])

    query_dict = list(query.order_by(Commute.date.asc()).dicts())
    name_set = set(item['이름'] for item in query_dict)
    df_dict = {name: pd.DataFrame([item for item in query_dict if item['이름'] == name]) for name in name_set}

    for key, item in df_dict.items():
        item['날짜'] = pd.to_datetime(item['날짜'])
        df_dict[key] = pd.merge(left=date_frame, right=item, on='날짜', how='outer')
        df_dict[key].sort_values(by='날짜', ascending=True)

    return get_excel_file(filename, df_dict)


@router.get("/csv/{filename}")
def download_csv_file(filename: str, start_at: Union[int, None] = None):
    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = (Commute.select(Commute.date.alias('날짜'), employee.c.name.alias('이름'), Commute.come_at.alias('출근'), Commute.leave_at.alias('퇴근'), Commute.location.alias('위치'))
             .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))

    if start_at:
        now = datetime.utcnow() + timedelta(hours=9)
        query = query.where((Commute.date >= start_at) & (Commute.date < now))

    query_dict = list(query.order_by(Commute.date.asc()).dicts())
    return pd.DataFrame(query_dict).to_csv()

# @router.post("/excel-bot")
# def download_excel_for_bot(token: Annotated[str, Form()], text: Annotated[str, Form()], username: Annotated[str, Form()], user_id: Annotated[int, Form()]):
#     # TODO intercepter 활용하여 모든 API 사용 할 때 DB에 사용자 저장
#     # TODO URL 변경 필요
#     check_token(token, conf.SLASH_EXCEL_TOKEN)
#
#     employee = Employee.get_or_none(employee_id=user_id)
#     if not employee:
#         employee = Employee.create(employee_id=user_id, name=username)
#
#     if not employee.manager:
#         raise CustomException(message='have no control over excel file download', status_code=403)
#
#     parameter = text.strip().split(' ')
#     filename = '_excel.xlsx'
#     if len(parameter) >= 4:
#         filename = '_' + parameter[3] + filename
#     if len(parameter) >= 3:
#         filename = '_' + parameter[2] + filename
#     if len(parameter) >= 2:
#         filename = parameter[1] + filename
#     if len(parameter) == 1:
#         send_message(conf.BOT_COMMUTE_URL, [user_id], file_url=f'{conf.HOST_URL}/employees/record/excel.xlsx')
#         return True
#
#     file_url = ''
#     if len(parameter) >= 2 and parameter[1]:
#         if parameter[1].isdecimal():
#             send_message(conf.BOT_COMMUTE_URL, [user_id],
#                          file_url=f"{conf.HOST_URL}/files/excel/{filename}?month={parameter[1]}")
#             return True
#         else:
#             file_url = f'{conf.HOST_URL}/employees/{parameter[1]}/record/{filename}'
#
#     if len(parameter) >= 3 and parameter[2]:
#         if len(parameter[2]) != 8:
#             raise CustomException(message=f'Invalid formatted `start_at`', status_code=409)
#         file_url = file_url + '%26' + 'start_at=' + parameter[2]
#     if len(parameter) >= 4 and parameter[3]:
#         if len(parameter[3]) != 8:
#             raise CustomException(message=f'Invalid formatted `end_at`', status_code=409)
#         file_url = file_url + '%26' + 'end_at=' + parameter[3]
#     send_message(conf.BOT_COMMUTE_URL, [user_id], file_url=file_url)
#     return True
