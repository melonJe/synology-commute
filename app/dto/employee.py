from pydantic import BaseModel


class UpdateEmployeeDto(BaseModel):
    name: str
    manager: bool


class CreateEmployeeDto(UpdateEmployeeDto):
    id: int
