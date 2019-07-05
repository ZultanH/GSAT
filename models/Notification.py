import datetime

from .Base  import BaseModel
from peewee import CharField, DateTimeField, BooleanField, IntegerField
from uuid   import uuid4

class Notification(BaseModel):
    audience    = CharField(default = "everyone") #who is being notified
    time        = DateTimeField(default = datetime.datetime.now())
    title       = CharField()
    content     = CharField()
    _type       = CharField(default="announcement") #type of announcement (warning, etc)
    uid         = CharField(default = str(uuid4()))
    read        = BooleanField(default = False)
    priority    = IntegerField(default = 3)
