from ..models.globals import Server, Stub, User

class ServerModule:
    def __init__(self, uid):
        self.uid = uid
    
    def exists(self):
        try:
            Server.select().where(Server.uid == self.uid).get()
            return True
        except Server.DoesNotExist:
            return False
    
    def getServerByUid(self):
        record = Server.select().where(Server.uid == self.uid).get()
        return record
    
    @staticmethod
    def getServerByIp(serverIp):
        record = Server.select().where(Server.ip == serverIp).get()
        return record
    
    @staticmethod
    def getAll():
        tbl = {}
        for serverModel in Server.select():
            tbl[serverModel.uid] = [
                serverModel.ip,
                serverModel.port
            ]
        return tbl