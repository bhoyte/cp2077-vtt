---
type: register
title: Facts register — engine, mods, vendors, host
status: active
updated: 2026-10-14
stack: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
---

# Facts register

Ladder: hypothesis → claimed → documented → source-read → verified (or refuted). A fact whose `scope` ≠ `stack` above is stale.
Spikes move facts up or down this ladder. Never cite a fact above its status.
Source summaries: [night-city-live](sources/src-night-city-live.md) · [vendors and host](sources/src-vendor-and-host.md).

## Transport & CET runtime

### F-001 — RedSocket TCP bridge works both directions between CET and a Python asyncio server
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/bridge-evidence-log.md (2026-03-28); raw/evidence/2026-10-11-phase0-smoke.md (re-verified after C: reinstall)
note: JSON lines, `\r\n` delimiter, game is TCP client, Python is server on 127.0.0.1:2077.

### F-002 — RedSocket needs RegisterListener before Connect, no `\r\n` inside payloads, and the server up before Connect
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/HANDOFF-2026-06.md; raw/env/host-audit-2026-10-11.md (log: "RedSocket connection failed" when bridge absent)
note: A failed first Connect does not retry by itself. Reloading CypherAgent while a server is listening does connect (2026-10-11). `IsConnected` stayed true after the peer died (2026-10-13 00:00). ArcadeLink's redial is F-029.

### F-003 — In CET, `require("json")` is unreliable; bundle rxi/json as `cypher_json.lua`; `Cron.lua` must sit at mod root
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/03-CET-MOD-REFERENCE.md

### F-010 — The CET overlay being open pauses the game
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/HANDOFF-2026-06.md
note: Operations must never require the overlay during a show. On 2026-10-12 the world clock still advanced and CET `onUpdate` still ran spawns while the overlay was open (raw/evidence/2026-10-12-s02-roof-cast.md).

## Spawning & puppetry

### F-004 — Our CET mod can spawn NPCs through AMM (`AMM.Spawn:NewSpawn` → `SpawnNPC`), change appearance, and despawn
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/bridge-evidence-log.md (2026-04-04); raw/evidence/2026-10-11-phase0-smoke.md (`spawn complete logical_id=npc_test`)

### F-005 — Arbitrary entity records (e.g. gang NPCs) spawn via `try_direct_record`
status: claimed
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/bridge-evidence-log.md (implemented; in-game verification not recorded)
note: `GetAMMCharacters()` only lists ~19 `_character` rows; gang categories exist in AMM's DB (Maelstrom 20, Tyger Claws 19, …). S-02 must verify.

### F-006 — Our mod can spawn `simple_free_camera.ent` with `exEntitySpawner.Spawn` and resolve the `camera` component in a loaded save
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-11-s01-camera-run2.md
note: "Unavailable from CypherAgent" is refuted. onInit and after the player exists, `exEntitySpawner` is userdata and `Spawn` is a function. 22:16 loaded save: three ids `10031371ULL`–`10031373ULL`, component found in about 1 s. An earlier pass at 22:05 timed out at 2 s; treat that as a miss, not the rule. `ToEulerAngles{roll,pitch,yaw}` works. `DynamicEntitySystem:CreateEntity` was not retested.

### F-007 — AMM's free camera = spawned `base\entities\cameras\simple_free_camera.ent`; component "camera" supports Activate(blend)/Deactivate(blend)/SetFOV/SetZoom/SetLocalOrientation; moved via TeleportationFacility
status: source-read
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/amm/camera.lua
note: Activation also calls `Util:AddPlayerEffects()` + `Tools:ToggleHead()` (hides V). Deactivation re-activates the player FPP camera. Foundation of S-01.

### F-008 — Any entity can be teleported with `Game.GetTeleportationFacility():Teleport(entity, Vector4, EulerAngles)`
status: source-read
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/amm/camera.lua (Camera:Move); raw/night-city-live/03-CET-MOD-REFERENCE.md; raw/evidence/2026-10-11-s01-camera.md (player only: park 5/30/80/150 m returned ok)
note: On 2026-10-12 the same call returned ok on three fresh AMM puppets and did not move them. They stayed at the shared spawn point for 2.4 s of retries (raw/evidence/2026-10-12-s02-separate.md). NPC placement that did move them is F-028.

### F-012 — AMM's DB holds 4,363 entities (incl. 103 "FX & Effects", 37 weapons), 30,069 appearances, 43,765 workspots, 142 photo-mode poses, 121 locations
status: source-read
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/amm_universe_summary.md (D:\night-city-live\catalog\amm_universe.sqlite)

### F-013 — AMM 2.12.5 exposes FreezeNPC, ActivateFacialExpression, ActivateLookAt, ToggleInvisibility, SetGodMode, EquipGivenWeapon, PlayAnimationOnTarget, SetTime, and TriggerCombatAgainst; there is no AMM `SetWeather`
status: source-read
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-12-s02-amm-source.md
note: Not exercised in-game. `AMM.Tools` and `AMM.Poses` are on the AMM table. `Util` is a bare global (`Util = require('Modules/util.lua')`); `AMM.Util` is nil (S-01). Signatures: `Tools:FreezeNPC(handle, freeze)` → time dilation `radialMenu` 0.0, plus workspot stop/replay; `Tools:ActivateFacialExpression(target, face)` → `ResetFacial` then `ApplyFeature("FacialReaction")` (`face.category`, `face.idle`); `Tools:ActivateLookAt()` → `Util:NPCLookAt` (needs `Tools.currentTarget` / `lookAtTarget` / `selectedLookAt`); `Tools:ToggleInvisibility()` → `Game.GetPlayer():SetInvisible` (player only); `Util:SetGodMode(entity, immortal)` → `GodModeSystem` Clear + Add (`Immortal`/`Mortal`) — not `Tools:ToggleGodMode`; `Util:EquipGivenWeapon(puppet, tdbid, override)` → `AIEquipCommand` on `AttachmentSlots.WeaponRight` (`override` unused; callers then `EquipPrimaryWeaponCommand`); `Poses:PlayAnimationOnTarget(t, anim, instant, caller)` → spawn `anim.ent`, `PlayInDeviceSimple`, `SendJumpToAnimEnt`; `Tools:SetTime(minutes)` → `SetGameTimeByHMS`; `Util:TriggerCombatAgainst(handle, target)` → mutual `AIA_Hostile` + `TriggerCombat`. Weather is F-025. Friendly/neutral is F-026, not TriggerCombatAgainst.

### F-025 — Weather is `Game.GetWeatherSystem():SetWeather(cname, 10.0, 5)` from `Tools:DrawTimeActions`, not an AMM function named SetWeather
status: source-read
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-12-s02-amm-source.md
note: `Tools:new` sets `Tools.weatherSystem = Game.GetWeatherSystem()`. The combo path passes `weather.cname` and calls `ResetWeather(true)` when `cname == "reset"`. Gated on `AMM.CodewareVersion >= 4`. The time-slider branch passes the option table instead of `cname`. Cname list is in the evidence file.

### F-026 — `Tools:SetNPCAttitude(entity, attitude, target, group)` sets an NPC's attitude group and attitude towards a target
status: source-read
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-12-s02-amm-source.md
note: `entity` is an AMM target (`entity.handle`). `target` defaults to the player. `group` defaults to that target's attitude group. Next calls: `SetAttitudeGroup` and `SetAttitudeTowards`. This is the neutralize path for S-02. `Util:TriggerCombatAgainst` forces hostile instead.

### F-011 — Spawned entities do not persist across save/load
status: claimed
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/perplexity-deep-search-brief.md
note: Design assumes it regardless (declarative restage, ADR-003).

### F-009 — The world streams (LOD, NPCs, collision) around the player, not the active camera
status: hypothesis
scope: none
evidence: none yet
note: If true, V must be parked near every soundstage while cameras look elsewhere. S-01.

## Vendors & platform

### F-014 — Patch 2.31 is still the current CP2077 version, and CET 1.37.1 supports it
status: documented
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/web/cp2077-compat-2026-10-11.md

### F-015 — Jev `choice` picks among ≤255 labelled options and returns calibrated probabilities + confidence; ~US$0.00003 per small call
status: documented
scope: jev-1.13.0
evidence: raw/web/typesafe-jev-2026-10-11.md
note: Latency (spec claims 70–150 ms) not documented → S-07.

### F-016 — Twitch viewers see the stream several seconds behind real time, even in low-latency mode
status: hypothesis
scope: none
evidence: none yet
note: Drives vote-window compensation (ADR-010). Measure in S-06.

### F-019 — Launching `bin\x64\Cyberpunk2077.exe` directly with Steam running starts the game
status: verified
scope: host-2026-10-11
evidence: raw/evidence/2026-10-11-stack-freeze.md
note: 2026-10-11 21:25: exe started, RED4ext 1.30.0 + 3 plugins on 2.31, Steam LastUpdated unchanged. There was no pending update (`buildid` == `TargetBuildID`), so "skips a forced Steam update" is still untested.

## Host

### F-017 — Community redscript v0.5.31 is installed at `engine\tools\scc.exe` (+ `scc_lib.dll`, `scripts.ini`, `r6\config\cybercmd\scc.toml`)
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/env/redscript-restore-2026-10-11.md
note: Compile observed 2026-10-11 (`r6\logs\redscript_rCURRENT.log`, RED4ext "scc invoked successfully"). Zip kept at `D:\cp2077-stack\redscript-v0.5.31-windows.zip`.

### F-018 — Host (morning 2026-10-11): RTX 3060 Ti 8 GB, Ryzen 5 5600, 16 GB RAM; C: 101 GB free, D: 3.4 TB free; OBS not installed
status: verified
scope: host-2026-10-11
evidence: raw/env/host-audit-2026-10-11.md
note: Disk free space superseded by F-021 after the C: install.

### F-020 — CP2077 2.31 is installed at `C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077` (91 GB); Phantom Liberty depot present; April mod layer survived in-place
status: verified
scope: host-2026-10-11
evidence: raw/env/host-audit-2026-10-11-c-install.md
note: exe ProductVersion 2.31. Steam AutoUpdateBehavior is now 1 (only update when launched; observed 2026-10-11 21:00). CET, AMM, CypherAgent, RedSocket, RED4ext, ArchiveXL, Codeware, `archive\pc\mod` still present.

### F-021 — C: is a 1 TB Kingston NVMe SSD (51 GB free); D: is a 4 TB Toshiba USB HDD (3.4 TB free)
status: verified
scope: host-2026-10-11
evidence: raw/env/host-audit-2026-10-11-c-install.md
note: Overturns the space-only reason in ADR-011. Live game stays on C: (ADR-012). 51 GB free is tight for pagefile + Steam verify — backups go to D:, not a second copy on C:.

### F-022 — OBS Studio 32.2.2 is installed at `C:\Program Files\obs-studio\bin\64bit\obs64.exe`
status: verified
scope: host-2026-10-11
evidence: Start Menu shortcut `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OBS Studio.lnk` → that exe; FileVersion 32.2.2 (2026-08-23)
note: Newer than the unused 32.0.4 installer on D:\. Not yet run against CP2077 capture (S-05).

### F-023 — `SettingsSystem:GetVar("/interface", "hud")` asserts and crashes the game
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-11-s01-camera.md (RED4ext 21:59:40, `inGameConfigGroup.cpp:76`)
note: `pcall` does not catch it. There is no safe HUD-off call yet; S-01 checks the HUD by eye.

### F-028 — `AMM.Tools:TeleportNPCTo` places a fresh AMM puppet on a world mark
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-12-s02-aitp.md
note: `AITeleportCommand` with `doNavTest = false`. Johnny, Hanako, and Song So Ri each reported distance 0.00 to a different mark, then held that position through pose and freeze. V stayed at -1536.78, 1195.77, 57.00. The facility teleport in F-008 did not do this.

### F-029 — ArcadeLink redials the booth after the pings stop, without a CET reload
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-13-session-redial.md
note: Version 0.1.2. Booth sends a ping each second. After the booth process was killed, the log showed `link down quiet=3.4` at 02:23:59 and `connected` plus hello at 02:24:07. No reload between them. `status` returned player -1536.78, 1195.77, 57.00. Actors empty. The roof cast was not commanded.

### F-027 — Three AMM characters can be posed and frozen beside V without moving V
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-12-s02-roof-cast.md
note: First passes stacked them at AMM's shared 1 m spawn (raw/evidence/2026-10-12-s02-separate.md). 21:54 pass with `Tools:TeleportNPCTo` put them on three marks and the freeze kept those coordinates (raw/evidence/2026-10-12-s02-aitp.md). Player unmoved.

### F-030 — ArcadeLink `place` with character-list names puts those people on marks in front of V
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-13-place-names.md; raw/evidence/2026-10-13-place-file.md; raw/evidence/2026-10-13-place-wedge.md; raw/evidence/2026-10-14-sequence.md
note: Version 0.1.4 stood them side by side, about 1.6 m apart. Version 0.1.5, 22:01, placed the three in single file; the user frame shows Johnny nearest, then Hanako, then Song So Ri. Version 0.1.6, 22:12, moved the same three into a wedge. Johnny is the point, about 7.51 m along V's facing. Hanako is 0.80 m to V's left and Song So Ri 0.80 m to her right, both about 1.39 m further out. Each pair is about 1.60 m apart. V stayed at -1536.79, 1194.84, 57.01. The wedge sat three steps of 1.6 m further than the usual 2.7 m point, because the nearer marks were already taken by the file. The user frames show that wedge, and other bodies still standing farther down the roof. They were not posed or frozen. Version 0.1.12, 00:03 on 2026-10-14, placed one slot at a time with the roof empty. Rank, file, and wedge all landed on the unshifted marks: center and point and the near file mark at about 2.70 m, neighbors about 1.60 m. V stayed at -1536.84, 1194.00, 57.01.

### F-031 — ArcadeLink `clear` removes only the appearance menu's live spawn list; after a mod reload that list was empty
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-13-clear.md; raw/evidence/2026-10-14-sequence.md
note: Version 0.1.8, 23:21. Reply `removed` was empty. The menu's saved `spawnedNPCs` list also had length 0. V was at -1536.39, 1196.02, 57.00 in the reply. Version 0.1.9, 23:36, wrote `tagged.json` for the three. After another reload at 23:37, hello had no actors, and `clear` at 23:38 removed Hanako, Song So Ri, and Johnny Silverhand with `missed` empty. The tag file was `[]` afterward. V stayed at -1540.39, 1200.91, 57.00. No frame after the clear. Version 0.1.12, 00:03 on 2026-10-14, cleared one menu-listed person nine times in a row. Each reply named that person, `missed` was empty, and the tag file ended `[]`. A clear just before that, after a reload, removed Johnny Silverhand from the tag file while the menu list was empty.

### F-024 — An activated `simple_free_camera.ent` replaces the player view and holds a distinct angle; the game HUD stays drawn on top
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/evidence/2026-10-11-s01-roof-prelim.md
note: Roof, 2026-10-11 22:46–22:50. Four frames, four angles. V's body is visible when she stands in the shot. Minimap, quest text, weapon prompts, and a cyan crosshair remain. Hide-V was not applied on this pass.
