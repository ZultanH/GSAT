from .Base  import BaseModel
from .Permission import Permission
from peewee     import CharField, ForeignKeyField

class Role(BaseModel):
    name        = CharField()
    permissions = ForeignKeyField(Permission)

    @property
    def __dict__(self):
        return {"name": self.name, "permissions": self.permissions.__dict__}