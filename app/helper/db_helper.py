import config as conf
from peewee import *


class DBHelper(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = MySQLDatabase(host=conf.DB_HOST, port=conf.DB_PORT, database=conf.DB_NAME,
                                             user=conf.DB_USER, password=conf.DB_PASS)
        return cls._instance


class BaseModel(Model):
    class Meta:
        database = DBHelper().db


class Commute(BaseModel):
    employee_id = IntegerField()
    date = DateField()
    come_at = TimeField()
    leave_at = TimeField()


class Employee(BaseModel):
    employee_id = IntegerField()
    name = CharField()
    manager = BooleanField(default=False)