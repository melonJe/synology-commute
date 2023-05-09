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

router = APIRouter(prefix="/employees", tags=["employees"], responses={404: {"description": "Not found"}})


@router.post("/commute")
def add_commute(token: Annotated[str, Form()], user_id: Annotated[int, Form()], username: Annotated[str, Form()],
                trigger_word: Annotated[str, Form()]):
    check_token(token, conf.OUTGOING_COMMUTE_TOKEN)

    date: datetime.utcnow() + relativedelta(hours=9)

    if Employee.select().where(Employee.employee_id == user_id).count() < 1:
        Employee(employee_id=user_id, name=username).save()

    try:
        if trigger_word == "출근":
            commute = (
                Commute.select(Commute.come_at).where(Commute.employee_id == user_id, Commute.date == date.date()))
            if commute:
                raise CustomException(message=f'already record {str(commute[0].come_at)}', status_code=409)
            del commute
            Commute(employee_id=user_id, date=date.date(), come_at=date.time()).save()
        elif trigger_word == "퇴근":
            (Commute.update(leave_at=date.time())
             .where(Commute.employee_id == user_id and Commute.date == date.date())
             .execute())
        send_message(conf.BOT_COMMUTE_URL, [user_id], text=f"{date} {trigger_word} 기록 되었습니다.")
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(message=str(e), status_code=500)
    return {username, date}


@router.get("/record/{filename}")
def download_excel_file(filename: str, start_at: Union[str, None] = None, end_at: Union[str, None] = None):
    # TODO token valid

    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = (Commute.select(employee.c.name, Commute.come_at, Commute.leave_at, Commute.date)
             .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))

    query = where_time(query, start_at, end_at)

    query_dict = list(query.order_by(Commute.date.asc()).dicts())
    name_set = set(item['name'] for item in query_dict)
    df_dict = {name: pd.DataFrame([item for item in query_dict if item['name'] == name]) for name in name_set}
    return get_excel_file(filename, df_dict)


@router.get("/{name}/record/{filename}")
def download_excel_file(filename: str, name: Union[str, None] = None,
                        start_at: Union[str, None] = None, end_at: Union[str, None] = None):
    # TODO token valid

    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = (Commute.select(employee.c.name, Commute.come_at, Commute.leave_at, Commute.date)
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
