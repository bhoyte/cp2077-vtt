# CET Mod Reference

Verified patterns for `cypher-vision/CypherAgent/`. Do not invent APIs — check [NativeDB](https://nativedb.red4ext.com) or Redmodding Discord when unsure.

---

## File layout (critical)

CET resolves `require()` from the **mod root**, not `modules/`.

```
mods/CypherAgent/
  init.lua           ← require("cypher_json"), require("Cron")
  Cron.lua           ← from psiberx/cp2077-cet-kit
  cypher_json.lua    ← from rxi/json.lua (unique name — see below)
```

**Wrong:** `require("modules/Cron")` with files in `modules/` — often yields `Cron is nil`.

**Wrong:** `require("json")` — often returns nil due to CET built-in/preload clash. The repo uses `cypher_json.lua` and `require("cypher_json")`.

---

## init.lua skeleton

```lua
local json = require("cypher_json")
local Cron = require("Cron")

registerForEvent("onInit", function()
  Cron.Every(0.2, function()
    local player = Game.GetPlayer()
    if player == nil then return end
    -- build snapshot, json.encode, socket:SendCommand or print
  end)
end)

registerForEvent("onUpdate", function(delta)
  Cron.Update(delta)  -- required or Cron never fires
end)
```

The shipped `init.lua` is much larger: RedSocket bridge, AMM spawn executor, command queue. Read it before extending.

---

## Cron.lua

From [psiberx/cp2077-cet-kit](https://github.com/psiberx/cp2077-cet-kit).

| API | Use |
|-----|-----|
| `Cron.Every(interval, fn)` | Repeating timer (0.2 = 200ms) |
| `Cron.After(delay, fn)` | One-shot |
| `Cron.Update(delta)` | **Must** run in `onUpdate` |

`registerForEvent("onUpdate", ...)` should only call `Cron.Update` — no heavy work per frame.

---

## cypher_json.lua

Bundled rxi/json under a unique module name:

```lua
local json = require("cypher_json")
local s = json.encode({foo = "bar"})
local t = json.decode(s)
```

Nil values can break encode — guard before building tables.

---

## Player snapshot (verified)

```lua
local player = Game.GetPlayer()
local pos = player:GetWorldPosition()      -- Vector4
local forward = player:GetWorldForward()   -- Vector4

local inCombat = false
local ok, result = pcall(function() return player:IsInCombat() end)
if ok then inCombat = result end
```

Wrap patch-sensitive calls in `pcall` (already done in `init.lua`).

---

## RedSocket (Phase 2 — implemented)

```lua
local RedSocket = GetMod("RedSocket")
if RedSocket == nil then
  print("[Cypher] ERROR: RedSocket not installed!")
  return
end

local socket = RedSocket.createSocket()

local function OnCommand(command) -- handle BridgeCommand JSON end
local function OnConnection(status)
  if status ~= 0 then print("[Cypher] Connection failed.") return end
  print("[Cypher SOCKET] Connected to Python bridge.")
end

socket:RegisterListener(OnCommand, OnConnection)  -- BEFORE Connect
socket:Connect("127.0.0.1", 2077)
socket:SendCommand(json.encode(snapshot))         -- no \r\n in string
```

**Python server (`server/bridge.py`):**
- Parse on `\r\n` boundaries
- Terminate every response with `\r\n`
- Start server before launching the game
- Stdlib `asyncio` only — no pip packages required

Repo: [rayshader/cp2077-red-socket](https://github.com/rayshader/cp2077-red-socket)  
Protocol: [bridge/bridge-protocol-v0.1.md](bridge/bridge-protocol-v0.1.md)

---

## AMM NPC spawn (Phase 2.5 — implemented)

Spawn goes through **Appearance Menu Mod**, not raw `Game.SpawnNPC()` in the current bridge mod.

Python sends a `BridgeCommand` with `command: "amm_spawn_npc"`. CET resolves the character via `AMM.API.GetAMMCharacters()` and calls `AMM.Spawn.SpawnNPC(...)`.

**Interactive testing** (from repo root):

```powershell
python server/bridge.py --port 2077 --interactive --quiet
```

| CLI command | Effect |
|-------------|--------|
| `ammchars [limit]` | Dump catalog names/records to CET console |
| `spawnname <id> <exact name>` | Spawn by AMM catalog **name** |
| `spawn [id] [record]` | Spawn by **record** string |
| `setapp [-d MS] <id> <appearance>` | Change appearance (optional delay) |
| `despawn <id>` | Remove tracked NPC |
| `list` | Show spawned registry |

Always run `ammchars` first on a fresh install — catalog names vary.

---

## NPC control (other verified patterns)

| Task | API |
|------|-----|
| Spawn (vanilla) | `Game.SpawnNPC("Character.xxx")` — prefer AMM path for bridge |
| Teleport entity | `Game.GetTeleportationFacility():Teleport(entity, pos, rot)` |
| Teleport player | `Game.TeleportPlayerToPosition(x, y, z)` |
| Hostility | `npc:GetAttitudeAgent():SetAttitudeGroup(CName.new("hostile"))` |
| Status effect | `StatusEffectHelper.ApplyStatusEffect(entity, "BaseStatusEffect.xxx")` |
| Look-at target | `Game.GetTargetingSystem():GetLookAtObject(player, false, false)` |

**Animations:** Workspot system — study [CyberScript](https://www.nexusmods.com/cyberpunk2077/mods/6475) and AMM source. No single one-liner.

**Do not use (fabricated):** `player:QueueMove()`, `npc:SetBehavior()`, `entity:Navigate()`.

---

## Observe hooks (event tap)

```lua
Observe('PlayerPuppet', 'OnAction', function(action)
  local name = Game.NameToString(action:GetName(action))
  -- filter and append to snapshot.events
end)
```

Find class/method names on NativeDB. Not all engine events are exposed.

---

## Logging

| Output | Location |
|--------|----------|
| `print("[Cypher] ...")` | CET overlay → Console tab |
| CET main log | `bin/x64/plugins/cyber_engine_tweaks/cyber_engine_tweaks.log` |
| Per-mod file (optional) | Write via `io.open` under mod folder |

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `module 'Cron' not found` | Wrong path | `Cron.lua` at mod root |
| `module 'cypher_json' not found` | Missing file | Copy `cypher_json.lua` to mod root |
| `require("json")` is nil | CET clash | Use `cypher_json.lua`, delete `json.lua` |
| Mod not loading | Bad nesting | Must be `mods/CypherAgent/init.lua` |
| Timers never fire | No `Cron.Update` | Add `onUpdate` handler |
| Game paused | CET overlay open | Close overlay while testing |
| RedSocket nil | Not installed | Re-extract RedSocket to game root |
| Connection refused | Server down | Start `python server/bridge.py` first |
| AMM nil | Not installed | Install Appearance Menu Mod |
| Spawn name not found | Wrong catalog string | Run `ammchars`, copy exact name |
| No JSON in console | Player nil | Load a save, get in-world |
| Syntax error | Lua typo | Check `cyber_engine_tweaks.log` |

---

## Performance

`Cron.Every(0.2, ...)` with lightweight reads + JSON encode is safe (~5 Hz). Do not poll heavy scans in `onUpdate` (60+ fps).

---

## Key links

| Resource | URL |
|----------|-----|
| NativeDB | https://nativedb.red4ext.com |
| CET Wiki | https://wiki.redmodding.org/cyber-engine-tweaks |
| CET Kit (Cron) | https://github.com/psiberx/cp2077-cet-kit |
| RedSocket | https://github.com/rayshader/cp2077-red-socket |
| Redmodding Discord | https://discord.gg/redmodding |
| CyberScript (NPC patterns) | https://www.nexusmods.com/cyberpunk2077/mods/6475 |

More links in [cypher-vision/archive/resources.md](../cypher-vision/archive/resources.md).
