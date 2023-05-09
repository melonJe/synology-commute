from pydantic import BaseModel


class EmployeeDto(BaseModel):
    name: str
    manager: bool
