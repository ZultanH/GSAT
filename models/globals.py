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

db = connect("postgres://jtfahlfstizxxv:66f734d3134489f0b9ec0ed32f0be69a24f60a25d45a539889fc6c71aab3e80a@ec2-107-20-185-16.compute-1.amazonaws.com:5432/d7q25b18db4ht8")
db.connect()
db.create_tables([User, Role, BannedUser, Notification, Permission, Server, Stub, Loader])