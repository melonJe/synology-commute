import configuration as conf
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
    user_id = IntegerField()
    date = DateField()
    come_at = TimeField()
    leave_at = TimeField()


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    username = CharField()
    manager = BooleanField(default=False)
