import config as conf
from fastapi import Form, APIRouter, Depends
from datetime import datetime
from app.Exceptions.HttpException import CustomException
from app.helper.db_helper import Commute, Employee
from typing_extensions import Annotated
from dateutil.relativedelta import relativedelta
from app.helper.security_helper import check_token, api_key_auth
from app.helper.synology_chat_helper import send_message

router = APIRouter(prefix="/commute", tags=["commute"], responses={404: {"description": "Not found"}})


@router.get("", dependencies=[Depends(api_key_auth)])
def get_commutes(start_at: str, end_at: str):
    if len(start_at) != 8:
        raise CustomException(message=f'Invalid formatted `start_at`', status_code=409)
    start_at = datetime.strptime(start_at, '%Y%m%d')
    if len(end_at) != 8:
        raise CustomException(message=f'Invalid formatted `end_at`', status_code=409)
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


@router.post("")
def add_commute(token: Annotated[str, Form()], user_id: Annotated[int, Form()], username: Annotated[str, Form()],
                trigger_word: Annotated[str, Form()]):
    print(conf.OUTGOING_COMMUTE_TOKEN)
    check_token(token, conf.OUTGOING_COMMUTE_TOKEN)

    date_time = datetime.utcnow() + relativedelta(hours=9)

    if not Employee.get_or_none(employee_id=user_id):
        Employee.create(employee_id=user_id, name=username)

    commute = Commute.get_or_none(employee_id=user_id, date=date_time.date())

    try:
        if trigger_word == "출근":
            if commute:
                raise CustomException(message=f'already record {str(commute.come_at)}', status_code=409)
            Commute.create(employee_id=user_id, date=date_time.date(), come_at=date_time.time().replace(microsecond=0))
        elif trigger_word == "퇴근":
            if not commute:
                send_message(conf.BOT_COMMUTE_URL, [user_id], text=f"출근 기록이 없습니다.")
                raise CustomException(message='not exist commute record', status_code=409)
            commute = Commute.get(employee_id=user_id, date=date_time.date())
            commute.leave_at = date_time.time().replace(microsecond=0)
            commute.save()
        send_message(conf.BOT_COMMUTE_URL, [user_id],
                     text=f"{date_time.replace(microsecond=0)} {trigger_word} 기록 되었습니다.")
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(message=str(e), status_code=500)
    return {"username": username, "time": date_time.replace(microsecond=0)}
