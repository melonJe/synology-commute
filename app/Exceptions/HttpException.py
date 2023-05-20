from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


class CustomException(Exception):
    def __init__(self, message: str, status_code: int):
        self.status_code = status_code
        self.message = message


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )
