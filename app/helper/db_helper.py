from playhouse.signals import pre_save

import config as conf
from peewee import *


class DBHelper(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = PostgresqlDatabase(host=conf.DB_HOST, port=conf.DB_PORT, database=conf.DB_NAME,
                                                  user=conf.DB_USER, password=conf.DB_PASS)
        return cls._instance


class BaseModel(Model):
    class Meta:
        database = DBHelper().db


class Commute(BaseModel):
    no = AutoField(primary_key=True)
    employee_id = IntegerField()
    date = DateField()
    come_at = TimeField()
    leave_at = TimeField()


class Employee(BaseModel):
    employee_id = IntegerField(primary_key=True)
    name = CharField()
    manager = BooleanField(default=False)
