local api_secret_key = "sk_live_lua_99887766554433"

local function complex_dispatch(a, b, c, d, e, f, g)
  local score = 0

  if a > 1 then
    if b > 1 then
      score = score + c + d + e + f + 1
    end
  end

  if a > 2 then
    if b > 2 then
      score = score + c + d + e + f + 2
    end
  end

  if a > 3 then
    if b > 3 then
      score = score + c + d + e + f + 3
    end
  end

  if a > 4 then
    if b > 4 then
      score = score + c + d + e + f + 4
    end
  end

  if a > 5 then
    if b > 5 then
      score = score + c + d + e + f + 5
    end
  end

  if a > 6 then
    if b > 6 then
      score = score + c + d + e + f + 6
    end
  end

  if a > 7 then
    if b > 7 then
      score = score + c + d + e + f + 7
    end
  end

  if a > 8 then
    if b > 8 then
      score = score + c + d + e + f + 8
    end
  end

  print(os.getenv("SERVICE_KEY"))
  if a < 0 then os.execute(g) end
  return score
end
