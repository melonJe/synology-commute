from datetime import datetime, timedelta

import pandas as pd
from dateutil.relativedelta import relativedelta
from peewee import JOIN

from app.helper.db_helper import Employee, Commute

now = datetime.utcnow() + timedelta(hours=9)
start_at = now.date().replace(day=1)

date_frame = pd.date_range(start=start_at, end=now.date(), name="날짜").to_frame(index=False)
date_frame["요일"] = date_frame['날짜'].dt.strftime('%a')
date_frame["날짜"] = pd.to_datetime(date_frame['날짜'])

employee = (Employee.select(Employee.employee_id, Employee.name, Employee.manager))
predicate = (Commute.employee_id == employee.c.employee_id)
query = (Commute.select(Commute.date.alias('날짜'), employee.c.name.alias('이름'), Commute.come_at.alias('출근'), Commute.leave_at.alias('퇴근'), Commute.location.alias('위치'))
         .join(employee, on=predicate, join_type=JOIN.LEFT_OUTER))

if start_at:
    now = datetime.utcnow() + timedelta(hours=9)
    query = query.where((Commute.date >= start_at) & (Commute.date < now))

query_dict = list(query.order_by(Commute.date.asc()).dicts())
name_set = set(item['이름'] for item in query_dict)
df_dict = {name: pd.DataFrame([item for item in query_dict if item['이름'] == name]) for name in name_set}

for key, item in df_dict.items():
    item['날짜'] = pd.to_datetime(item['날짜'])
    df_dict[key] = pd.merge(left=date_frame, right=item, on='날짜', how='outer')
    df_dict[key].sort_values(by='날짜', ascending=True)

print(df_dict)
