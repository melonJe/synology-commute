import json
import schedule
import requests
import time
from datetime import datetime


def commute():
    now = datetime.now()
    if now.weekday() in [5, 6]:
        return
    requests.post(
        'https://mv-w.com:1112/webapi/entry.cgi?api=SYNO.Chat.External&method=incoming&version=2&token=%22kbBzHLcSleklQKYqWrwsfuDX8KROSFO3ZeTbRuvcexpueVAIgiXwUvKyyW16SBm2%22',
        'payload=' + json.dumps({'text': f'{now.date()} 출근 업무 보고 부탁드립니다.'}))


if __name__ == '__main__':
    schedule.every().days.at("17:22").do(commute)
    # schedule.every().days.at("08:40").do(commute)
    while True:
        schedule.run_pending()
        time.sleep(1)
