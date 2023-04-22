import os

from peewee import *
from dotenv import load_dotenv

load_dotenv()

from peewee import *


class DBHelper(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = MySQLDatabase(host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
                                             database=os.getenv('DB_NAME'),
                                             user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'))
        return cls._instance


class BaseModel(Model):
    class Meta:
        database = DBHelper().db


class Commute(BaseModel):
    username = CharField()
    date = IntegerField()
    come_at = IntegerField()
    leave_at = IntegerField()
