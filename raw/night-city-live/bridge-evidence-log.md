# Milestone-0 Evidence Log

Use this log while running soak/bridge tests to confirm pass criteria.

## Environment

- **Functional verification date:** 2026-03-28 (in-game bridge + ACK + command path observed)
- **CP2077 build / version:** **2.31** (confirmed by user)
- **Pinned stack for 2.31** (from [RedSocket v0.5.0](https://github.com/rayshader/cp2077-red-socket/releases/tag/v0.5.0) release notes — adjust if your installed files differ):
  - **RedSocket:** **v0.5.0** — *“support patch 2.31”*
  - **RED4ext:** **v1.29.0+**
  - **redscript:** **0.5.27+**
  - **CET:** **v1.36.0+** required by RedSocket; **recommend latest [CET v1.37.1](https://github.com/maximegmd/CyberEngineTweaks/releases/tag/v1.37.1)** (or whatever current release targets 2.31 — verify in CET/Nexus description)
- **Installed CET / RedSocket build** _(optional: copy exact zip or Nexus version string from your `plugins` folder for a perfect audit trail)_
- **Mod path:** `...\Steam\steamapps\common\Cyberpunk 2077\bin\x64\plugins\cyber_engine_tweaks\mods\CypherAgent\`
- **Python:** 3.11 (path used: `C:\Users\bento\AppData\Local\Programs\Python\Python311\` — adjust if yours differs)
- **Bridge command (reference):** `python server/bridge.py --host 127.0.0.1 --port 2077 --command-every 25`

### Nexus mods installed (URLs you provided — pin these archives)

| Mod | Nexus | Version on page / file (as fetched 2026-03-28) | Your link |
| --- | --- | --- | --- |
| **Appearance Menu Mod (AMM)** | [mods/790](https://www.nexusmods.com/cyberpunk2077/mods/790) | **2.12.5** (from installed zip: `Appearance Menu Mod-790-2-12-5-1749642728.zip`). Nexus *description* may still say **2.11**; treat **artifact / Files tab** as source of truth. | [Description](https://www.nexusmods.com/cyberpunk2077/mods/790?tab=description) |
| **ArchiveXL** | [mods/4198](https://www.nexusmods.com/cyberpunk2077/mods/4198) | **1.26.3** — file **139905** (page: last updated 18 Mar 2026) | [Files → file 139905](https://www.nexusmods.com/cyberpunk2077/mods/4198?tab=files&file_id=139905) |
| **Codeware** | [mods/7780](https://www.nexusmods.com/cyberpunk2077/mods/7780) | **1.19.0** — file **134059** (page: last updated 26 Jan 2026) | [Files → file 134059](https://www.nexusmods.com/cyberpunk2077/mods/7780?tab=files&file_id=134059) |

**Notes**

- **AMM** on current CP2077 stacks often expects **ArchiveXL** / **Codeware** (and **RED4ext**) per each mod’s Nexus *Requirements*; your triplet matches that pattern.
- Nexus “headline version” and update notes blocks can lag newer **Files** uploads; **Vortex/Nexus zip names** typically encode `modId-major-minor-patch-timestamp`.

## Version pinning (before streams / long sessions)

Per project spec: pin CP2077 and mod stack so a surprise patch does not break CET/RedSocket between sessions.

- [ ] **Steam:** Cyberpunk 2077 → Properties → Updates → set to update only when launched, or note current build after verification.
- [ ] **Record** CP2077 build string in the Environment section above after next launch.
- [ ] **Record** CET + RedSocket versions above; keep the Nexus/GitHub installers or zip archives that match.
- [ ] **After a game patch:** re-run bridge smoke test (server up → launch game → ACK + one test command) before announcing a stream.

## In-game bridge session (2026-03-28) — closed on paper

**Result: PASS** for Milestone-0 wire goals (snapshot → Python → ACK → command → CET handler).

**CET console (observed):**

- Continuous `[Cypher]` lines with `schema_version` `scene_snapshot.v0.1`, incrementing `tick_id`, `timestamp_ms`, `player`, `events`.
- Matching `[Cypher ACK] tick_id=…` after snapshots.
- Test command path: `[Cypher COMMAND RECEIVED] id=…`, `[Cypher CMD] … target=observer action=log_marker`, `[Cypher CMD PAYLOAD] {"marker":"bridge_test_command","sequence":…}` (e.g. `cmd-3`).

**Python bridge console (observed):**

- Lines of the form `[bridge] snapshot tick=<n> acked mps≈4.94` (consistent with ~200 ms poll ≈ 5 Hz).
- Periodic `[bridge] test_command_sent id=cmd-<n>` (~every 25 valid snapshots with default `--command-every 25`).

**Operational note:** Port `2077` was in use once (Errno 10048); resolved by identifying `LISTENING` PID via `netstat -ano | findstr :2077` and ending the stale process before restarting the bridge.

## Test 1: Observer Soak (15 min)

- Start time: _(optional formal run)_
- End time: _(optional formal run)_
- Poll interval: 0.2 s (200 ms)
- Repeated runtime errors observed? **N** during 2026-03-28 bridge session (no errors reported in captured session)
- Average JSON cadence near 5Hz? **Y** (bridge ~4.94 mps)
- Result: **PASS** (operational during extended bridge use) / formal 15 min timed soak: _optional_
- Notes: Full timed 15 min soak still recommended for regression baseline after next game or mod update.

## Test 2: One-Way Snapshot Parse (>=500)

- **Synthetic harness:** 200 snapshots, 0 parse failures, 0 invalid — **PARTIAL** (target was ≥500; can re-run with larger batch).
- **In-game:** Python accepted sustained stream (e.g. ticks into 700+ range) with continuous ack path — **PASS** for CET-as-source transport.
- Bridge command used: `python server/bridge.py --host 127.0.0.1 --port 2077 --command-every 25` (or `--quiet` variant)

## Test 3: Two-Way ACK (5 min)

- **Synthetic:** 200 ACKs / 200 snapshots, 0 mismatches at client — **PASS**
- **In-game:** CET showed `[Cypher ACK] tick_id=…` in lockstep with snapshots — **PASS**
- Expected mismatch count: 0

## Test 4: Command Envelope Proof

- **Synthetic:** Commands received without parse errors — **PASS**
- **In-game:** CET handler logs for `COMMAND RECEIVED`, `CMD`, `CMD PAYLOAD` — **PASS** (e.g. `cmd-3`; bridge also logged `cmd-31`, `cmd-32`, etc.)

## Exit Gate (Milestone-0)

- [x] Observer stable during bridge session (formal 15 min optional)
- [x] One-way snapshot transport (in-game sustained + synthetic parser)
- [x] Two-way ACK transport (in-game + synthetic)
- [x] One command envelope round-trip (in-game + synthetic)

**Next planning gate (updated 2026-04-04):** Milestone 0.5 **in-world NPC spawn via bridge** is **verified** (see § AMM adapter below). **Milestone 0.6** (multi-actor offsets + deferred `setapp`) is implemented in code — verify in-game when convenient. Next: animation / weather commands, scene script batching per roadmap.

---

## AMM adapter & spawn ground truth (2026-03-30 — 2026-04-04)

### What we learned (engineering)

| Topic | Outcome |
| --- | --- |
| **`AMM.API` vs `AMM.Spawn`** | On AMM 2.12+, `AMM.API` is **Collabs/API.lua** only (appearances, `GetAMMCharacters`, etc.). NPC spawn is **`AMM.Spawn:NewSpawn` → `AMM.Spawn:SpawnNPC`**, same as the in-game Spawn tab pipeline ([AMM `API.lua`](https://github.com/MaximiliumM/appearancemenumod/blob/main/Release/bin/x64/plugins/cyber_engine_tweaks/mods/AppearanceMenuMod/Collabs/API.lua), [AMM `spawn.lua`](https://github.com/MaximiliumM/appearancemenumod/blob/main/Release/bin/x64/plugins/cyber_engine_tweaks/mods/AppearanceMenuMod/Modules/spawn.lua)). |
| **Cross-mod SQLite `db`** | CypherAgent cannot rely on querying AMM’s `entities` table via a global `db`; CET mod scopes differ → **`no such table: entities`** when called from another mod. |
| **`exEntitySpawner` / `PreventionSpawnSystem`** | On the verified CP2077 2.31 + CET stack, logs showed both **unavailable** from Cypher’s context; **`DynamicEntitySystem:CreateEntity`** returned a ref but did not yield a resolvable visible puppet for our poll loop. **Primary path abandoned** in favor of AMM-native spawn. |
| **`GetAMMCharacters()` scope** | Per AMM source, this lists rows where `entity_path LIKE '%_character%'` (not “all TweakDB `Character.*`”). On the user’s install, **`ammchars` reported `total=19`** — mostly `AMM_Character.*` plus a few specials (e.g. `Custom_MM_Character.juby`), **not** open-world gang NPCs like Maelstrom grunts unless AMM’s DB includes them. |
| **Stale `logical_id`** | If spawn failed but registry kept `npc_test`, later `spawn` commands were skipped. **Fix:** replace stale entries when no live entity handle exists. |

### Verified in-game (2026-04-04)

- **Command:** bridge interactive `spawnname` → CET `amm_spawn_npc` with `character_name` matching AMM catalog (e.g. **Johnny Silverhand**).
- **Resolved record:** `AMM_Character.Silverhand` (from catalog).
- **CET log:** `[Cypher] spawn queued logical_id=npc_test character=AMM_Character.Silverhand` → `[Cypher] spawn complete logical_id=npc_test`.
- **World:** Johnny Silverhand puppet visible in front of V (screenshot captured).

### Catalog snapshot (user install, 2026-04-04)

`amm_list_characters` / `GetAMMCharacters()` enumerated **19** entries, including (abbrev.):

- E3 V Female / Male → `AMM_Character.E3_V_Female`, `AMM_Character.E3_V_Male`
- Hanako, Johnny Silverhand, Judy (as **Juby**), Rache Bartmoss, Song So Ri / Songbird
- Multiple **Nibbles** pose variants → `AMM_Character.Nibbles*`

**Implication:** default CLI `spawn` using `Character.gang_maelstrom_melee_w_hard` **fails catalog validation** on this install until/unless that record appears in `GetAMMCharacters()`. Use **`ammchars`** then **`spawnname <logical_id> <exact AMM name>`** or pass a known-good **`character_id`** from the printed list.

### Bridge / Cypher commands added (for reproducibility)

| Surface | Command / action |
| --- | --- |
| Python `--interactive` | `ammchars [limit]`, `spawnname <logical_id> <name...>`, `setapp`, `spawn`, `despawn`, `list` |
| CET handler | `amm_list_characters`, `amm_spawn_npc`, `amm_set_appearance`, `amm_despawn_npc`, `amm_list_npcs` |

### References (source of truth)

- AMM `GetAMMCharacters` SQL: `Collabs/API.lua` in [appearancemenumod](https://github.com/MaximiliumM/appearancemenumod).
- AMM spawn implementation: `Modules/spawn.lua` (`NewSpawn`, `SpawnNPC`, `DynamicEntitySpec`, `Cron` poll for `Game.FindEntityByID`).

---

## Milestone 0.6 — Multi-actor offsets & appearance timing (implemented)

**Goal:** Stage two (or more) catalog NPCs without stacking on the same world point; run `ChangeAppearance` after spawn without racing the AMM attach.

| Change | Detail |
| --- | --- |
| **`payload.right_m`** | Lateral meters along horizontal right (`forward × Z-up`). Combined with `forward_m` for teleport after `SpawnNPC`. |
| **Python CLI** | `spawn` / `spawnname` accept optional prefix flags `-f M` and `-r M` per line; defaults also from `--forward-m` and **`--right-m`**. |
| **`amm_set_appearance.delay_ms`** | If set, CET logs `amm_set_appearance scheduled …` and applies appearance after `Cron.After(delay_ms/1000)`. |
| **Bridge `setapp`** | `setapp [-d MS] <logical_id> <appearance>` |

**Suggested in-game check:** `spawnname -r -1.5 npc_l Johnny Silverhand` then `spawnname -r 1.5 npc_r Hanako` (adjust names to your `ammchars` list), confirm two puppets separated. Then `setapp -d 800 npc_l <valid_appearance>` and watch CET for scheduled + success lines.

**Catalog preflight (implemented):** `server/catalog.py` + `--catalog` / `--catalog-strict` on `bridge.py`; verification matrix in `docs/bridge/catalog-verification.md`; example allowlist `catalog/curated.v1.example.json`. Use `check spawnname …` and `cmdjson {…}` in interactive mode to dry-run before live sends.

**Full Spawn-tab catalog (implemented):** `server/export_amm_spawn_catalog.py` reads **`AppearanceMenuMod/db.sqlite3`** (same `entities` / categories as AMM Spawn UI). CET action **`amm_list_appearances`** + bridge **`ammapps <record>`** lists appearance strings via **`AMM.API.GetAppearancesForRecord`**. Interactive **`spawn`** with **`--allow-direct-record`** sets **`try_direct_record`** so spawns work for `entity_path` values **not** returned by **`GetAMMCharacters()`** / `ammchars`.
