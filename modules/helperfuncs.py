"""
-------------------------
|    Helper Functions   |
-------------------------
"""
import jwt
import datetime
import base64
import binascii

from dateutil           import parser
from sanic              import response
from sanic.response     import text, json
from datetime           import timedelta
from ..models.globals   import Permission, User, Stub, Server, AccountState, JWTStatus
from functools          import wraps
from jwt.exceptions     import PyJWTError, InvalidTokenError, ExpiredSignatureError

JWT_SECRET = "Cu`t5zUQ$mt=9?qt"

def Successful():
    return json({"success": True, "error": False})

def Unsuccessful(errorMsg):
    return json({"success": False, "error": True, "error_msg": errorMsg})

def SuccessfulContent(content):
    return json({"success": True, "error": False, "content": content})

def validPermission(permissionName):
    try:
        Permission.select().where(getattr(Permission, permissionName) == False).get()
        return True
    except Permission.DoesNotExist:
        return False

def isNone(*args):
    return None in args

def tobool(boolStr):
    return True if boolStr.lower() == "true" else False

#def authenticateUser(userModel):
    #session.permanent       = True
    #session["logged_in"]    = True
    #session["user_uuid"]    = userModel.uuid
    #session["username"]     = userModel.username

#def getCurrentUser():
#    if session.get("logged_in"):
#        return User.get(User.uuid == session["user_uuid"])

#def login_required(f):
#    @wraps(f)
#    def predicate(*args, **kwargs):
#        if not session.get("logged_in"):
#            return redirect(url_for("login"))
#        return f(*args, **kwargs)
#    return predicate

def validate_token(f):
    @wraps(f)
    async def predicate(request, *args, **kwargs):
        try:
            token = request.form.get("api_token")
            if token is None:
                return Unsuccessful("No API Token Supplied")
            
            payload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
        except PyJWTError:
            return Unsuccessful("Invalid Token")
        else:
            if not payload.get("uuid"):
                return Unsuccessful("Invalid Payload")
            
            userModel = User.get(User.uuid == payload["uuid"])
            tokenTimestamp = payload["time"]
            tokenDatetime = datetime.datetime.fromtimestamp(tokenTimestamp)

            if (datetime.datetime.now() - tokenDatetime).total_seconds() >= 14400: #4 hours
                return Unsuccessful("Token Expired")
            
            if not userModel.account_state == AccountState.NORMAL.value:
                accountStateName = AccountState(userModel.account_state).name
                return Unsuccessful(f"Account: {accountStateName}")
        return await f(request, *args, **kwargs)
    return predicate


def stubExists(sid):
    if sid is None:
        return False
    
    try:
        Stub.get(Stub.sid == sid)
        return True
    except Stub.DoesNotExist:
        return False

def serverExists(ip, port):
    if isNone(ip, port):
        return False
    
    try:
        Server.get((Server.ip == ip) & (Server.port == port))
        return True
    except Server.DoesNotExist:
        return False

def getJwtStatus(token):
    if token is None:
        return JWTStatus.INVALID
    
    try:
        payload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
        return JWTStatus.NORMAL
    except InvalidTokenError:
        return JWTStatus.INVALID
    except PyJWTError:
        return JWTStatus.OTHER
    else:
        tokenTime = payload["time"]
        dtClass = datetime.datetime.fromtimestamp(tokenTime)
        difference = datetime.datetime.now() - dtClass
        if difference.total_seconds() > timedelta(hours=12).total_seconds():
            return JWTStatus.EXPIRED

def validBase64(payload):
    try:
        base64.b64decode(payload.encode())
        return True
    except binascii.Error:
        return False

def dtFromStr(dtStr):
    return parser.parse(dtStr)
