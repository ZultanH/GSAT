from .Base  import BaseModel
from peewee import ForeignKeyField, BooleanField

class Permission(BaseModel):
    list_users          = BooleanField(default=False)
    list_stubs          = BooleanField(default=False)
    list_servers        = BooleanField(default=False)
    user_status         = BooleanField(default=False)
    update_permissions  = BooleanField(default=False)
    view_permissions    = BooleanField(default=False)
    ban_user            = BooleanField(default=False)
    unban_user          = BooleanField(default=False)
    delete_server       = BooleanField(default=False)
    delete_stub         = BooleanField(default=False)
    create_stub         = BooleanField(default=False)
    add_notification    = BooleanField(default=False)
    delete_notification = BooleanField(default=False)
    
    @property
    def __dict__(self):
        return {
            "list_users":           self.list_users,
            "list_stubs":           self.list_stubs,
            "list_servers":         self.list_servers,
            "user_status":          self.user_status,
            "update_permissions":   self.update_permissions,
            "view_permissions":     self.view_permissions,
            "ban_user":             self.ban_user,
            "unban_user":           self.unban_user,
            "delete_server":        self.delete_server,
            "delete_stub":          self.delete_stub,
            "create_stub":          self.create_stub,
            "add_notification":     self.add_notification,
            "delete_notification":  self.delete_notification
        }