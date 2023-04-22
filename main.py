import os
import urllib.parse
import uvicorn
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Body
from db.db_Helper import Commute

load_dotenv()

app = FastAPI(debug=True)


@app.post("/")
def read_root(message: str = Body()):
    message = query_string_to_dict(message)
    if message.get('token') and message.get('token') != os.getenv('SYNOLGY_TOKEN'):
        return

    if message.get('timestamp'):
        message['timestamp'] = int(message['timestamp'])
    else:
        message['timestamp'] = int(datetime.timestamp(datetime.now()))

    for parameter in ('username', 'text'):
        if not message.get(parameter):
            return
        else:
            message[parameter] = urllib.parse.unquote(message[parameter])

    print(message)
    if message['text'] == '출근':
        commute = Commute(username=message['username'], date=message['timestamp'] - message['timestamp'] % 86400,
                          come_at=message['timestamp'] % 86400)
        commute.save()
    elif message['text'] == '퇴근':
        commute = Commute.update(leave_at=message['timestamp'] % 86400).where(
            Commute.username == message['username']
            and Commute.date == message['timestamp'] - message['timestamp'] % 86400).execute()
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
    uvicorn.run(app, host="127.0.0.1", port=8000)
