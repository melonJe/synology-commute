from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

import config as conf
from app.helper.synology_chat_helper import send_message

now = datetime.utcnow() + timedelta(hours=9)
end_at = now.date().replace(day=1)
start_at = end_at - relativedelta(months=1)

file_url = f'https://webhook.site/d44cb7bb-c61e-42f8-8f76-60437447323f'
send_message(conf.BOT_COMMUTE_URL, [29], file_url=file_url)
