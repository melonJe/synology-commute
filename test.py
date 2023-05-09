from datetime import datetime

from dateutil.relativedelta import relativedelta

import config as conf

print((datetime.utcnow() + relativedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S'))