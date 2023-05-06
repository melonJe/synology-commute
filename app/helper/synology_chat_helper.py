import json

import requests


def send_message(synology_url: str, user_ids: list, text=None, file_url=None):
    # print(synology_url, user_ids, text, file_url)
    try:
        payload = {"user_ids": user_ids}
        payload.update({'text': text}) if text else None
        payload.update({'file_url': file_url}) if text else None
        requests.post(synology_url, "payload=" + json.dumps(payload))
    except Exception as error:
        print(error)
