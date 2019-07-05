import datetime
from peewee import DateTimeField, AutoField
from playhouse.signals import Model, pre_save
from playhouse.db_url   import connect

class BaseModel(Model):
    id              = AutoField()
    date_created    = DateTimeField(default = datetime.datetime.now())
    date_modified   = DateTimeField(default = datetime.datetime.now())

    class Meta:
        database = connect("postgres://jtfahlfstizxxv:66f734d3134489f0b9ec0ed32f0be69a24f60a25d45a539889fc6c71aab3e80a@ec2-107-20-185-16.compute-1.amazonaws.com:5432/d7q25b18db4ht8")