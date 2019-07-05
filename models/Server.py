from .Base  import BaseModel
from peewee import CharField, IntegerField, ForeignKeyField, DateTimeField, TextField
from uuid   import uuid4
from .Stub  import Stub

class Server(BaseModel):
    uid                 = CharField(default=str(uuid4()), unique=True)
    ip                  = CharField(default="0.0.0.0")
    port                = IntegerField(default=27015)
    stub                = ForeignKeyField(Stub, backref="servers") #reference to corresponding Stub model
    last_auth           = DateTimeField()
    payload             = TextField()
    payload_instance    = CharField()

    @property    
    def __dict__(self):
       return {
           "uid": self.uid,
           "ip": self.ip,
           "port": self.port,
           "stub": self.stub.__dict__,
           "last_auth": self.last_auth,
           "payload": self.payload,
           "payload_instance": self.payload_instance
       }