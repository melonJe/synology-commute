import pandas as pd
import config as conf

from peewee import JOIN
from fastapi import Form, APIRouter
from datetime import datetime

from app.Exceptions.HttpException import CustomException
from app.dto.employee_dto import EmployeeDto
from app.helper.db_helper import Commute, Employee
from typing_extensions import Annotated
from dateutil.relativedelta import relativedelta
from typing import Union

from app.helper.security_helper import check_token
from app.helper.synology_chat_helper import send_message
from app.helper.file_helper import get_excel_file

router = APIRouter(prefix="/employees", tags=["employees"], responses={404: {"description": "Not found"}})


@router.get("/")
def get_employees():
    return [employee for employee in Employee.select().dicts()]


@router.get("/{employee_id}")
def get_employee(employee_id: int):
    employee = Employee.get_or_none(employee_id)
    return employee.__data__ if employee else None


@router.post("/{employee_id}")
def update_employee(employee_id: int, data: EmployeeDto):
    try:
        employee = Employee.get_or_none(employee_id)
        if employee:
            employee.name = data.name
            employee.manager = data.manager
            employee.save()
    except Exception:
        raise CustomException(message='failed update employee', status_code=500)
    return True


@router.delete("/{employee_id}")
def delete_employee(employee_id: int):
    try:
        employee = Employee.get(employee_id)
        employee.delete_instance()
    except Exception:
        raise CustomException(message='failed delete employee', status_code=500)
    return True


@router.post("/commute")
def add_commute(token: Annotated[str, Form()], user_id: Annotated[int, Form()], username: Annotated[str, Form()],
                trigger_word: Annotated[str, Form()]):
    check_token(token, conf.OUTGOING_COMMUTE_TOKEN)

    date_time = datetime.utcnow() + relativedelta(hours=9)

    if not Employee.get_or_none(employee_id=user_id):
        Employee.create(employee_id=user_id, name=username)

    try:
        if trigger_word == "출근":
            commute = Commute.get_or_none(employee_id=user_id, date=date_time.date())
            if commute:
                raise CustomException(message=f'already record {str(commute.come_at)}', status_code=409)
            Commute(employee_id=user_id, date=date_time.date(), come_at=date_time.time()).save()
        elif trigger_word == "퇴근":
            commute = Commute.get(employee_id=user_id, date=date_time.date())
            commute.leave_at = date_time.time()
            commute.save()
        send_message(conf.BOT_COMMUTE_URL, [user_id],
                     text=f"{date_time.strftime('%Y-%m-%d %H:%M:%S')} {trigger_word} 기록 되었습니다.")
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(message=str(e), status_code=500)
    return {"username": username, "time": date_time.strftime('%Y-%m-%d %H:%M:%S')}


@router.get("/record/{filename}")
def download_excel_file(filename: str, start_at: Union[str, None] = None, end_at: Union[str, None] = None):
    # TODO token valid

    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = (Commute.select(employee.c.name.alias('이름'), Commute.come_at.alias('출근'), Commute.leave_at.alias('퇴근'),
                            Commute.date.alias('날짜'))
             .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))

    query = where_time(query, start_at, end_at)

    query_dict = list(query.order_by(Commute.date.asc()).dicts())
    name_set = set(item['이름'] for item in query_dict)
    df_dict = {name: pd.DataFrame([item for item in query_dict if item['이름'] == name]) for name in name_set}
    return get_excel_file(filename, df_dict)


@router.get("/{name}/record/{filename}")
def download_excel_file(filename: str, name: Union[str, None] = None,
                        start_at: Union[str, None] = None, end_at: Union[str, None] = None):
    # TODO token valid

    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = (Commute.select(employee.c.name.alias('이름'), Commute.come_at.alias('출근'), Commute.leave_at.alias('퇴근'),
                            Commute.date.alias('날짜'))
             .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))

    query = query.where(
        Commute.employee_id == Employee.select(Employee.employee_id).limit(1).where(Employee.name == name).get())

    query = where_time(query, start_at, end_at)

    query_dict = list(query.order_by(Commute.date.asc()).dicts())
    return get_excel_file(filename, {name: pd.DataFrame(query_dict)})


def where_time(query: any, start_at, end_at):
    if start_at:
        query = query.where(Commute.date >= datetime.strptime(start_at, '%Y%m%d'))
    if end_at:
        query = query.where(Commute.date < datetime.strptime(end_at, '%Y%m%d'))
    if not start_at and not end_at:
        start_at = datetime.now().date().replace(day=1) - relativedelta(months=3)
        query = query.where(Commute.date >= start_at)
    return query
