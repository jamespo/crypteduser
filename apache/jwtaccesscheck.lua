require 'apache2'
local jwt = require 'luajwt'

function jwt_access_checker(r)
    local cookie = r:getcookie("user")
    if not cookie then
       return 403
    else
       local key = "kh3ro2kjfsdf8j"
       local ok, err = jwt.decode(cookie, key)
       if not ok then
	  io.stderr:write(cookie .. " " .. err)
	  return 403
       end       
       return apache2.OK
    end
end
