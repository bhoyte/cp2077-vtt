-- ArcadeLink — operated-table session (ADR-013).
-- Dials the booth, redials when the socket is down, answers status.
-- Does not spawn, move, or despawn anyone.

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
local VERSION = "0.1.2"
local lastInbound = 0

local socket = nil
local connected = false
local attempting = false
local attemptAt = 0

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

local function snapshot()
  return {
    schema = "table.v0",
    mod = "ArcadeLink",
    version = VERSION,
    player = playerState(),
    actors = {},
  }
end

local function send(message)
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
