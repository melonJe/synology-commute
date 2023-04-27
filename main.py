import os

import uvicorn
import urllib.parse
import pandas as pd
from io import BytesIO
from fastapi import FastAPI, Body, Depends
from datetime import datetime, timedelta
from starlette.responses import StreamingResponse
from app.database.db_Helper import Commute, BaseModel
from app.routers import user
from typing_extensions import Annotated

app = FastAPI(debug=True)
app.include_router(user.router)


class CommuteDto(BaseModel):
    token: str = ''
    channel_id: int = ''
    channel_name: str = ''
    user_id: str = ''
    username: str = ''
    post_id: int = ''
    time: datetime = datetime.now()
    text: str = ''
    trigger_word: str = ''


async def commute_parameters_parser(message: str = Body()):
    result = dict()
    for pair in message.split('&'):
        key, value = pair.split("=")
        if key == 'timestamp':
            result['date'] = datetime.fromtimestamp(int(value[:-3]))
            continue
        result[key] = value

    for parameter in ('text', 'trigger_word'):
        if not result.get(parameter):
            pass
        else:
            result[parameter] = urllib.parse.unquote(result[parameter])
    return result


@app.post("/api")
def add_commute(message: Annotated[dict, Depends(commute_parameters_parser)]):
    print(message)
    if message['token'] != os.getenv('SYNOLGY_TOKEN'):
        return

    if message['trigger_word'] == '출근':
        # try 이미 출근 처리 되었을 때
        commute = Commute(username=message['username'], date=message['date'].date(), come_at=message['date'].time())
        commute.save()
    elif message['trigger_word'] == '퇴근':
        commute = Commute.update(leave_at=message['date'].time()).where(
            Commute.username == message['username']
            and Commute.date == message['date'].date()).execute()
    else:
        return
    return {message['username'], message['date']}


@app.get("/excel/{filename}")
def get_csv_data(filename: str, ):
    # filename 검증?
    df = pd.DataFrame(
        [["Canada", 10], ["USA", 20]],
        columns=["team", "points"]
    )
    buffer = BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        df.to_excel(writer, index=False)
    return StreamingResponse(
        BytesIO(buffer.getvalue()),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
