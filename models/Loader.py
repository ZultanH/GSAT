from .Base  import BaseModel
from peewee import TextField, FloatField

class Loader(BaseModel):
    code    = TextField()
    version = FloatField()