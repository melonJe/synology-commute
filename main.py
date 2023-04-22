import uvicorn
from datetime import datetime
from fastapi import FastAPI, Body
from pydantic import BaseModel


class Item(BaseModel):
    token: str = ''
    channel_id: str = ''
    channel_name: str = ''
    user_id: str = ''
    username: str = ''
    post_id: str = ''
    timestamp: datetime = datetime.now()
    text: str = ''
    trigger_word: str = ''


app = FastAPI(debug=True)


@app.post("/")
def read_root(message: str = Body()):
    message = query_string_to_dict(message)
    if not message['token'] == 'str':
        return
    
    print(message)
    return message


def query_string_to_dict(query_string: str):
    result = dict()
    for pair in query_string.split('&'):
        key, value = pair.split("=")
        result[key] = value
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
