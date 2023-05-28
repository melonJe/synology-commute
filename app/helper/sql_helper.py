from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from app.helper.db_helper import Commute


def where_time(query: any, start_at, end_at=(datetime.utcnow() + timedelta(hours=9)).strftime('%Y%m%d')):
    if start_at:
        query = query.where(Commute.date >= datetime.strptime(start_at, '%Y%m%d'))
    if end_at:
        query = query.where(Commute.date < datetime.strptime(end_at, '%Y%m%d'))
    if not start_at and not end_at:
        start_at = datetime.now().date().replace(day=1) - relativedelta(months=3)
        query = query.where(Commute.date >= start_at)
    return query
