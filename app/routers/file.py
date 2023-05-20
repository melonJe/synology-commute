import pandas as pd
import config as conf

from peewee import JOIN
from fastapi import Form, APIRouter
from datetime import datetime, timedelta

from app.Exceptions.HttpException import CustomException
from app.helper.db_helper import Commute, Employee
from typing_extensions import Annotated
from typing import Union

from app.helper.security_helper import check_token
from app.helper.synology_chat_helper import send_message
from app.helper.file_helper import get_excel_file

# router = APIRouter(prefix="/files", tags=["files"], responses={404: {"description": "Not found"}})

# @router.get("/excel/{filename}")
# def download_excel_file(filename: str, month: Union[int, None] = None):
#     employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
#     predicate = (Commute.employee_id == employee.c.employee_id)
#     query = (Commute.select(employee.c.name.alias('이름'), Commute.come_at.alias('출근'), Commute.leave_at.alias('퇴근'),
#                             Commute.date.alias('날짜'))
#              .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))
#
#     if month:
#         now = datetime.utcnow() + timedelta(hours=9)
#         query = query.where(
#             (Commute.date >= now.date().replace(day=1) - relativedelta(months=month)) & (Commute.date < now))
#
#     query_dict = list(query.order_by(Commute.date.asc()).dicts())
#     name_set = set(item['이름'] for item in query_dict)
#     df_dict = {name: pd.DataFrame([item for item in query_dict if item['이름'] == name]) for name in name_set}
#     return get_excel_file(filename, df_dict)
#
#
# @router.post("/excel-bot")
# def download_excel_for_bot(token: Annotated[str, Form()], text: Annotated[str, Form()],
#                            username: Annotated[str, Form()], user_id: Annotated[int, Form()]):
#     # TODO intercepter 활용하여 모든 API 사용 할 때 DB에 사용자 저장
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
