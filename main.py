import uvicorn
import pandas as pd
import requests
import json
import tempfile
import configuration as conf
from io import BytesIO
from fastapi import FastAPI, Form, responses
from datetime import datetime
from app.database.db_Helper import Commute, User
from typing_extensions import Annotated
from dateutil.relativedelta import relativedelta
from typing import Union

app = FastAPI(debug=True)


# app.include_router(user.router)
def send_message(synology_url: str, user_ids: list, payload: dict):
    try:
        payload.update({"user_ids": user_ids})
        requests.post(synology_url, "payload=" + json.dumps(payload))
    except Exception as error:
        print(error)


@app.post("/api")
def add_commute(token: Annotated[str, Form()], user_id: Annotated[int, Form()], username: Annotated[str, Form()],
                timestamp: Annotated[str, Form()], trigger_word: Annotated[str, Form()]):
    if token != conf.SYNOLOGY_TOKEN:
        # TODO exception
        return

    date: datetime = (datetime.fromtimestamp(int(timestamp[:-3])) if timestamp else datetime.utcnow())
    date = date + relativedelta(hours=9)

    if User.select().where(User.user_id == user_id).count() < 1:
        user = User(user_id=user_id, username=username)
        user.save()

    # TODO try exception
    if trigger_word == "출근":
        # TODO 이미 출근 처리 되었을 때
        commute = Commute(user_id=user_id, date=date.date(), come_at=date.time())
        commute.save()
        pass
    elif trigger_word == "퇴근":
        (Commute.update(leave_at=date.time())
         .where(Commute.user_id == user_id and Commute.date == date.date())
         .execute())
        pass
    send_message(conf.BOT_URL, [user_id], {"text": f"{date} {trigger_word} 기록 되었습니다."})
    return {username, date}


@app.get("/download/excel/{filename}")
def get_csv_data(filename: str, month: Union[int, None] = None, username: Union[str, None] = None,
                 start_at: Union[str, None] = None, end_at: Union[str, None] = None):
    # TODO token valid
    if start_at:
        start_at = datetime.strptime(start_at, '%Y%m%d')
    if end_at:
        end_at = datetime.strptime(end_at, '%Y%m%d')

    query = Commute.select(Commute.user_id, Commute.come_at, Commute.leave_at, Commute.date)

    if month:
        now = datetime.utcnow() + relativedelta(hours=9)
        start_at = now.date().replace(day=1) - relativedelta(months=month)
        end_at = now
    if username:
        query = query.where(
            Commute.user_id == User.select(User.user_id).limit(1).where(User.username == username).get())
    if start_at:
        query = query.where(Commute.date >= start_at)
    if end_at:
        query = query.where(Commute.date <= end_at)
    if not start_at and not end_at:
        start_at = datetime.now().date().replace(day=1) - relativedelta(months=3)
        query = query.where(Commute.date >= start_at)
    print(query)
    df = pd.DataFrame(list(query.dicts()))
    stream = BytesIO()
    df.to_excel(stream, index=False)
    stream.seek(0)
    with tempfile.NamedTemporaryFile(mode="w+b", suffix=".xlsx", delete=False) as temp_file:
        temp_file.write(stream.read())
        return responses.FileResponse(
            temp_file.name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}",
                     "Access-Control-Expose-Headers": "Content-Disposition",
                     }
        )


@app.post("/excel-bot")
def excel_file_for_bot(token: Annotated[str, Form()], text: Annotated[str, Form()], user_id: Annotated[int, Form()]):
    # TODO intercepter 활용하여 모든 API 사용 할 때 DB에 사용자 저장
    # TODO token valid
    # TODO manger일 경우만
    # TODO 입력 값에 대한 valid

    # TODO text.split(' ') + [None] * (4 - len(text.split(' '))) 수정
    _, username, start_at, end_at = text.split(' ') + [None] * (4 - len(text.split(' ')))
    filename = '_excel.xlsx'
    if end_at:
        filename = '_' + end_at + filename
    if start_at:
        filename = '_' + start_at + filename
    if username:
        filename = username + filename

    # TODO 본인? API 사용법
    file_url = f'http://54.180.187.156:59095/download/excel/{filename}?'
    if username:
        if username.isdecimal():
            file_url = file_url + 'month=' + username
            send_message(conf.BOT_URL, [user_id], {"file_url": file_url})
            return True
        else:
            file_url = file_url + 'username=' + username
    if start_at:
        if len(start_at) != 8:
            # TODO exception
            return
        file_url = file_url + '&' + 'start_at=' + start_at
    if end_at:
        if len(end_at) != 8:
            # TODO exception
            return
        file_url = file_url + '&' + 'end_at=' + end_at
    send_message(conf.BOT_URL, [user_id], {"file_url": file_url})
    return True


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
