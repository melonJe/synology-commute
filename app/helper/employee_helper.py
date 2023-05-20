from app.Exceptions.HttpException import CustomException
from app.dto.employee import CreateEmployeeDto, UpdateEmployeeDto
from app.helper.db_helper import Employee


def get_employee(employee_id: int):
    employee = Employee.get_or_none(employee_id)
    return employee.__data__ if employee else None


def create_employee(employee_id: int, data: CreateEmployeeDto):
    try:
        employee = Employee.get_or_none(employee_id)
        if employee:
            raise CustomException(message='Already exists. please use patch method', status_code=409)
        Employee.create(employee_id=data.id, name=data.name, manager=data.manager)
    except CustomException as err:
        raise err
    except Exception:
        raise CustomException(message='failed create employee', status_code=500)
    return True


def update_employee(employee_id: int, data: UpdateEmployeeDto):
    try:
        employee = Employee.get_or_none(employee_id)
        if not employee:
            raise CustomException(message='Not found employee data. please use post method', status_code=000)
        if data.name:
            employee.name = data.name
        if data.manager:
            employee.manager = data.manager
        employee.save()
    except CustomException as err:
        raise err
    except Exception:
        raise CustomException(message='failed update employee', status_code=500)
    return True


def delete_employee(employee_id: int):
    try:
        employee = Employee.get(employee_id)
        employee.delete_instance()
    except CustomException as err:
        raise err
    except Exception:
        raise CustomException(message='failed delete employee', status_code=500)
    return True
