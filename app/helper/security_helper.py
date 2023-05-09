from app.Exceptions.HttpException import CustomException


def check_token(token: str, valid_token: list):
    if not token:
        raise CustomException(message='Empty token', status_code=401)
    if token not in valid_token:
        raise CustomException(message='Ineligible token', status_code=401)
