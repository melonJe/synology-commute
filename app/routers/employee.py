import pandas as pd
from dateutil.relativedelta import relativedelta
from peewee import JOIN
from fastapi import APIRouter, Depends
from datetime import datetime
from app.Exceptions.HttpException import CustomException
from app.dto.employee import CreateEmployeeDto, UpdateEmployeeDto
from app.helper import employee_helper, sql_helper
from app.helper.db_helper import Commute, Employee
from typing import Union
from app.helper.file_helper import get_excel_file
from app.helper.security_helper import api_key_auth

router = APIRouter(prefix="/api/employees", tags=["employees"], responses={404: {"description": "Not found"}})


@router.get("", dependencies=[Depends(api_key_auth)])
def get_employees():
    return [employee for employee in Employee.select(Employee.employee_id, Employee.name, Employee.manager).dicts()]


@router.get("/{employee_id}", dependencies=[Depends(api_key_auth)])
def get_employee(employee_id: int):
    return employee_helper.get_employee(employee_id)


@router.post("/{employee_id}", dependencies=[Depends(api_key_auth)])
def create_employee(employee_id: int, data: CreateEmployeeDto):
    return employee_helper.create_employee(employee_id, data)


@router.patch("/{employee_id}", dependencies=[Depends(api_key_auth)])
def update_employee(employee_id: int, data: UpdateEmployeeDto):
    return employee_helper.update_employee(employee_id, data)


@router.delete("/{employee_id}", dependencies=[Depends(api_key_auth)])
def delete_employee(employee_id: int):
    return employee_helper.delete_employee(employee_id)


@router.get("/record/{filename}")
def download_record_file(filename: str, start_at: Union[str, None] = None, end_at: Union[str, None] = None):
    # TODO token valid

    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = (Commute.select(employee.c.name.alias('이름'), Commute.come_at.alias('출근'), Commute.leave_at.alias('퇴근'), Commute.date.alias('날짜'))
             .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))

    query = sql_helper.where_time(query, start_at, end_at)

    query_dict = list(query.order_by(Commute.date.asc()).dicts())
    name_set = set(item['이름'] for item in query_dict)
    df_dict = {name: pd.DataFrame([item for item in query_dict if item['이름'] == name]) for name in name_set}
    return get_excel_file(filename, df_dict)


@router.get("/{name}/record/{filename}")
def download_record_file_one_employees(filename: str, name: Union[str, None] = None, start_at: Union[str, None] = None, end_at: Union[str, None] = None):
    # TODO token valid

    employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
    predicate = (Commute.employee_id == employee.c.employee_id)
    query = (Commute.select(employee.c.name.alias('이름'), Commute.come_at.alias('출근'), Commute.leave_at.alias('퇴근'), Commute.date.alias('날짜'))
             .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))

    query = query.where(
        Commute.employee_id == Employee.select(Employee.employee_id).limit(1).where(Employee.name == name).get())

    query = sql_helper.where_time(query, start_at, end_at)

    query_dict = list(query.order_by(Commute.date.asc()).dicts())
    return get_excel_file(filename, {name: pd.DataFrame(query_dict)})
