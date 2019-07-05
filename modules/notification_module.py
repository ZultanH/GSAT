from ..models.globals import Notification

class NotificationModule:
    def __init__(self, notificationUid):
        self.uid = notificationUid

    @staticmethod
    def addNotification(*args, **kwargs):
        title   = kwargs.get('title')
        user    = kwargs.get('user')
        content = kwargs.get('content')
        _type   = kwargs.get("_type")
        
        if len(title) > 20:
            raise ValueError("Title too long")
        
        if len(content) > 250:
            raise ValueError("Content too long")

        if not user:
            user = "everyone"

        newNotification = Notification(
            user=user,
            title=title,
            content=content,
            _type=_type
        )

        newNotification.save()

    def notificationExists(self):
        try:
            Notification.select().where(Notification.uid == self.uid).get()
            return True
        except Notification.DoesNotExist:
            return False
    
    def getNotificationById(self):
        return Notification.select().where(Notification.uid == self.uid).get()
    
    def removeNotificationById(self):
        Notification.delete().where(Notification.uid == self.uid).execute()
    
    @staticmethod
    def getNoitificationsByUser(self, userUid):
        return [Notification for Notification in Notification.select().where(Notification.user == userUid)]

    def setRead(self, boolean, userUid):
        Notification.edit(read=boolean).where((Notification.uid == self.uid) & (Notification.user == userUid)).execute()