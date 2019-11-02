from enum               import Enum
from .BannedUser        import BannedUser
from .Notification      import Notification
from .Permission        import Permission
from .Role              import Role
from .Server            import Server
from .Stub              import Stub
from .User              import User
from .Loader            import Loader

from playhouse.db_url   import connect

class AccountState(Enum):
    PENDING  = 0
    NORMAL   = 1
    BANNED   = 2

class JWTStatus(Enum):
    NORMAL  = 0
    EXPIRED = 1
    INVALID = 2
    OTHER   = 3

db = connect("")
db.connect()
db.create_tables([User, Role, BannedUser, Notification, Permission, Server, Stub, Loader])
