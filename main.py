import os

import uvicorn
import urllib.parse
from fastapi import FastAPI, Body
from datetime import datetime, timedelta
from app.database.db_Helper import Commute
from app.routers import user

app = FastAPI(debug=True)
app.include_router(user.router)


@app.post("/")
def add_commute(message: str = Body()):
    message = query_string_to_dict(message)
    print(message)

    if message.get('token') and message.get('token') != os.getenv('SYNOLGY_TOKEN'):
        return

    if message.get('timestamp'):
        message['timestamp'] = datetime.fromtimestamp(int(message['timestamp'][:-3])) + timedelta(hours=9)
    else:
        message['timestamp'] = datetime.now()

    for parameter in ('username', 'text', 'trigger_word'):
        if not message.get(parameter):
            return
        else:
            message[parameter] = urllib.parse.unquote(message[parameter])

    print(message)
    if message['trigger_word'] == '출근':
        # try 이미 출근 처리 되었을 때
        commute = Commute(username=message['username'], date=message['timestamp'].date(),
                          come_at=message['timestamp'].time())
        commute.save()
    elif message['trigger_word'] == '퇴근':
        commute = Commute.update(leave_at=message['timestamp'].time()).where(
            Commute.username == message['username']
            and Commute.date == message['timestamp'].date()).execute()
    else:
        return

    print(message['username'], message['timestamp'])


def query_string_to_dict(query_string: str):
    result = dict()
    for pair in query_string.split('&'):
        key, value = pair.split("=")
        result[key] = value
    return result


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
