from peewee import fn

from app.helper.db_helper import Commute

last_value = Commute.select(fn.Max(Commute.no))[0].no
next_value = last_value + 1 if last_value else 1
print(next_value)
