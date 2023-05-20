from app.dto.employee import CreateEmployeeDto
from app.helper import employee_helper

user_id = 123123123
username = 'test'
employee_helper.create_employee(user_id, CreateEmployeeDto(id=user_id, name=username, manager=False))
