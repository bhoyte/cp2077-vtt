-- CypherAgent/init.lua — Bridge lab mod for Night City Live Milestone 0.
-- Emits SceneSnapshot v0.1, sends snapshots via RedSocket, receives ACK/command envelopes.
-- require("json") returns nil on many CET builds (preload/built-in clash). Use bundled rxi lib under a unique name.
local json = require("cypher_json")
local Cron = require("Cron")

if not json or type(json.encode) ~= "function" then
  registerForEvent("onInit", function()
    print("[Cypher FATAL] require('cypher_json') failed. Place cypher_json.lua next to init.lua in mods/CypherAgent/.")
  end)
  return
end

local SCHEMA_VERSION = "scene_snapshot.v0.1"
local POLL_INTERVAL_SECONDS = 0.2

local isReady = false
local snapshot = {}
local snapshotTick = 0

local socket = nil
local isConnected = false
local pendingCommands = {}
-- logical_id -> { character_id = string, entity = handle|nil, amm_spawn = AMM spawn wrapper|nil }
local spawnedNpcs = {}
local ackStats = {
  received = 0,
  mismatched = 0,
  last_tick_id = nil
}

local DEFAULT_SPAWN_CHARACTER = "Character.gang_maelstrom_melee_w_hard"

local function resolveEntityRef(ref)
  if ref == nil then
    return nil
  end
  local okHandle = pcall(function()
    if type(ref.GetEntityID) ~= "function" then
      error("not-handle")
    end
    ref:GetEntityID()
  end)
  if okHandle then
    return ref
  end
  local ok, ent = pcall(function()
    return Game.FindEntityByID(ref)
  end)
  if ok then
    return ent
  end
  return nil
end

local function getAmmModules()
  local AMM = GetMod("AppearanceMenuMod")
  if AMM == nil then
    return nil, nil, nil
  end
  local spawnMod = AMM.Spawn
  local api = AMM.API
  return AMM, spawnMod, api
end

local function recordLeafName(record)
  local leaf = tostring(record or ""):match("%.([^%.]+)$")
  if leaf == nil or leaf == "" then
    return tostring(record)
  end
  return leaf:gsub("_", " ")
end

-- Resolve a record to AMM's known character catalog to match what works in AMM UI.
local function resolveAmmCharacter(AMM, requestedRecord, requestedName)
  local api = AMM.API
  if type(api) ~= "table" or type(api.GetAMMCharacters) ~= "function" then
    return nil, nil, "AMM.API.GetAMMCharacters unavailable"
  end
  local ok, characters = pcall(function()
    return api.GetAMMCharacters()
  end)
  if not ok or type(characters) ~= "table" then
    return nil, nil, "AMM character catalog query failed"
  end

  local rec = tostring(requestedRecord or "")
  if rec == "" then
    rec = DEFAULT_SPAWN_CHARACTER
  end

  for _, c in ipairs(characters) do
    if c.record == rec then
      return c.record, c.name, nil
    end
  end

  local recLower = string.lower(rec)
  for _, c in ipairs(characters) do
    if string.lower(tostring(c.record or "")) == recLower then
      return c.record, c.name, nil
    end
  end

  local name = tostring(requestedName or "")
  if name == "" then
    name = rec
  end
  local nameLower = string.lower(name)
  for _, c in ipairs(characters) do
    if string.lower(tostring(c.name or "")) == nameLower then
      return c.record, c.name, nil
    end
  end

  return nil, nil, "record/name not found in AMM catalog"
end

local function logAmmCharacterCatalog(limit)
  local AMM, _, api = getAmmModules()
  if AMM == nil or type(api) ~= "table" or type(api.GetAMMCharacters) ~= "function" then
    print("[Cypher ERROR] AMM.API.GetAMMCharacters unavailable")
    return
  end
  local ok, characters = pcall(function()
    return api.GetAMMCharacters()
  end)
  if not ok or type(characters) ~= "table" then
    print("[Cypher ERROR] AMM character catalog query failed")
    return
  end

  local n = #characters
  local maxN = tonumber(limit) or 25
  if maxN < 1 then
    maxN = 1
  end
  if maxN > n then
    maxN = n
  end
  print("[Cypher AMM] characters total=" .. tostring(n) .. " showing=" .. tostring(maxN))
  for i = 1, maxN do
    local c = characters[i]
    print("[Cypher AMM] character[" .. tostring(i) .. "] name=" .. tostring(c.name) .. " record=" .. tostring(c.record))
  end
end

local function nowMs()
  -- CET Lua does not expose a monotonic ms clock directly; combine wall time + fractional process time.
  local wallMs = os.time() * 1000
  local fractionMs = math.floor((os.clock() % 1) * 1000)
  return wallMs + fractionMs
end

local function logSocketMessage(prefix, payload)
  if payload == nil then
    print(prefix)
    return
  end
  print(prefix .. tostring(payload))
end

local function onCommand(raw)
  if raw == nil or raw == "" then
    return
  end

  local ok, message = pcall(json.decode, raw)
  if not ok or type(message) ~= "table" then
    print("[Cypher SOCKET ERROR] Failed to decode incoming message: " .. tostring(raw))
    return
  end

  local messageType = message.type
  if messageType == nil and message.status == "ok" then
    messageType = "ack"
  end

  if messageType == "ack" then
    ackStats.received = ackStats.received + 1
    ackStats.last_tick_id = message.tick_id
    if message.tick_id ~= snapshotTick then
      ackStats.mismatched = ackStats.mismatched + 1
    end
    logSocketMessage("[Cypher ACK] tick_id=", message.tick_id)
    return
  end

  if messageType == "command" then
    table.insert(pendingCommands, message)
    logSocketMessage("[Cypher COMMAND RECEIVED] id=", message.id)
    return
  end

  print("[Cypher SOCKET] Ignoring unknown message type: " .. tostring(messageType))
end

local function onConnection(status)
  if status ~= 0 then
    print("[Cypher SOCKET ERROR] RedSocket connection failed.")
    isConnected = false
    return
  end

  isConnected = true
  print("[Cypher SOCKET] Connected to Python bridge.")
end

local function onDisconnection()
  isConnected = false
  print("[Cypher SOCKET] Disconnected from Python bridge.")
end

local function onError()
  print("[Cypher SOCKET ERROR] Failed to send command.")
end

local function executeCommand(cmd)
  local action = cmd.action
  local id = tostring(cmd.id or "unknown")

  if action == "log_marker" then
    print("[Cypher CMD] id=" .. id .. " action=log_marker")
    if cmd.payload ~= nil then
      local ok, payloadStr = pcall(json.encode, cmd.payload)
      if ok then
        print("[Cypher CMD PAYLOAD] " .. payloadStr)
      end
    end
    return
  end

  if action == "amm_list_npcs" then
    local n = 0
    for logicalId, entry in pairs(spawnedNpcs) do
      n = n + 1
      local h = entry.entity
      if h == nil and entry.amm_spawn ~= nil then
        h = entry.amm_spawn.handle
      end
      local hasE = (h ~= nil) and "yes" or "no"
      print("[Cypher AMM] registry: " .. tostring(logicalId) .. " character=" .. tostring(entry.character_id) .. " has_entity=" .. hasE)
    end
    if n == 0 then
      print("[Cypher AMM] registry: (empty)")
    end
    return
  end

  if action == "amm_list_characters" then
    local payload = cmd.payload or {}
    logAmmCharacterCatalog(payload.limit)
    return
  end

  if action == "amm_spawn_npc" then
    local payload = cmd.payload or {}
    local logicalId = payload.logical_id
    if logicalId == nil or logicalId == "" then
      print("[Cypher ERROR] amm_spawn_npc requires payload.logical_id")
      return
    end
    if spawnedNpcs[logicalId] ~= nil then
      local existing = spawnedNpcs[logicalId]
      local ref = existing.entity
      if ref == nil and existing.amm_spawn ~= nil then
        ref = existing.amm_spawn.handle
      end
      local live = resolveEntityRef(ref)
      if live ~= nil then
        print("[Cypher] skip spawn — logical_id already exists: " .. tostring(logicalId))
        return
      end
      print("[Cypher WARN] replacing stale logical_id with no live entity: " .. tostring(logicalId))
      spawnedNpcs[logicalId] = nil
    end

    local AMM, spawnMod, _ = getAmmModules()
    if AMM == nil then
      print("[Cypher ERROR] AppearanceMenuMod not loaded")
      return
    end
    if type(spawnMod) ~= "table" or type(spawnMod.NewSpawn) ~= "function" or type(spawnMod.SpawnNPC) ~= "function" then
      print("[Cypher ERROR] AMM.Spawn module unavailable")
      return
    end

    local requestedRecord = payload.character_id
    local requestedName = payload.character_name
    local record, displayName, resolveErr = resolveAmmCharacter(AMM, requestedRecord, requestedName)
    if record == nil then
      print("[Cypher ERROR] cannot resolve AMM character: " .. tostring(resolveErr))
      print("[Cypher INFO] Try AMM Spawn UI names (e.g. Female Maelstrom Grunt) via payload.character_name")
      return
    end

    local spawnId = logicalId
    local okScan, scanId = pcall(function()
      return AMM:GetScanID(record)
    end)
    if okScan and scanId ~= nil then
      spawnId = tostring(scanId)
    end
    local params = nil
    if payload.appearance ~= nil and payload.appearance ~= "" then
      params = { app = tostring(payload.appearance) }
    end

    local spawnObj = nil
    local okBuild, buildErr = pcall(function()
      spawnObj = spawnMod:NewSpawn(
        tostring(displayName or recordLeafName(record)),
        spawnId,
        params,
        0,
        record,
        nil,
        nil
      )
    end)
    if not okBuild or spawnObj == nil then
      print("[Cypher ERROR] AMM NewSpawn failed: " .. tostring(buildErr))
      return
    end

    local okSpawn, spawnErr = pcall(function()
      -- We override position after AMM resolves handle.
      spawnMod:SpawnNPC(spawnObj, true)
    end)
    if not okSpawn then
      print("[Cypher ERROR] AMM SpawnNPC failed: " .. tostring(spawnErr))
      return
    end

    spawnedNpcs[logicalId] = {
      character_id = record,
      entity = nil,
      amm_spawn = spawnObj
    }

    local player = Game.GetPlayer()
    local forwardM = tonumber(payload.forward_m) or 3.0
    local pos = player and player:GetWorldPosition() or nil
    local fwd = player and player:GetWorldForward() or nil
    local rot = player and player:GetWorldOrientation():ToEulerAngles() or nil
    local spawnPos = nil
    if pos ~= nil and fwd ~= nil then
      spawnPos = Vector4.new(
        pos.x + fwd.x * forwardM,
        pos.y + fwd.y * forwardM,
        pos.z,
        1.0
      )
    end

    local attempts = 0
    Cron.Every(0.2, function(args)
      attempts = attempts + 1
      local handle = nil
      if spawnObj ~= nil then
        handle = spawnObj.handle
      end
      local entity = resolveEntityRef(handle)
      if entity ~= nil then
        local reg = spawnedNpcs[logicalId]
        if reg ~= nil then
          reg.entity = entity
        end

        if spawnPos ~= nil and rot ~= nil then
          local okTp, errTp = pcall(function()
            Game.GetTeleportationFacility():Teleport(
              entity,
              spawnPos,
              EulerAngles.new(rot.roll, rot.pitch, rot.yaw - 180)
            )
          end)
          if not okTp then
            print("[Cypher WARN] post-spawn teleport failed: " .. tostring(errTp))
          end
        end

        print("[Cypher] spawn complete logical_id=" .. tostring(logicalId))
        Cron.Halt(args)
      elseif attempts > 50 then
        spawnedNpcs[logicalId] = nil
        print("[Cypher WARN] AMM spawn unresolved logical_id=" .. tostring(logicalId) .. " record=" .. tostring(record))
        Cron.Halt(args)
      end
    end)

    print("[Cypher] spawn queued logical_id=" .. tostring(logicalId) .. " character=" .. tostring(record))
    return
  end

  if action == "amm_despawn_npc" then
    local logicalId = (cmd.payload or {}).logical_id
    if logicalId == nil or logicalId == "" then
      print("[Cypher ERROR] amm_despawn_npc requires payload.logical_id")
      return
    end
    local entry = spawnedNpcs[logicalId]
    if entry == nil then
      print("[Cypher] unknown logical_id: " .. tostring(logicalId))
      return
    end
    if entry.amm_spawn ~= nil then
      local okD, errD = pcall(function()
        entry.amm_spawn:Despawn()
      end)
      if not okD then
        print("[Cypher WARN] amm_spawn:Despawn failed: " .. tostring(errD))
      end
    elseif entry.entity ~= nil then
      local okD, errD = pcall(function()
        entry.entity:Dispose()
      end)
      if not okD then
        print("[Cypher WARN] entity:Dispose failed: " .. tostring(errD))
      end
    end
    spawnedNpcs[logicalId] = nil
    print("[Cypher] despawned logical_id=" .. tostring(logicalId))
    return
  end

  if action == "amm_set_appearance" then
    local payload = cmd.payload or {}
    local logicalId = payload.logical_id
    local appearance = payload.appearance
    if logicalId == nil or logicalId == "" then
      print("[Cypher ERROR] amm_set_appearance requires payload.logical_id")
      return
    end
    if appearance == nil or appearance == "" then
      print("[Cypher ERROR] amm_set_appearance requires payload.appearance")
      return
    end
    local entry = spawnedNpcs[logicalId]
    if entry == nil then
      print("[Cypher ERROR] amm_set_appearance unknown logical_id: " .. tostring(logicalId))
      return
    end
    local entity = resolveEntityRef(entry.entity)
    if entity == nil and entry.amm_spawn ~= nil then
      entity = resolveEntityRef(entry.amm_spawn.handle)
    end
    if entity == nil then
      print("[Cypher ERROR] amm_set_appearance no live entity for logical_id=" .. tostring(logicalId))
      return
    end

    local AMM, _, api = getAmmModules()
    if AMM == nil or type(api) ~= "table" or type(api.ChangeAppearance) ~= "function" then
      print("[Cypher ERROR] AMM.API.ChangeAppearance unavailable")
      return
    end
    local okA, errA = pcall(function()
      api.ChangeAppearance(entity, tostring(appearance))
    end)
    if not okA then
      print("[Cypher ERROR] amm_set_appearance failed: " .. tostring(errA))
      return
    end
    print("[Cypher] amm_set_appearance logical_id=" .. tostring(logicalId) .. " appearance=" .. tostring(appearance))
    return
  end

  if type(action) == "string" and (string.sub(action, 1, 4) == "cam_" or string.sub(action, 1, 4) == "pup_") then
    local spike = GetMod("ArcadeSpike")
    if spike == nil or type(spike.handle_command) ~= "function" then
      print("[Cypher ERROR] ArcadeSpike not loaded (need CET reload after install)")
      return
    end
    local okSpike, errSpike = pcall(function()
      spike.handle_command(action, cmd.payload or {}, id)
    end)
    if not okSpike then
      print("[Cypher ERROR] ArcadeSpike: " .. tostring(errSpike))
    end
    return
  end

  print("[Cypher CMD] id=" .. id .. " target=" .. tostring(cmd.target or "?") .. " action=" .. tostring(action) .. " (no handler)")
  if cmd.payload ~= nil then
    local ok, payloadStr = pcall(json.encode, cmd.payload)
    if ok then
      print("[Cypher CMD PAYLOAD] " .. payloadStr)
    end
  end
end

registerForEvent("onInit", function()
  print("[Cypher] Mod loaded.")
  isReady = true

  -- ArcadeLink owns 127.0.0.1:2077 (ADR-013). This mod no longer dials.
  print("[Cypher] socket disabled; ArcadeLink owns the session.")
  local RedSocket = nil
  if RedSocket ~= nil then
    local createSocket = RedSocket.createSocket or RedSocket.new
    if type(createSocket) == "function" then
      socket = createSocket()
      if socket ~= nil and socket.RegisterListener ~= nil and socket.Connect ~= nil then
        socket:RegisterListener(onCommand, onConnection, onDisconnection, onError)
        socket:Connect("127.0.0.1", 2077)
      else
        print("[Cypher SOCKET ERROR] Socket object missing required methods.")
      end
    else
      print("[Cypher SOCKET ERROR] Could not find RedSocket.createSocket/new API.")
    end
  else
    print("[Cypher SOCKET WARN] RedSocket not found. Observer running in local-only mode.")
  end

  -- Poll game state every 200ms.
  Cron.Every(POLL_INTERVAL_SECONDS, function()
    if not isReady then return end

    local player = Game.GetPlayer()
    if player == nil then return end

    -- Wrap the entire snapshot logic in a protected call (catches API changes / patch issues)
    local success, err = pcall(function()
      local pos = player:GetWorldPosition()
      local forward = player:GetWorldForward()

      local hasCombat, inCombat = pcall(function() return player:IsInCombat() end)
      if not hasCombat then inCombat = false end

      local hasDead, isDead = pcall(function() return player:IsDead() end)
      if not hasDead then isDead = false end

      snapshotTick = snapshotTick + 1
      snapshot = {
        schema_version = SCHEMA_VERSION,
        tick_id = snapshotTick,
        timestamp_ms = nowMs(),
        player = {
          position = {
            x = string.format("%.1f", pos.x),
            y = string.format("%.1f", pos.y),
            z = string.format("%.1f", pos.z)
          },
          facing = {
            x = string.format("%.2f", forward.x),
            y = string.format("%.2f", forward.y)
          },
          is_in_combat = inCombat,
          is_dead = isDead
        },
        events = {}
      }

      local encoded = json.encode(snapshot)
      print("[Cypher] " .. encoded)

      if isConnected and socket ~= nil and socket.SendCommand ~= nil then
        socket:SendCommand(encoded)
      end
    end)

    if not success then
      print("[Cypher ERROR] " .. tostring(err))
    end
  end)
end)

registerForEvent("onUpdate", function(delta)
  Cron.Update(delta)

  if #pendingCommands > 0 then
    local cmd = table.remove(pendingCommands, 1)
    local okRun, errRun = pcall(function()
      executeCommand(cmd)
    end)
    if not okRun then
      print("[Cypher CMD ERROR] " .. tostring(errRun))
    end
  end
end)

registerForEvent("onShutdown", function()
  isReady = false
  if socket ~= nil and socket.Disconnect ~= nil then
    socket:Disconnect()
  end
  print(
    "[Cypher] Shutting down. ack_received=" .. tostring(ackStats.received) ..
    " ack_mismatch=" .. tostring(ackStats.mismatched)
  )
  print("[Cypher] Shutting down.")
end)
