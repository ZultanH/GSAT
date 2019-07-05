from uuid       import uuid4
from .Base      import BaseModel
from .User      import User
from peewee     import CharField, ForeignKeyField
from enum       import Enum

    
class Stub(BaseModel):
    uid             = CharField(default=str(uuid4()), unique=True)
    owner           = ForeignKeyField(User, backref="stubs") #reference to corresponding User model
    sid             = CharField()

    @property
    def __dict__(self):
        return {
            "uid": self.uid,
            "owner": self.owner.__dict__,
            "sid": self.sid
        }