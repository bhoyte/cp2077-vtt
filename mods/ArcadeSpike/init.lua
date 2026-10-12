-- ArcadeSpike — S-01 camera rig. Commands arrive via CypherAgent (cam_*).
-- Never invent APIs: every engine call is pcall + [ArcadeSpike] RESULT.

local Cron = require("Cron")

local CAMERA_PATH = "base\\entities\\cameras\\simple_free_camera.ent"
local RESTRICTIONS = {
  "GameplayRestriction.NoMovement",
  "GameplayRestriction.NoCameraControl",
  "GameplayRestriction.NoZooming",
  "GameplayRestriction.FastForwardCrouchLock",
  "GameplayRestriction.NoCombat",
  "GameplayRestriction.VehicleNoSummoning",
  "GameplayRestriction.NoPhone",
  "GameplayRestriction.NoDriving",
}

local PRESETS = {
  { id = "cam_a", fwd = 4.0, right = 0.0,  up = 2.2, yaw_off = 180, pitch = -15, fov = 70 },
  { id = "cam_b", fwd = 1.2, right = 2.0,  up = 1.7, yaw_off = 200, pitch = -8,  fov = 45 },
  { id = "cam_c", fwd = 2.8, right = -0.8, up = 1.5, yaw_off = 175, pitch = -10, fov = 35 },
}

-- Standing talk clip. Same workspot entity for every rig. Rig must match the body.
local POSE = {
  name = "stand__2h_on_hip__01__talk__neutral__01",
  ent = "base\\amm_workspots\\entity\\workspot_anim.ent",
  comp = "amm_workspot_base",
}

-- Small offsets in front of V. Actors move; V does not.
local CAST = {
  { id = "johnny", name = "Johnny Silverhand", rig = "Man Average", fwd = 2.2, right = -1.2 },
  { id = "hanako", name = "Hanako", rig = "Woman Average", fwd = 2.4, right = 0.0 },
  { id = "song", name = "Song So Ri", rig = "Woman Average", fwd = 2.2, right = 1.2 },
}

local ArcadeSpike = {
  version = "s02-cast",
  actors = {},
  spawning = false,
  pendingCut = nil,
  cams = {},
  active = nil,
  vHidden = false,
  tppHead = false,
  subject = nil,
  subjectAngles = nil,
  parkRight = nil,
  spawnPath = "none",
  exAtInit = "unlogged",
  exAfterLoad = "unlogged",
}

local function log(msg)
  print("[ArcadeSpike] " .. tostring(msg))
end

local function result(key, value)
  print("[ArcadeSpike] RESULT " .. tostring(key) .. "=" .. tostring(value))
end

local function dumpKeys(label, tbl)
  if type(tbl) ~= "table" then
    result(label, type(tbl))
    return
  end
  local keys = {}
  for k, v in pairs(tbl) do
    table.insert(keys, tostring(k) .. ":" .. type(v))
  end
  table.sort(keys)
  result(label, table.concat(keys, ","))
end

local function describeEx()
  local kind = type(exEntitySpawner)
  if kind == "table" or kind == "userdata" then
    local spawnType = "missing"
    local ok, t = pcall(function()
      return type(exEntitySpawner.Spawn)
    end)
    if ok then
      spawnType = t
    end
    return kind .. " spawn=" .. spawnType
  end
  return kind
end

local function playerOrNil()
  local ok, player = pcall(function()
    return Game.GetPlayer()
  end)
  if ok then
    return player
  end
  return nil
end

local function horizontalRight(fwd)
  local rx, ry = fwd.y, -fwd.x
  local len = math.sqrt(rx * rx + ry * ry)
  if len < 0.001 then
    return 1, 0
  end
  return rx / len, ry / len
end

local function makeAngles(roll, pitch, yaw)
  local angles = nil
  local via = "none"
  local okNamed = pcall(function()
    angles = ToEulerAngles({ roll = roll, pitch = pitch, yaw = yaw })
  end)
  if okNamed and angles ~= nil then
    via = "ToEulerAngles"
    return angles, via
  end
  local okNew = pcall(function()
    angles = EulerAngles.new(roll, pitch, yaw)
  end)
  if okNew and angles ~= nil then
    via = "EulerAngles.new(roll,pitch,yaw)"
    return angles, via
  end
  return nil, via
end

local function applyEffect(effect, apply)
  local player = playerOrNil()
  if player == nil then
    return false, "no-player"
  end
  local ok, err = pcall(function()
    local effectID = TweakDBID.new(effect)
    local ses = Game.GetStatusEffectSystem()
    if apply then
      ses:ApplyStatusEffect(player:GetEntityID(), effectID, player:GetRecordID(), player:GetEntityID())
    else
      ses:RemoveStatusEffect(player:GetEntityID(), effectID, 999)
    end
  end)
  return ok, err
end

local function setRestrictions(on)
  local failed = 0
  for i = 1, #RESTRICTIONS do
    local ok, err = applyEffect(RESTRICTIONS[i], on)
    if not ok then
      failed = failed + 1
      log("restriction fail " .. RESTRICTIONS[i] .. " err=" .. tostring(err))
    end
  end
  result("restrictions", (on and "on" or "off") .. " failed=" .. tostring(failed))
end

local function genderSuffix()
  local player = playerOrNil()
  if player == nil then
    return "Ma"
  end
  local ok, name = pcall(function()
    return player:GetResolvedGenderName()
  end)
  if ok and string.find(tostring(name), "Female") then
    return "Wa"
  end
  return "Ma"
end

local function toggleTppHead(enable)
  local player = playerOrNil()
  if player == nil then
    result("tpp_head", "no-player")
    return
  end
  local ok, err = pcall(function()
    local ts = Game.GetTransactionSystem()
    local gender = genderSuffix()
    local headItem = string.format("Items.CharacterCustomization%sHead", gender)
    local itemID = ItemID.FromTDBID(TweakDBID.new(headItem))
    local slot = TweakDBID.new("AttachmentSlots.TppHead")
    local fppHead = ItemID.FromTDBID(TweakDBID.new("Items.PlayerFppHead"))
    if ts:HasItem(player, itemID) == false then
      ts:GiveItem(player, itemID, 1)
    end
    ts:RemoveItemFromSlot(player, slot, true, true, true)
    if enable then
      ts:AddItemToSlot(player, slot, itemID)
    else
      ts:AddItemToSlot(player, slot, fppHead)
      ts:ChangeItemAppearanceByName(player, fppHead, "default&FPP")
    end
  end)
  ArcadeSpike.tppHead = enable and ok
  result("tpp_head", (enable and "on" or "off") .. " ok=" .. tostring(ok) .. " err=" .. tostring(err))
end

local function tryAmmToggleHead()
  local ok, err = pcall(function()
    local AMM = GetMod("AppearanceMenuMod")
    if AMM == nil or AMM.Tools == nil or type(AMM.Tools.ToggleHead) ~= "function" then
      error("AMM.Tools:ToggleHead unavailable")
    end
    AMM.Tools:ToggleHead()
  end)
  result("amm_toggle_head", "ok=" .. tostring(ok) .. " err=" .. tostring(err))
  return ok
end

local function hideHud(hide)
  -- Do not call SettingsSystem:GetVar("/interface", "hud"). That name is not
  -- in the group; the engine asserts and flatlines (RED4ext 2026-10-11 21:59:40).
  result("hud", "untouched hide=" .. tostring(hide) .. " reason=no-safe-api")
end

local function storeSubject()
  local player = playerOrNil()
  if player == nil then
    return false
  end
  local pos = player:GetWorldPosition()
  local fwd = player:GetWorldForward()
  local rx, ry = horizontalRight(fwd)
  ArcadeSpike.subject = Vector4.new(pos.x, pos.y, pos.z, pos.w)
  ArcadeSpike.parkRight = { x = rx, y = ry }
  local ok, ang = pcall(function()
    return player:GetWorldOrientation():ToEulerAngles()
  end)
  if ok then
    ArcadeSpike.subjectAngles = ang
  end
  result("subject", string.format("%.2f,%.2f,%.2f", pos.x, pos.y, pos.z))
  return true
end

local function spawnViaEx(preset, pos, angles)
  local player = playerOrNil()
  local transform = nil
  local okT = pcall(function()
    transform = player:GetWorldTransform()
    transform:SetPosition(pos)
  end)
  if not okT or transform == nil then
    return nil, "no-transform"
  end
  local okS, entityID = pcall(function()
    return exEntitySpawner.Spawn(CAMERA_PATH, transform, "")
  end)
  if not okS or entityID == nil then
    return nil, "spawn-nil:" .. tostring(entityID)
  end
  local hash = "?"
  pcall(function()
    hash = tostring(entityID.hash)
  end)
  result("spawn_id", preset.id .. " type=" .. type(entityID) .. " hash=" .. hash)
  return entityID, nil
end

local spawnViaAmm

local function rememberCam(preset, entity, component, entityID, via, amm)
  if component ~= nil then
    pcall(function()
      component:SetFOV(preset.fov)
    end)
  end
  ArcadeSpike.cams[preset.id] = {
    handle = entity,
    component = component,
    entityID = entityID,
    via = via,
    amm = amm,
  }
  result("spawned", preset.id .. " via=" .. via .. " component=" .. tostring(component ~= nil))
  if ArcadeSpike.ready_count() >= 3 and ArcadeSpike.pendingCut ~= nil then
    local blend = ArcadeSpike.pendingCut
    ArcadeSpike.pendingCut = nil
    ArcadeSpike.spawning = false
    ArcadeSpike.cut("cam_a", blend)
    result("hotkey_ready", "showing cam_a")
  end
end

local function attachWhenReady(preset, entityID, angles, pos)
  local ticks = 0
  Cron.Every(0.1, { tick = 1 }, function(timer)
    ticks = ticks + 1
    local entity = nil
    local okFind, findErr = pcall(function()
      entity = Game.FindEntityByID(entityID)
    end)
    if not okFind and (ticks == 1 or ticks == 25) then
      result("find_err", preset.id .. " " .. tostring(findErr))
    end
    if entity ~= nil then
      local component = nil
      pcall(function()
        component = entity:FindComponentByName("camera")
      end)
      if component ~= nil and angles ~= nil then
        pcall(function()
          component:SetLocalOrientation(angles:ToQuat())
        end)
      end
      rememberCam(preset, entity, component, entityID, "exEntitySpawner", nil)
      Cron.Halt(timer)
    elseif ticks > 50 then
      result("spawn_timeout", preset.id .. " via=exEntitySpawner ticks=" .. tostring(ticks))
      local okAmm, errAmm = spawnViaAmm(preset, pos, angles)
      if not okAmm then
        result("amm_spawn_fail", preset.id .. " " .. tostring(errAmm))
      end
      Cron.Halt(timer)
    end
  end)
end

function spawnViaAmm(preset, pos, angles)
  local AMM = GetMod("AppearanceMenuMod")
  if AMM == nil or type(AMM.Camera) ~= "table" or type(AMM.Camera.new) ~= "function" then
    return false, "AMM.Camera unavailable"
  end
  local cam = AMM.Camera:new()
  local ok, err = pcall(function()
    cam:Spawn(pos, angles)
  end)
  if not ok then
    return false, tostring(err)
  end
  local ticks = 0
  Cron.Every(0.1, { tick = 1 }, function(timer)
    ticks = ticks + 1
    if cam.handle ~= nil and cam.component ~= nil then
      rememberCam(preset, cam.handle, cam.component, cam.entityID, "amm.Camera", cam)
      Cron.Halt(timer)
    elseif ticks > 50 then
      result("spawn_timeout", preset.id .. " via=amm.Camera")
      Cron.Halt(timer)
    end
  end)
  return true, nil
end

local function spawnOne(preset)
  local player = playerOrNil()
  if player == nil then
    result("spawn_skip", preset.id .. " no-player")
    return
  end
  local pos = player:GetWorldPosition()
  local fwd = player:GetWorldForward()
  local rx, ry = horizontalRight(fwd)
  local camPos = Vector4.new(
    pos.x + fwd.x * preset.fwd + rx * preset.right,
    pos.y + fwd.y * preset.fwd + ry * preset.right,
    pos.z + preset.up,
    1.0
  )
  local playerAng = player:GetWorldOrientation():ToEulerAngles()
  local angles, viaAng = makeAngles(0, preset.pitch, playerAng.yaw + preset.yaw_off)
  result("angles_" .. preset.id, viaAng)

  if ArcadeSpike.spawnPath == "own" or ArcadeSpike.spawnPath == "none" then
    local entityID, err = spawnViaEx(preset, camPos, angles)
    if entityID ~= nil then
      ArcadeSpike.spawnPath = "own"
      attachWhenReady(preset, entityID, angles, camPos)
      return
    end
    result("own_spawn_fail", preset.id .. " " .. tostring(err))
  end

  local okAmm, errAmm = spawnViaAmm(preset, camPos, angles)
  if okAmm then
    ArcadeSpike.spawnPath = "amm"
    return
  end
  result("amm_spawn_fail", preset.id .. " " .. tostring(errAmm))
  ArcadeSpike.spawnPath = "failed"
end

local function deactivateFpp()
  pcall(function()
    Game.GetPlayer():GetFPPCameraComponent():Deactivate(0, false)
  end)
end

local function activateFpp()
  pcall(function()
    Game.GetPlayer():GetFPPCameraComponent():Activate()
  end)
end

function ArcadeSpike.probe()
  local player = playerOrNil()
  result("player", player ~= nil)
  result("exEntitySpawner_now", describeEx())
  result("exEntitySpawner_onInit", ArcadeSpike.exAtInit)
  result("exEntitySpawner_afterLoad", ArcadeSpike.exAfterLoad)
  local AMM = GetMod("AppearanceMenuMod")
  dumpKeys("amm_keys", AMM)
  if type(AMM) == "table" then
    result("amm_Camera", type(AMM.Camera))
    result("amm_Tools", type(AMM.Tools))
    result("amm_Util", type(AMM.Util) .. "/" .. type(Util))
  end
  local angles, via = makeAngles(0, -10, 180)
  result("euler_helper", via .. " ok=" .. tostring(angles ~= nil))
end

function ArcadeSpike.spawn_rig()
  ArcadeSpike.cams = {}
  ArcadeSpike.active = nil
  if not storeSubject() then
    result("spawn_rig", "no-player")
    return
  end
  result("exEntitySpawner_spawn", describeEx())
  if describeEx() ~= "nil" then
    ArcadeSpike.spawnPath = "own"
  else
    ArcadeSpike.spawnPath = "none"
  end
  for i = 1, #PRESETS do
    spawnOne(PRESETS[i])
  end
end

function ArcadeSpike.cut(camId, blend)
  blend = tonumber(blend) or 0
  local target = ArcadeSpike.cams[camId]
  if target == nil or target.component == nil then
    result("cut_fail", tostring(camId) .. " missing")
    return
  end
  local prev = ArcadeSpike.active
  if prev ~= nil and ArcadeSpike.cams[prev] ~= nil and ArcadeSpike.cams[prev].component ~= nil and prev ~= camId then
    pcall(function()
      ArcadeSpike.cams[prev].component:Deactivate(blend, false)
    end)
  end
  deactivateFpp()
  local ok, err = pcall(function()
    target.component:Activate(blend, false)
  end)
  ArcadeSpike.active = camId
  result("cut", camId .. " blend=" .. tostring(blend) .. " ok=" .. tostring(ok) .. " err=" .. tostring(err) .. " from=" .. tostring(prev))
end

function ArcadeSpike.hide_v()
  setRestrictions(true)
  toggleTppHead(true)
  hideHud(true)
  ArcadeSpike.vHidden = true
  result("hide_v", "requested")
end

function ArcadeSpike.show_v()
  setRestrictions(false)
  toggleTppHead(false)
  hideHud(false)
  ArcadeSpike.vHidden = false
  result("show_v", "requested")
end

function ArcadeSpike.park(meters)
  meters = tonumber(meters) or 0
  local player = playerOrNil()
  if player == nil or ArcadeSpike.subject == nil or ArcadeSpike.parkRight == nil then
    result("park_fail", "no-subject")
    return
  end
  local dest = Vector4.new(
    ArcadeSpike.subject.x + ArcadeSpike.parkRight.x * meters,
    ArcadeSpike.subject.y + ArcadeSpike.parkRight.y * meters,
    ArcadeSpike.subject.z,
    1.0
  )
  local ang = ArcadeSpike.subjectAngles
  if ang == nil then
    local ok, a = pcall(function()
      return player:GetWorldOrientation():ToEulerAngles()
    end)
    if ok then
      ang = a
    end
  end
  local ok, err = pcall(function()
    Game.GetTeleportationFacility():Teleport(player, dest, ang)
  end)
  result("park", tostring(meters) .. " ok=" .. tostring(ok) .. " err=" .. tostring(err))
end

function ArcadeSpike.status()
  local ids = {}
  for id, cam in pairs(ArcadeSpike.cams) do
    table.insert(ids, id .. ":" .. tostring(cam.component ~= nil) .. "/" .. tostring(cam.via))
  end
  table.sort(ids)
  result("status_cams", table.concat(ids, ","))
  result("status_active", tostring(ArcadeSpike.active))
  result("status_path", ArcadeSpike.spawnPath)
  result("status_hidden", ArcadeSpike.vHidden)
  local player = playerOrNil()
  if player ~= nil then
    local pos = player:GetWorldPosition()
    result("status_player", string.format("%.2f,%.2f,%.2f", pos.x, pos.y, pos.z))
  end
end

local CAMERA_ORDER = { "cam_a", "cam_b", "cam_c" }

function ArcadeSpike.ready_count()
  local n = 0
  for i = 1, #CAMERA_ORDER do
    local cam = ArcadeSpike.cams[CAMERA_ORDER[i]]
    if cam ~= nil and cam.component ~= nil then
      n = n + 1
    end
  end
  return n
end

function ArcadeSpike.cycle(blend)
  blend = tonumber(blend) or 0
  if ArcadeSpike.ready_count() < #CAMERA_ORDER then
    ArcadeSpike.pendingCut = blend
    if not ArcadeSpike.spawning then
      ArcadeSpike.spawning = true
      ArcadeSpike.spawn_rig()
      result("hotkey", "spawning")
    else
      result("hotkey", "waiting " .. tostring(ArcadeSpike.ready_count()) .. "/3")
    end
    return
  end
  local nextId = CAMERA_ORDER[1]
  for i = 1, #CAMERA_ORDER do
    if ArcadeSpike.active == CAMERA_ORDER[i] then
      nextId = CAMERA_ORDER[(i % #CAMERA_ORDER) + 1]
      break
    end
  end
  ArcadeSpike.cut(nextId, blend)
end

function ArcadeSpike.despawn(doPark)
  if ArcadeSpike.active ~= nil then
    local cam = ArcadeSpike.cams[ArcadeSpike.active]
    if cam ~= nil and cam.component ~= nil then
      pcall(function()
        cam.component:Deactivate(0, false)
      end)
    end
  end
  ArcadeSpike.active = nil
  activateFpp()
  for id, cam in pairs(ArcadeSpike.cams) do
    pcall(function()
      if cam.amm ~= nil and type(cam.amm.Despawn) == "function" then
        cam.amm:Despawn()
      elseif cam.handle ~= nil then
        cam.handle:Dispose()
      end
    end)
    result("despawned", id)
  end
  ArcadeSpike.cams = {}
  ArcadeSpike.spawning = false
  ArcadeSpike.pendingCut = nil
  ArcadeSpike.show_v()
  if doPark ~= false and ArcadeSpike.subject ~= nil then
    ArcadeSpike.park(0)
  end
  result("despawn", "done")
end

local function playerPos()
  local player = playerOrNil()
  if player == nil then
    return nil
  end
  local ok, pos = pcall(function()
    return player:GetWorldPosition()
  end)
  if ok and pos ~= nil then
    return pos
  end
  return nil
end

local function formatPos(pos)
  if pos == nil then
    return "nil"
  end
  return string.format("%.2f,%.2f,%.2f", pos.x, pos.y, pos.z)
end

local function resolveCharacter(AMM, name)
  local api = AMM.API
  if type(api) ~= "table" or type(api.GetAMMCharacters) ~= "function" then
    return nil, nil, "no catalog"
  end
  local ok, characters = pcall(function()
    return api.GetAMMCharacters()
  end)
  if not ok or type(characters) ~= "table" then
    return nil, nil, "catalog failed"
  end
  local want = string.lower(name)
  for _, c in ipairs(characters) do
    if string.lower(tostring(c.name or "")) == want then
      return c.record, c.name, nil
    end
  end
  return nil, nil, "not in catalog"
end

local function flatRight(fwd)
  local len = math.sqrt(fwd.x * fwd.x + fwd.y * fwd.y)
  if len < 0.001 then
    return 0, 1
  end
  return -fwd.y / len, fwd.x / len
end

function ArcadeSpike.clear_cast()
  for id, actor in pairs(ArcadeSpike.actors) do
    pcall(function()
      if actor.spawn ~= nil and type(actor.spawn.Despawn) == "function" then
        actor.spawn:Despawn()
      elseif actor.entity ~= nil then
        actor.entity:Dispose()
      end
    end)
    result("pup_cleared", id)
  end
  ArcadeSpike.actors = {}
  result("pup_clear", "done")
end

local function poseAndHold(actor)
  local AMM = GetMod("AppearanceMenuMod")
  if AMM == nil or actor.entity == nil then
    result("pup_pose_err", actor.id .. " no-amm-or-entity")
    return
  end
  local target = nil
  local okT, errT = pcall(function()
    local scan = AMM:GetScanID(actor.entity)
    target = AMM:NewTarget(actor.entity, "NPCPuppet", scan, actor.name, nil, nil)
  end)
  if not okT or target == nil then
    local hash = "?"
    pcall(function()
      hash = tostring(actor.entity:GetEntityID().hash)
    end)
    target = { handle = actor.entity, hash = hash, name = actor.name }
    result("pup_target_fallback", actor.id .. " " .. tostring(errT))
  end
  actor.target = target
  if AMM.Tools ~= nil and type(AMM.Tools.SetNPCAttitude) == "function" then
    local okA, errA = pcall(function()
      AMM.Tools:SetNPCAttitude(target, EAIAttitude.AIA_Friendly)
    end)
    result("pup_attitude", actor.id .. " " .. (okA and "friendly" or tostring(errA)))
  end
  if AMM.Poses == nil or type(AMM.Poses.PlayAnimationOnTarget) ~= "function" then
    result("pup_pose_err", actor.id .. " no-poses")
    return
  end
  local anim = {
    name = POSE.name,
    ent = POSE.ent,
    comp = POSE.comp,
    rig = actor.rig,
  }
  local okP, errP = pcall(function()
    AMM.Poses:PlayAnimationOnTarget(target, anim, true)
  end)
  result("pup_posed", actor.id .. " " .. (okP and "ok" or tostring(errP)))
  Cron.After(2.0, function()
    if ArcadeSpike.actors[actor.id] ~= actor or actor.entity == nil then
      return
    end
    if AMM.Tools == nil or type(AMM.Tools.FreezeNPC) ~= "function" then
      result("pup_freeze_err", actor.id .. " no-freeze")
      return
    end
    local okF, errF = pcall(function()
      AMM.Tools:FreezeNPC(actor.entity, true)
    end)
    result("pup_frozen", actor.id .. " " .. (okF and "ok" or tostring(errF)))
    actor.frozen = okF
    actor.settled = true
    local pending = false
    for _, other in pairs(ArcadeSpike.actors) do
      if not other.settled then
        pending = true
      end
    end
    if not pending then
      result("pup_player_end", formatPos(playerPos()))
      result("pup_cast", "done")
    end
  end)
end

local function placeActor(spec, spawnObj)
  local player = playerOrNil()
  if player == nil or spawnObj == nil then
    result("pup_place_err", spec.id .. " no-player")
    return
  end
  local pos = player:GetWorldPosition()
  local fwd = player:GetWorldForward()
  local rot = player:GetWorldOrientation():ToEulerAngles()
  local rx, ry = flatRight(fwd)
  local spawnPos = Vector4.new(
    pos.x + fwd.x * spec.fwd + rx * spec.right,
    pos.y + fwd.y * spec.fwd + ry * spec.right,
    pos.z,
    1.0
  )
  local attempts = 0
  Cron.Every(0.2, function(timer)
    attempts = attempts + 1
    local entity = nil
    pcall(function()
      entity = spawnObj.handle
    end)
    if entity ~= nil then
      local actor = ArcadeSpike.actors[spec.id]
      if actor ~= nil then
        actor.entity = entity
      end
      local okTp, errTp = pcall(function()
        Game.GetTeleportationFacility():Teleport(
          entity,
          spawnPos,
          EulerAngles.new(rot.roll, rot.pitch, rot.yaw - 180)
        )
      end)
      result("pup_placed", spec.id .. " " .. (okTp and "ok" or tostring(errTp)))
      poseAndHold(actor)
      Cron.Halt(timer)
    elseif attempts > 40 then
      result("pup_place_err", spec.id .. " unresolved")
      local actor = ArcadeSpike.actors[spec.id]
      if actor ~= nil then
        actor.settled = true
      end
      local pending = false
      for _, other in pairs(ArcadeSpike.actors) do
        if not other.settled then
          pending = true
        end
      end
      if not pending then
        result("pup_player_end", formatPos(playerPos()))
        result("pup_cast", "done")
      end
      Cron.Halt(timer)
    end
  end)
end

function ArcadeSpike.cast()
  local startPos = playerPos()
  result("pup_player_start", formatPos(startPos))
  ArcadeSpike.clear_cast()
  local AMM = GetMod("AppearanceMenuMod")
  if AMM == nil or AMM.Spawn == nil then
    result("pup_cast", "no-amm")
    return
  end
  for _, spec in ipairs(CAST) do
    local record, displayName, err = resolveCharacter(AMM, spec.name)
    if record == nil then
      result("pup_spawn_err", spec.id .. " " .. tostring(err))
    else
      local spawnObj = nil
      local okB, errB = pcall(function()
        local scanId = AMM:GetScanID(record)
        spawnObj = AMM.Spawn:NewSpawn(
          tostring(displayName or spec.name),
          tostring(scanId),
          nil,
          0,
          record,
          nil,
          nil
        )
      end)
      if not okB or spawnObj == nil then
        result("pup_spawn_err", spec.id .. " newspawn " .. tostring(errB))
      else
        local okS, errS = pcall(function()
          AMM.Spawn:SpawnNPC(spawnObj, true)
        end)
        if not okS then
          result("pup_spawn_err", spec.id .. " " .. tostring(errS))
        else
          ArcadeSpike.actors[spec.id] = {
            id = spec.id,
            name = spec.name,
            rig = spec.rig,
            spawn = spawnObj,
            entity = nil,
            frozen = false,
          }
          result("pup_queued", spec.id)
          placeActor(spec, spawnObj)
        end
      end
    end
  end
end

function ArcadeSpike.handle_command(action, payload, id)
  payload = payload or {}
  log("cmd id=" .. tostring(id) .. " action=" .. tostring(action))
  if action == "cam_probe" then
    ArcadeSpike.probe()
  elseif action == "cam_spawn" then
    ArcadeSpike.spawn_rig()
  elseif action == "cam_cut" then
    ArcadeSpike.cut(payload.cam, payload.blend)
  elseif action == "cam_hide" then
    ArcadeSpike.hide_v()
  elseif action == "cam_show" then
    ArcadeSpike.show_v()
  elseif action == "cam_park" then
    ArcadeSpike.park(payload.meters)
  elseif action == "cam_status" then
    ArcadeSpike.status()
  elseif action == "cam_despawn" then
    ArcadeSpike.despawn(payload.park == true)
  elseif action == "pup_cast" then
    ArcadeSpike.cast()
  elseif action == "pup_clear" then
    ArcadeSpike.clear_cast()
  else
    result("unknown_cmd", tostring(action))
  end
end

registerForEvent("onInit", function()
  ArcadeSpike.exAtInit = describeEx()
  result("exEntitySpawner_onInit", ArcadeSpike.exAtInit)
  log("loaded version=" .. ArcadeSpike.version)
  Cron.Every(0.5, { tick = 1 }, function(timer)
    timer.tick = timer.tick + 1
    local player = playerOrNil()
    if player ~= nil then
      ArcadeSpike.exAfterLoad = describeEx()
      result("exEntitySpawner_afterLoad", ArcadeSpike.exAfterLoad)
      Cron.Halt(timer)
    elseif timer.tick > 120 then
      ArcadeSpike.exAfterLoad = "no-player-timeout " .. describeEx()
      result("exEntitySpawner_afterLoad", ArcadeSpike.exAfterLoad)
      Cron.Halt(timer)
    end
  end)
end)

registerForEvent("onUpdate", function(delta)
  Cron.Update(delta)
end)

registerHotkey("arcade_next_camera", "Arcade: next camera", function()
  ArcadeSpike.cycle(0)
end)

registerHotkey("arcade_blend_camera", "Arcade: blend to next camera", function()
  ArcadeSpike.cycle(1.5)
end)

registerHotkey("arcade_release_camera", "Arcade: release camera", function()
  ArcadeSpike.despawn(false)
end)

return ArcadeSpike
