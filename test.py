import json

import requests

payload = {"user_ids": [29],
           'file_url': 'https://wormhole.app/eeAJl#OAl_Xk3jJEzyVNfpNMKgmw'
           # "attachments": [{"callback_id": "abc", "text": "attachment", "actions":
           #     [{"type": "file", "name": "resp", "value": "ok", "text": "OK", "style": "green"}]}]
           }

requests.post(
    'https://mv-w.com:1112/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token=%22FgCn8D4JRT6wpQqTU9KH6C88oB9QkVtSrLnNCVmO7Bsj8CUsrj3PE7qTJqLN8tmB%22',
    'payload=' + json.dumps(payload))
