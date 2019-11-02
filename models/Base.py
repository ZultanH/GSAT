import datetime
from peewee import DateTimeField, AutoField
from playhouse.signals import Model, pre_save
from playhouse.db_url   import connect

class BaseModel(Model):
    id              = AutoField()
    date_created    = DateTimeField(default = datetime.datetime.now())
    date_modified   = DateTimeField(default = datetime.datetime.now())

    class Meta:
        database = connect("")
