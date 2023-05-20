import config as conf
from fastapi import Form, APIRouter, Depends
from datetime import datetime, timedelta
from app.Exceptions.HttpException import CustomException
from app.dto.employee import CreateEmployeeDto
from app.helper import employee_helper
from app.helper.db_helper import Commute, Employee
from typing_extensions import Annotated
from app.helper.security_helper import check_token, api_key_auth
from app.helper.synology_chat_helper import send_message

router = APIRouter(prefix="/api/commute", tags=["commute"], responses={404: {"description": "Not found"}})


@router.get("", dependencies=[Depends(api_key_auth)])
def get_commutes(start_at: str, end_at: str):
    if len(start_at) != 8:
        raise CustomException(message=f'Invalid formatted `start_at` ex) 20230814', status_code=409)
    start_at = datetime.strptime(start_at, '%Y%m%d')
    if len(end_at) != 8:
        raise CustomException(message=f'Invalid formatted `end_at` ex) 20230814', status_code=409)
    end_at = datetime.strptime(end_at, '%Y%m%d')
    return [commute for commute in Commute.select().where((Commute.date >= start_at) & (Commute.date < end_at)).dicts()]


@router.get("/{employee_id}", dependencies=[Depends(api_key_auth)])
def get_commute(employee_id: int, start_at: str, end_at: str):
    if len(start_at) != 8:
        raise CustomException(message=f'Invalid formatted `start_at`', status_code=409)
    start_at = datetime.strptime(start_at, '%Y%m%d')
    if len(end_at) != 8:
        raise CustomException(message=f'Invalid formatted `end_at`', status_code=409)
    end_at = datetime.strptime(end_at, '%Y%m%d')

    commute = Commute.select().where(
        (Commute.employee_id == employee_id) & (Commute.date >= start_at) & (Commute.date < end_at))
    return [item.__data__ for item in commute] if commute else None


@router.post("/work")
def add_commute(token: Annotated[str, Form()], user_id: Annotated[int, Form()], username: Annotated[str, Form()],
                text: Annotated[str, Form()]):
    location = time = ''
    for item in text.strip().split(' '):
        if item[0] == '@':
            location = item[1:]
        if item[0] == '*':
            time = item[1:]
    print(location, time)
    return
    check_token(token, conf.WORK_TOKEN)

    date_time = datetime.utcnow() + timedelta(hours=9)

    if not Employee.get_or_none(employee_id=user_id):
        Employee.create(employee_id=user_id, name=username)

    commute = Commute.get_or_none(employee_id=user_id, date=date_time.date())

    try:
        if commute:
            send_message(conf.BOT_COMMUTE_URL, [user_id], text=f"이미 출근 기록 되었습니다. {commute.come_at}")
            raise CustomException(message=f'already record {str(commute.come_at)}', status_code=409)
        Commute.create(employee_id=user_id, date=date_time.date(), come_at=date_time.time().replace(microsecond=0))
        send_message(conf.BOT_COMMUTE_URL, [user_id], text=f"{date_time.replace(microsecond=0)} 출근.")
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(message=str(e), status_code=500)
    return {"username": username, "time": date_time.replace(microsecond=0)}


@router.post("/leave")
def add_commute(token: Annotated[str, Form()], user_id: Annotated[int, Form()], username: Annotated[str, Form()]):
    check_token(token, conf.LEAVE_TOKEN)

    date_time = datetime.utcnow() + timedelta(hours=9)

    if not Employee.get_or_none(employee_id=user_id):
        Employee.create(employee_id=user_id, name=username)

    commute = Commute.get_or_none(employee_id=user_id, date=date_time.date())

    try:
        if not commute:
            send_message(conf.BOT_COMMUTE_URL, [user_id], text=f"출근 기록이 없습니다.")
            raise CustomException(message='not exist commute record', status_code=409)
        commute = Commute.get(employee_id=user_id, date=date_time.date())
        commute.leave_at = date_time.time().replace(microsecond=0)
        commute.save()
        send_message(conf.BOT_COMMUTE_URL, [user_id], text=f"{date_time.replace(microsecond=0)} 퇴근.")
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(message=str(e), status_code=500)
    return {"username": username, "time": date_time.replace(microsecond=0)}
