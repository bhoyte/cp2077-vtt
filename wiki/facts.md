---
type: register
title: Facts register — engine, mods, vendors, host
status: active
updated: 2026-10-11
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
evidence: raw/night-city-live/bridge-evidence-log.md (2026-03-28 session: ~4.94 msg/s snapshots, ACKs, command envelopes)
note: JSON lines, `\r\n` delimiter, game is TCP client, Python is server on 127.0.0.1:2077.

### F-002 — RedSocket needs RegisterListener before Connect, no `\r\n` inside payloads, and the server up before Connect
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/HANDOFF-2026-06.md; raw/env/host-audit-2026-10-11.md (log: "RedSocket connection failed" when bridge absent)
note: Whether a failed socket can simply Connect() again (auto-reconnect) is untested → S-04.

### F-003 — In CET, `require("json")` is unreliable; bundle rxi/json as `cypher_json.lua`; `Cron.lua` must sit at mod root
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/03-CET-MOD-REFERENCE.md

### F-010 — The CET overlay being open pauses the game
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/HANDOFF-2026-06.md
note: Operations must never require the overlay during a show.

## Spawning & puppetry

### F-004 — Our CET mod can spawn NPCs through AMM (`AMM.Spawn:NewSpawn` → `SpawnNPC`), change appearance, and despawn
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/bridge-evidence-log.md (2026-04-04: Johnny Silverhand puppet visible)

### F-005 — Arbitrary entity records (e.g. gang NPCs) spawn via `try_direct_record`
status: claimed
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/bridge-evidence-log.md (implemented; in-game verification not recorded)
note: `GetAMMCharacters()` only lists ~19 `_character` rows; gang categories exist in AMM's DB (Maelstrom 20, Tyger Claws 19, …). S-02 must verify.

### F-006 — From CypherAgent's context, `exEntitySpawner` was unavailable and `DynamicEntitySystem:CreateEntity` produced no visible puppet
status: claimed
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/bridge-evidence-log.md
note: CONTRADICTS F-007 (AMM itself calls `exEntitySpawner.Spawn` successfully). Likely a call-timing or usage issue. Resolve in S-01.

### F-007 — AMM's free camera = spawned `base\entities\cameras\simple_free_camera.ent`; component "camera" supports Activate(blend)/Deactivate(blend)/SetFOV/SetZoom/SetLocalOrientation; moved via TeleportationFacility
status: source-read
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/amm/camera.lua
note: Activation also calls `Util:AddPlayerEffects()` + `Tools:ToggleHead()` (hides V). Deactivation re-activates the player FPP camera. Foundation of S-01.

### F-008 — Any entity can be teleported with `Game.GetTeleportationFacility():Teleport(entity, Vector4, EulerAngles)`
status: source-read
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/amm/camera.lua (Camera:Move); raw/night-city-live/03-CET-MOD-REFERENCE.md

### F-012 — AMM's DB holds 4,363 entities (incl. 103 "FX & Effects", 37 weapons), 30,069 appearances, 43,765 workspots, 142 photo-mode poses, 121 locations
status: source-read
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/amm_universe_summary.md (D:\night-city-live\catalog\amm_universe.sqlite)

### F-013 — AMM modules expose FreezeNPC, ActivateFacialExpression, ActivateLookAt, ToggleInvisibility, SetGodMode, EquipGivenWeapon, PlayAnimationOnTarget, SetWeather, SetTime, TriggerCombatAgainst
status: claimed
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/night-city-live/perplexity-deep-search-brief.md (parsed from AMM source; never exercised)
note: Each must be source-read then verified in S-02/S-03 before use in beats.

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

### F-019 — Launching `bin\x64\Cyberpunk2077.exe` directly (Steam running) starts the game without Steam applying a pending update
status: hypothesis
scope: none
evidence: none yet
note: If true, a full game-folder backup on D: is a real rollback path without GOG (Q-03). Test in Phase 0.

## Host

### F-017 — The uninstall left the mod layer in the Steam game folder but removed redscript (`engine\` gone)
status: verified
scope: cp2077-2.31 / cet-1.37.1 / red4ext-1.30.0 / codeware-1.19.0 / archivexl-1.26.3 / amm-2.12.5 / redsocket-0.5.0
evidence: raw/env/host-audit-2026-10-11.md

### F-018 — Host: RTX 3060 Ti 8 GB, Ryzen 5 5600, 16 GB RAM; C: 101 GB free, D: 3.4 TB free; OBS not installed
status: verified
scope: host-2026-10-11
evidence: raw/env/host-audit-2026-10-11.md
