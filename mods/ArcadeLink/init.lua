-- ArcadeLink — the game side of the live session (ADR-013).
-- Dials 127.0.0.1:2077, redials when the socket is down, answers status and place.
-- place names people from the character list. One name puts that person in front of V.
-- Several names put those people in a line, in the order given. Anyone not named stays.
-- It does not move V. A person already spawned is moved, not copied.

local json = require("link_json")
local Cron = require("Cron")

if not json or type(json.encode) ~= "function" then
  registerForEvent("onInit", function()
    print("[ArcadeLink] FATAL require('link_json') failed")
  end)
  return
end

local HOST = "127.0.0.1"
local PORT = 2077
local RETRY_S = 2.0
local ATTEMPT_TIMEOUT_S = 5.0
local VERSION = "0.1.4"
local lastInbound = 0
local GAP = 1.6
local FWD = 2.7

local socket = nil
local connected = false
local attempting = false
local attemptAt = 0
local actors = {}
local placing = false
local placeGen = 0

local function log(msg)
  print("[ArcadeLink] " .. tostring(msg))
end

local function round2(n)
  return math.floor(n * 100 + 0.5) / 100
end

local function playerState()
  local player = Game.GetPlayer()
  if player == nil then
    return nil
  end
  local ok, state = pcall(function()
    local pos = player:GetWorldPosition()
    local fwd = player:GetWorldForward()
    return {
      x = round2(pos.x),
      y = round2(pos.y),
      z = round2(pos.z),
      facing_x = round2(fwd.x),
      facing_y = round2(fwd.y),
    }
  end)
  if not ok then
    log("player read failed " .. tostring(state))
    return nil
  end
  return state
end

local send
local placeJobs = nil

local function trim(text)
  return (tostring(text or ""):match("^%s*(.-)%s*$"))
end

local function baseName(name)
  return string.lower(trim(name):gsub("%s*|%s*%d+$", ""))
end

local function flatRight(fwd)
  local len = math.sqrt(fwd.x * fwd.x + fwd.y * fwd.y)
  if len < 0.001 then
    return 0, 1
  end
  return -fwd.y / len, fwd.x / len
end

local function distXY(a, b)
  if a == nil or b == nil then
    return 999
  end
  local dx = a.x - b.x
  local dy = a.y - b.y
  return math.sqrt(dx * dx + dy * dy)
end

local function currentPlayer()
  local player = nil
  pcall(function()
    player = Game.GetPlayer()
  end)
  return player
end

local function entityHash(entity)
  if entity == nil then
    return nil
  end
  local hash = nil
  pcall(function()
    hash = tostring(entity:GetEntityID().hash)
  end)
  return hash
end

local function actorList()
  local keys = {}
  for key in pairs(actors) do
    table.insert(keys, key)
  end
  table.sort(keys)
  local list = {}
  for _, key in ipairs(keys) do
    local actor = actors[key]
    local row = { name = actor.name }
    local pos = nil
    if actor.entity ~= nil then
      pcall(function()
        pos = actor.entity:GetWorldPosition()
      end)
    end
    if pos ~= nil then
      row.x = round2(pos.x)
      row.y = round2(pos.y)
      row.z = round2(pos.z)
    end
    if actor.error ~= nil then
      row.error = actor.error
    elseif pos == nil then
      row.error = "gone"
    end
    table.insert(list, row)
  end
  return list
end

local function snapshot()
  return {
    schema = "table.v0",
    mod = "ArcadeLink",
    version = VERSION,
    player = playerState(),
    actors = actorList(),
  }
end

local function coerceNames(raw)
  if type(raw) == "string" then
    raw = { raw }
  end
  if type(raw) ~= "table" then
    return {}
  end
  local names = {}
  for _, item in ipairs(raw) do
    for part in tostring(item):gmatch("[^,]+") do
      local name = trim(part)
      if name ~= "" then
        table.insert(names, name)
      end
    end
  end
  return names
end

local function loadCatalog(AMM)
  if AMM == nil or type(AMM.API) ~= "table" or type(AMM.API.GetAMMCharacters) ~= "function" then
    return nil, "no catalog"
  end
  local ok, characters = pcall(function()
    return AMM.API.GetAMMCharacters()
  end)
  if not ok or type(characters) ~= "table" then
    return nil, "catalog failed"
  end
  return characters, nil
end

local function lookup(characters, query)
  local want = string.lower(query)
  local exact = nil
  local starts = {}
  local contains = {}
  for _, c in ipairs(characters) do
    local name = tostring(c.name or "")
    local low = string.lower(name)
    if low == want then
      exact = c
      break
    end
    if string.sub(low, 1, #want) == want then
      table.insert(starts, c)
    elseif #want >= 4 and string.find(low, want, 1, true) ~= nil then
      table.insert(contains, c)
    end
  end
  if exact ~= nil then
    return exact.record, exact.name, nil, nil
  end
  local pool = starts
  if #pool == 0 then
    pool = contains
  end
  if #pool == 1 then
    return pool[1].record, pool[1].name, nil, nil
  end
  if #pool > 1 then
    local matches = {}
    local n = math.min(5, #pool)
    for i = 1, n do
      matches[i] = pool[i].name
    end
    return nil, nil, "say which one", matches
  end
  return nil, nil, "not in catalog", nil
end

local function liveEntity(spawn)
  if spawn == nil or spawn.handle == nil then
    return nil
  end
  local pos = nil
  local ok = pcall(function()
    pos = spawn.handle:GetWorldPosition()
  end)
  if ok and pos ~= nil then
    return spawn.handle
  end
  return nil
end

local function spawnsNamed(AMM, key)
  local found = {}
  if AMM == nil or AMM.Spawn == nil or type(AMM.Spawn.spawnedNPCs) ~= "table" then
    return found
  end
  for _, spawn in pairs(AMM.Spawn.spawnedNPCs) do
    if baseName(spawn.name) == key then
      table.insert(found, spawn)
    end
  end
  return found
end

local function despawnSpawn(AMM, spawn)
  pcall(function()
    if type(spawn.Despawn) == "function" and spawn.handle ~= nil then
      spawn:Despawn()
    elseif AMM ~= nil and AMM.Spawn ~= nil and type(AMM.Spawn.spawnedNPCs) == "table" and type(spawn.uniqueName) == "function" then
      AMM.Spawn.spawnedNPCs[spawn.uniqueName()] = nil
    end
  end)
end

local function eachNearby(player, fn)
  pcall(function()
    local searchQuery = Game["TSQ_NPC;"]()
    searchQuery.maxDistance = 8
    local success, parts = Game.GetTargetingSystem():GetTargetParts(player, searchQuery)
    if not success or parts == nil then
      return
    end
    for _, part in ipairs(parts) do
      local entity = part:GetComponent(part):GetEntity()
      if entity ~= nil then
        local isNpc = false
        pcall(function()
          isNpc = entity:IsNPC()
        end)
        if isNpc then
          fn(entity)
        end
      end
    end
  end)
  local AMM = GetMod("AppearanceMenuMod")
  if AMM ~= nil and AMM.Spawn ~= nil and type(AMM.Spawn.spawnedNPCs) == "table" then
    for _, spawn in pairs(AMM.Spawn.spawnedNPCs) do
      local entity = liveEntity(spawn)
      if entity ~= nil then
        fn(entity)
      end
    end
  end
end

local function worldMark(player, fwdMeters, rightMeters)
  local mark, yaw = nil, nil
  local ok = pcall(function()
    local pos = player:GetWorldPosition()
    local fwd = player:GetWorldForward()
    local rot = player:GetWorldOrientation():ToEulerAngles()
    local rx, ry = flatRight(fwd)
    mark = Vector4.new(
      pos.x + fwd.x * fwdMeters + rx * rightMeters,
      pos.y + fwd.y * fwdMeters + ry * rightMeters,
      pos.z,
      1.0
    )
    yaw = rot.yaw - 180
  end)
  if not ok then
    return nil, nil
  end
  return mark, yaw
end

local function blocked(mark, spots)
  for _, pos in ipairs(spots) do
    if distXY(mark, pos) < 1.0 then
      return true
    end
  end
  return false
end

local function collectSpots(player, ignoreHashes)
  local spots = {}
  local playerHash = entityHash(player)
  eachNearby(player, function(entity)
    local hash = entityHash(entity)
    if hash == nil or hash == playerHash or ignoreHashes[hash] then
      return
    end
    local pos = nil
    pcall(function()
      pos = entity:GetWorldPosition()
    end)
    if pos ~= nil then
      table.insert(spots, pos)
    end
  end)
  return spots
end

local function chooseRights(n, player, spots)
  local function rights(shift)
    local list = {}
    for i = 1, n do
      list[i] = (i - (n + 1) / 2) * GAP + shift * GAP
    end
    return list
  end
  local function clear(shift)
    local list = rights(shift)
    for _, right in ipairs(list) do
      local mark = worldMark(player, FWD, right)
      if mark == nil or blocked(mark, spots) then
        return nil
      end
    end
    return list
  end
  for step = 0, 6 do
    local found = clear(step)
    if found ~= nil then
      return found
    end
    if step > 0 then
      found = clear(-step)
      if found ~= nil then
        return found
      end
    end
  end
  return rights(0)
end

local function clearOnMark(player, mark, ignoreHashes)
  if mark == nil then
    return
  end
  local playerHash = entityHash(player)
  eachNearby(player, function(entity)
    local hash = entityHash(entity)
    if hash == nil or hash == playerHash or ignoreHashes[hash] then
      return
    end
    local pos = nil
    pcall(function()
      pos = entity:GetWorldPosition()
    end)
    if distXY(pos, mark) > 0.7 then
      return
    end
    pcall(function()
      entity:Dispose()
    end)
    pcall(function()
      getEntitySystem():DeleteEntity(entity:GetEntityID())
    end)
    log("cleared a body on the mark")
  end)
end

local function setFriendly(entity, name)
  local AMM = GetMod("AppearanceMenuMod")
  if AMM == nil or AMM.Tools == nil or type(AMM.Tools.SetNPCAttitude) ~= "function" then
    return
  end
  local target = nil
  pcall(function()
    local scan = AMM:GetScanID(entity)
    target = AMM:NewTarget(entity, "NPCPuppet", scan, name, nil, nil)
  end)
  if target == nil then
    target = { handle = entity, hash = entityHash(entity) or "?", name = name }
  end
  pcall(function()
    AMM.Tools:SetNPCAttitude(target, EAIAttitude.AIA_Friendly)
  end)
end

local function jobRows(jobs)
  local rows = {}
  for _, job in ipairs(jobs) do
    local row = { name = job.name }
    if job.matches ~= nil then
      row.matches = job.matches
    end
    if job.error ~= nil then
      row.error = job.error
    else
      local actor = actors[job.key]
      if actor == nil then
        row.error = "gone"
      else
        row.name = actor.name or row.name
        local pos = nil
        if actor.entity ~= nil then
          pcall(function()
            pos = actor.entity:GetWorldPosition()
          end)
        end
        if pos ~= nil then
          row.x = round2(pos.x)
          row.y = round2(pos.y)
          row.z = round2(pos.z)
        end
        if actor.error ~= nil then
          row.error = actor.error
        elseif pos == nil then
          row.error = "gone"
        end
      end
    end
    table.insert(rows, row)
  end
  return rows
end

local function finishPlace(gen, id)
  if gen ~= placeGen then
    return
  end
  placing = false
  local message = snapshot()
  message.type = "place"
  message.id = id
  message.actors = jobRows(placeJobs or {})
  if send(message) then
    log("place id=" .. tostring(id))
  end
end

local function settle(name, key, entity, spawnPos, yaw, gen, oneDone)
  local actor = actors[key]
  pcall(function()
    entity:GetAIControllerComponent():DisableCollider()
  end)
  local function doTeleport()
    local AMM = GetMod("AppearanceMenuMod")
    if AMM == nil or AMM.Tools == nil or type(AMM.Tools.TeleportNPCTo) ~= "function" then
      return false, "no move"
    end
    return pcall(function()
      AMM.Tools:TeleportNPCTo(entity, spawnPos, yaw)
    end)
  end
  local okTp, errTp = doTeleport()
  log("move " .. name .. " " .. (okTp and "ok" or tostring(errTp)))
  local polls = 0
  local held = 0
  Cron.Every(0.2, function(timer)
    if gen ~= placeGen then
      Cron.Halt(timer)
      return
    end
    polls = polls + 1
    local here = nil
    pcall(function()
      here = entity:GetWorldPosition()
    end)
    local d = distXY(here, spawnPos)
    if d <= 0.35 then
      held = held + 1
    else
      held = 0
      if polls % 2 == 0 then
        doTeleport()
      end
    end
    if held >= 2 or polls >= 15 then
      Cron.Halt(timer)
      pcall(function()
        entity:GetAIControllerComponent():EnableCollider()
      end)
      if actor ~= nil and d > 0.35 then
        actor.error = "not on the mark"
      end
      setFriendly(entity, name)
      oneDone()
    end
  end)
end

local function spawnAndMove(job, AMM, gen, oneDone)
  if job.mark == nil then
    actors[job.key] = { name = job.name, error = "no mark" }
    oneDone()
    return
  end
  local spawnObj = nil
  local okB, errB = pcall(function()
    local scanId = AMM:GetScanID(job.record)
    spawnObj = AMM.Spawn:NewSpawn(
      tostring(job.name),
      tostring(scanId),
      nil,
      0,
      job.record,
      nil,
      nil
    )
  end)
  if not okB or spawnObj == nil then
    actors[job.key] = { name = job.name, error = "spawn failed" }
    log("newspawn " .. job.name .. " " .. tostring(errB))
    oneDone()
    return
  end
  local okS, errS = pcall(function()
    AMM.Spawn:SpawnNPC(spawnObj, true)
  end)
  if not okS then
    actors[job.key] = { name = job.name, error = "spawn failed" }
    log("spawnnpc " .. job.name .. " " .. tostring(errS))
    oneDone()
    return
  end
  actors[job.key] = { name = job.name, spawn = spawnObj, entity = nil }
  log("queued " .. job.name)
  local attempts = 0
  Cron.Every(0.2, function(timer)
    if gen ~= placeGen then
      Cron.Halt(timer)
      return
    end
    attempts = attempts + 1
    local entity = nil
    pcall(function()
      entity = spawnObj.handle
    end)
    if entity ~= nil then
      Cron.Halt(timer)
      local actor = actors[job.key]
      if actor ~= nil then
        actor.entity = entity
      end
      settle(job.name, job.key, entity, job.mark, job.yaw, gen, oneDone)
    elseif attempts > 40 then
      Cron.Halt(timer)
      local actor = actors[job.key]
      if actor ~= nil then
        actor.error = "did not appear"
      end
      log("missing " .. job.name)
      oneDone()
    end
  end)
end

local function beginPlace(id, rawNames)
  if placing then
    local message = snapshot()
    message.type = "place"
    message.id = id
    message.error = "busy"
    send(message)
    return
  end
  local names = coerceNames(rawNames)
  if #names == 0 then
    local message = snapshot()
    message.type = "place"
    message.id = id
    message.error = "say who"
    send(message)
    return
  end
  local player = currentPlayer()
  if player == nil then
    local message = snapshot()
    message.type = "place"
    message.id = id
    message.error = "no player"
    send(message)
    return
  end
  local AMM = GetMod("AppearanceMenuMod")
  local characters, catErr = loadCatalog(AMM)
  local jobs = {}
  local seenRaw = {}
  local seenCanon = {}
  local toPlace = {}
  for _, raw in ipairs(names) do
    local rawKey = string.lower(raw)
    local job = { key = rawKey, name = raw }
    if seenRaw[rawKey] then
      job.error = "named twice"
    else
      seenRaw[rawKey] = true
      if characters == nil then
        job.error = catErr or "no catalog"
      else
        local record, canon, err, matches = lookup(characters, raw)
        if record == nil then
          job.error = err
          job.matches = matches
        else
          local canonKey = string.lower(canon)
          if seenCanon[canonKey] then
            job.error = "named twice"
            job.name = canon
          else
            seenCanon[canonKey] = true
            job.record = record
            job.name = canon
            job.key = canonKey
            table.insert(toPlace, job)
          end
        end
      end
    end
    table.insert(jobs, job)
  end
  placeJobs = jobs
  if #toPlace == 0 then
    local message = snapshot()
    message.type = "place"
    message.id = id
    message.actors = jobRows(jobs)
    send(message)
    return
  end
  if AMM == nil or AMM.Spawn == nil then
    for _, job in ipairs(toPlace) do
      job.error = "no appearance menu"
      job.record = nil
    end
    local message = snapshot()
    message.type = "place"
    message.id = id
    message.actors = jobRows(jobs)
    send(message)
    return
  end
  placing = true
  placeGen = placeGen + 1
  local gen = placeGen
  local ignore = {}
  for _, job in ipairs(toPlace) do
    local keeper = nil
    for _, spawn in ipairs(spawnsNamed(AMM, job.key)) do
      local entity = liveEntity(spawn)
      if entity ~= nil and keeper == nil then
        keeper = spawn
        job.entity = entity
        job.spawn = spawn
        local hash = entityHash(entity)
        if hash ~= nil then
          ignore[hash] = true
        end
      else
        despawnSpawn(AMM, spawn)
      end
    end
  end
  local spots = collectSpots(player, ignore)
  local rights = chooseRights(#toPlace, player, spots)
  for i, job in ipairs(toPlace) do
    local mark, yaw = worldMark(player, FWD, rights[i])
    job.mark = mark
    job.yaw = yaw
  end
  local pending = #toPlace
  local function oneDone()
    pending = pending - 1
    if pending <= 0 then
      finishPlace(gen, id)
    end
  end
  for _, job in ipairs(toPlace) do
    if job.entity ~= nil then
      if job.mark == nil then
        actors[job.key] = { name = job.name, spawn = job.spawn, entity = job.entity, error = "no mark" }
        oneDone()
      else
        actors[job.key] = { name = job.name, spawn = job.spawn, entity = job.entity }
        settle(job.name, job.key, job.entity, job.mark, job.yaw, gen, oneDone)
      end
    else
      clearOnMark(player, job.mark, ignore)
      spawnAndMove(job, AMM, gen, oneDone)
    end
  end
end

send = function(message)
  if not connected or socket == nil or socket.SendCommand == nil then
    return false
  end
  local okEnc, encoded = pcall(json.encode, message)
  if not okEnc then
    log("encode failed " .. tostring(encoded))
    return false
  end
  local okSend, errSend = pcall(function()
    socket:SendCommand(encoded)
  end)
  if not okSend then
    log("send failed " .. tostring(errSend))
    connected = false
    return false
  end
  return true
end

local function sendHello()
  local message = snapshot()
  message.type = "hello"
  if send(message) then
    log("hello sent")
  end
end

local function replyStatus(id)
  local message = snapshot()
  message.type = "status"
  message.id = id
  if send(message) then
    log("status id=" .. tostring(id))
  end
end

local function dropSocket()
  local old = socket
  socket = nil
  connected = false
  if old ~= nil and old.Disconnect ~= nil then
    pcall(function()
      old:Disconnect()
    end)
  end
end

local function onCommand(raw)
  if raw == nil or raw == "" then
    return
  end
  local ok, message = pcall(json.decode, raw)
  if not ok or type(message) ~= "table" then
    log("bad message")
    return
  end
  if message.type == "ping" then
    lastInbound = os.clock()
    return
  end
  if message.type == "status" then
    lastInbound = os.clock()
    replyStatus(message.id)
    return
  end
  if message.type == "place" then
    lastInbound = os.clock()
    beginPlace(message.id, message.names)
    return
  end
  log("ignored type=" .. tostring(message.type))
end

local function onConnection(status)
  attempting = false
  if status ~= 0 then
    connected = false
    log("connect failed status=" .. tostring(status))
    return
  end
  connected = true
  lastInbound = os.clock()
  log("connected")
  sendHello()
end

local function onDisconnection()
  connected = false
  attempting = false
  log("disconnected")
end

local function onError()
  log("socket error")
end

local function tryConnect()
  if connected then
    return
  end
  attempting = true
  attemptAt = os.clock()
  dropSocket()
  attempting = true
  local RedSocket = GetMod("RedSocket")
  if RedSocket == nil then
    attempting = false
    log("RedSocket missing")
    return
  end
  local createSocket = RedSocket.createSocket or RedSocket.new
  if type(createSocket) ~= "function" then
    attempting = false
    log("RedSocket has no createSocket")
    return
  end
  local created = nil
  local okNew, errNew = pcall(function()
    created = createSocket()
  end)
  if not okNew or created == nil then
    attempting = false
    log("createSocket failed " .. tostring(errNew))
    return
  end
  socket = created
  local okReg, errReg = pcall(function()
    socket:RegisterListener(onCommand, onConnection, onDisconnection, onError)
    socket:Connect(HOST, PORT)
  end)
  if not okReg then
    attempting = false
    connected = false
    log("connect call failed " .. tostring(errReg))
  end
end

registerForEvent("onInit", function()
  log("loaded version=" .. VERSION)
  Cron.Every(RETRY_S, function()
    if connected and socket ~= nil and socket.IsConnected ~= nil then
      local quiet = os.clock() - lastInbound
      local ok, still = pcall(function()
        return socket:IsConnected()
      end)
      if ok and still and quiet < 3 then
        return
      end
      log("link down quiet=" .. string.format("%.1f", quiet))
      connected = false
      attempting = false
    end
    if attempting and (os.clock() - attemptAt) < ATTEMPT_TIMEOUT_S then
      return
    end
    tryConnect()
  end)
  tryConnect()
end)

registerForEvent("onUpdate", function(delta)
  Cron.Update(delta)
end)

registerForEvent("onShutdown", function()
  dropSocket()
  log("shutdown")
end)
