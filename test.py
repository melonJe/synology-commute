import json

import requests

from app.database.db_Helper import User

payload = {
    "user_ids": [29],
    # "text": f" 기록이 되었습니다."
    # "file_url": "https://www.synology.com/img/company/branding/synology_logo.jpg"
    "file_url": 'http://54.180.187.156:59095/download/excel/_excel.xlsx?'
    # "attachments": [{"callback_id": "abc", "text": "attachment", "actions":
    #     [{"type": "file", "name": "resp", "value": "ok", "text": "OK", "style": "green"}]}]
}

requests.post(
    "https://mv-w.com:1112/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token=%22FgCn8D4JRT6wpQqTU9KH6C88oB9QkVtSrLnNCVmO7Bsj8CUsrj3PE7qTJqLN8tmB%22",
    "payload=" + json.dumps(payload),
)
print(User.select(User.user_id).limit(1).where(User.username == 'sejeong').get())
