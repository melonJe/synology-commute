import os

import uvicorn
import urllib.parse
from fastapi import FastAPI, Body, Depends
from datetime import datetime, timedelta
from app.database.db_Helper import Commute, BaseModel
from app.routers import user
from typing_extensions import Annotated

app = FastAPI(debug=True)
app.include_router(user.router)


class CommuteDto(BaseModel):
    token: str = ''
    channel_id: str = ''
    channel_name: str = ''
    user_id: str = ''
    username: str = ''
    post_id: str = ''
    time: datetime = datetime.now()
    text: str = ''
    trigger_word: str = ''


async def commute_parameters_parser(message: str = Body()):
    result = dict()
    print(message)
    for pair in message.split('&'):
        key, value = pair.split("=")
        if key == 'timestamp':
            result['date'] = datetime.fromtimestamp(value[:3])
            break
        result[key] = value

    for parameter in ('username', 'text', 'trigger_word'):
        if not result.get(parameter):
            pass
        else:
            result[parameter] = urllib.parse.unquote(result[parameter])
    return result


@app.post("/api")
def add_commute(message: Annotated[CommuteDto, Depends(commute_parameters_parser)]):
    if message.token != os.getenv('SYNOLGY_TOKEN'):
        return

    if message.trigger_word == '출근':
        # try 이미 출근 처리 되었을 때
        commute = Commute(username=message.username, date=message.time.date(), come_at=message.time.time())
        commute.save()
    elif message.trigger_word == '퇴근':
        commute = Commute.update(leave_at=message.time.time()).where(
            Commute.username == message.username
            and Commute.date == message.time.date()).execute()
    else:
        return
    return {message.username, message.time}


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
