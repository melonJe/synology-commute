from app.Exceptions.HttpException import CustomException


def check_token(token: str, valid_token: str):
    if not token:
        raise CustomException(message='Empty token', status_code=401)
    if token != valid_token:
        raise CustomException(message='Ineligible token', status_code=401)
