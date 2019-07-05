import string
import random
import hashlib

from uuid import uuid4

from ..models.globals import User, AccountState, Permission, BannedUser, Role

def cleanDict(userDict):
    if userDict.get("password"):
        del userDict["password"]

    if userDict.get("account_state") and type(userDict.get("account_state")) is int:
        accountStateInt = userDict["account_state"]
        userDict["account_state"] = AccountState(accountStateInt).name
    
    return userDict
    
class UserModule:
    def __init__(self, uuid):
        self.uuid = uuid
    
    def validUid(self):
        try:
            User.get(User.uuid == self.uuid)
            return True
        except User.DoesNotExist:
            return False
    
    def assignRole(self, roleName):
        roleModel = Role.get(Role.name == roleName)
        permissionsJson = roleModel.permissions.__dict__

        User.update(role = roleModel).where(User.uuid == self.uuid).execute()
        self.updatePermissions(permissionsJson)

    def isRole(self, roleName):
        userModel = self.getUser()
        return userModel.role.name == roleName
    
    def getAccountState(self):
        model = self.getUser()
        return AccountState(model.account_state).name
    
    def setAccountState(self, stateName):
        User.update(account_state=AccountState(getattr(AccountState, stateName)).value).where(User.uuid == self.uuid).execute()

    @staticmethod
    def allUsers():
        userList = [cleanDict(record.__dict__) for record in User.select()]
        return userList
    
    @classmethod
    def getPendingdUsers(cls):
        userList = [cleanDict(record.__dict__) for record in User.select().where(User.account_state == AccountState.PENDING.value)]
        return userList
    
    def getUser(self):
        record = User.get(User.uuid == self.uuid)
        return record
    
    @staticmethod
    def createUser(accountInfo):
        username        = accountInfo["username"]
        password        = accountInfo["password"]
        email           = accountInfo["email"]
        hwid            = accountInfo["hwid"]
        uuid            = str(uuid4())

        hashedPassword  = hashlib.sha256(password.encode()).hexdigest()

        roleModel = Role.get(Role.name == "pending")

        newUser = User.create(
            username=username, 
            password=hashedPassword, 
            email=email, 
            account_state=AccountState.PENDING.value, 
            uuid=uuid,
            role=roleModel,
            permissions=roleModel.permissions,
            hwid=hwid
        )
        return newUser
        
    @staticmethod
    def getUserUidByUsername(username):
        record = User.get(User.username == username)
        return record.uuid

    def hasPermission(self, permission):
        userModel = self.getUser()
        userPermissions = userModel.permissions
        return getattr(userPermissions, permission)
    
    def updatePermissions(self, valueDict):
        Permission.update(**valueDict).where(Permission == self.getUser().permissions).execute()

    def banUser(self, userUid, reason=None):
        query = User.update(account_state=AccountState.BANNED.value).where(User.uuid == userUid)
        query.execute()

        toBan = User.get(User.uuid == userUid)
        reason = reason if reason is not None else "dumb idiot"
        bannedUserLog = BannedUser(user = toBan.id, reason = reason, by = self.getUser())
        bannedUserLog.save()

    def unbanUser(self, userUid):
        userModel = User.get(User.uuid == userUid)
        userUpdateQuery  = User.update(account_state=AccountState.NORMAL.value).where(User.uuid == userUid)
        BannedUserLog    = BannedUser.delete().where(BannedUser.user == userModel)

        BannedUserLog.execute()
        userUpdateQuery.execute()

    def isBanned(self):
        userModel = self.getUser()
        return userModel.account_state == AccountState.BANNED.value