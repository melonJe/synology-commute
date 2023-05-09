import time
from datetime import datetime

import schedule
import uvicorn
from fastapi import FastAPI

from app.Exceptions import HttpException
from app.routers import employee, file
from cron import excel_file_download, work_alert, leave_alert

app = FastAPI(debug=True)

app.include_router(employee.router)
app.include_router(file.router)
app.add_exception_handler(HttpException.CustomException, HttpException.custom_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    schedule.every().day.at("08:40").do(work_alert)
    # schedule.every().day.at("09:25").do(alert_late)
    schedule.every().day.at("18:00").do(leave_alert)
    schedule.every().day.at("09:00").do(excel_file_download)
    while True:
        print(datetime.now())
        schedule.run_pending()
        time.sleep(1)