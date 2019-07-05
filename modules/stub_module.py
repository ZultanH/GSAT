from ..models.globals   import Stub, Server, User, Loader
from uuid               import uuid4
from binascii           import crc32
from .short_url         import ShortURL
from string             import Template

class StubModule: 
    def __init__(self, uid):
        self.uid = uid if uid is not None else "No Stub"
    
    def stubExists(self):
        try:
            Stub.get(Stub.uid == self.uid)
            return True
        except Stub.DoesNotExist:
            return False
    
    
    @staticmethod
    def createStub(ownerUid):
        ownerModel = User.get(User.uuid == ownerUid)
        loaderCode = Loader.get(Loader.id==1).code
        uidStr = str(uuid4())
        uidCRC = crc32(uidStr.encode())
        sid    = ShortURL.encode(uidCRC)

        t = Template(loaderCode)
        loaderCodeSubstituted = t.substitute({"sid": sid})

        Stub.create(
            owner = ownerModel,
            sid   = sid
        )

        return {"sid": sid, "uid": uidStr, "code": loaderCodeSubstituted}