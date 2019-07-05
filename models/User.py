import datetime

from peewee         import CharField, DateTimeField, IntegerField, ForeignKeyField
from .Base          import BaseModel
from .Role          import Role
from .Permission    import Permission

class User(BaseModel):
    uuid                = CharField()
    username            = CharField(unique=True)
    password            = CharField()
    email               = CharField()
    role                = ForeignKeyField(Role)
    account_state       = IntegerField()
    permissions         = ForeignKeyField(Permission, backref="user")
    hwid                = CharField()
    
    @property
    def __dict__(self):
        return {
            "uuid":             self.uuid,
            "username":         self.username,
            "email":            self.email,
            "role":             self.role.__dict__,
            "account_state":    self.account_state,
            "permissions":      self.permissions.__dict__
        }