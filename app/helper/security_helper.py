import config
from app.Exceptions.HttpException import CustomException
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from typing_extensions import Annotated


def check_token(token: str, valid_token: list):
    if not token:
        raise CustomException(message='Empty token', status_code=401)
    if token not in valid_token:
        raise CustomException(message='Ineligible token', status_code=401)


def api_key_auth(x_api_key: Annotated[str, Header(convert_underscores=True)] = None):
    if not x_api_key:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Empty x-api-key"
        )
    if x_api_key not in config.X_API_KEY:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Ineligible Api Key"
        )
