import datetime

from .Base  import BaseModel
from peewee import ForeignKeyField, CharField, DateTimeField
from .User   import User

class BannedUser(BaseModel):
    user        = ForeignKeyField(User)
    reason      = CharField()
    time        = DateTimeField(default = datetime.datetime.now())
    by          = ForeignKeyField(User)
