import uvicorn
from fastapi import FastAPI

from app.Exceptions import HttpException
from app.helper.db_helper import Employee, Commute
from app.routers import employee, file

app = FastAPI(debug=True)

app.include_router(employee.router)
app.include_router(file.router)
app.add_exception_handler(HttpException.CustomException, HttpException.custom_exception_handler)

if __name__ == "__main__":
    Employee.create_table()
    Commute.create_table()
    uvicorn.run(app, host="0.0.0.0", port=8000)
