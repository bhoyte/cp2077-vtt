# Night City Live Bridge Protocol v0.1

This document defines the Milestone-0 wire contract between CET (`CypherAgent`) and the Python bridge.

## Transport

- Protocol: TCP
- Endpoint: `127.0.0.1:2077` (default)
- CP2077 side: RedSocket client
- Python side: TCP server
- Framing: one JSON message per line, delimited by `\r\n`

## Message Types

### 1) SceneSnapshot v0.1 (CET -> Python)

Required fields:

- `schema_version`: `"scene_snapshot.v0.1"`
- `tick_id`: integer, increments each poll
- `timestamp_ms`: integer epoch-like millisecond value
- `player`: object
  - `position`: `{x, y, z}` (stringified numeric values in current CET mod)
  - `facing`: `{x, y}`
  - `is_in_combat`: boolean
  - `is_dead`: boolean
- `events`: array

Example:

```json
{"schema_version":"scene_snapshot.v0.1","tick_id":41,"timestamp_ms":1711654838123,"player":{"position":{"x":"148.5","y":"265.6","z":"23.1"},"facing":{"x":"0.00","y":"0.01"},"is_in_combat":false,"is_dead":false},"events":[]}
```

### 2) BridgeAck v0.1 (Python -> CET)

Required fields:

- `type`: `"ack"`
- `schema_version`: `"bridge_ack.v0.1"`
- `status`: `"ok"`
- `tick_id`: integer copied from snapshot
- `received_at_ms`: integer timestamp

Example:

```json
{"type":"ack","schema_version":"bridge_ack.v0.1","status":"ok","tick_id":41,"received_at_ms":1711654838124}
```

### 3) BridgeCommand v0.1 (Python -> CET)

Safe command envelope used to prove routing (non-destructive):

- `type`: `"command"`
- `schema_version`: `"bridge_command.v0.1"`
- `id`: unique command id
- `target`: receiver target name
- `action`: command action string
- `payload`: object
- `issued_at`: integer timestamp

Example:

```json
{"type":"command","schema_version":"bridge_command.v0.1","id":"cmd-1","target":"observer","action":"log_marker","payload":{"marker":"bridge_test_command","sequence":1},"issued_at":1711654839000}
```

### 4) AMM adapter commands (Python → CET)

`target`: `"amm"`. CET keeps a **spawn registry** (`logical_id` → character + optional entity handle).

**`amm_spawn_npc`**

- `payload.logical_id` (required): stable name for later despawn / future anim target.
- `payload.character_id` (optional): spawn record (`entity_path`). Normally must match `AMM.API.GetAMMCharacters()`; if **`payload.try_direct_record`** is `true`, Cypher uses this string even when **not** in that list (for paths from AMM’s full `entities` DB — export via `server/export_amm_spawn_catalog.py`). Bridge: `--allow-direct-record` on interactive `spawn`.
- `payload.try_direct_record` (optional): see above; ignored for name-only resolution.
- `payload.character_name` (optional): exact **`name`** field from `GetAMMCharacters()` (bridge: `spawnname <logical_id> <name...>`). Case-insensitive match; does **not** use `try_direct_record`.
- `payload.forward_m` (optional): meters in front of player in the XY plane (default `3.0`); Z matches player foot height (same as pre-0.6 behavior).
- `payload.right_m` (optional): meters along the horizontal **right** vector (`forward × world_up`), default `0`. Negative values place the puppet to the player's left. Enables side-by-side multi-NPC staging without overlapping teleports.
- `payload.appearance` (optional): AMM appearance string passed as spawn parameters (`{ app = appearance }`).

Cypher uses AMM-native flow: resolve catalog via `AMM.API.GetAMMCharacters()` -> build `AMM.Spawn:NewSpawn(...)` -> call `AMM.Spawn:SpawnNPC(...)`.  
After handle resolves, Cypher teleports to `forward_m` / `right_m` offset.

Duplicate `logical_id`: if the old handle is still live, CET skips. If stale/no entity, CET replaces it and retries.

**`amm_despawn_npc`**

- `payload.logical_id` (required): removes registry entry; prefers `amm_spawn:Despawn()`, else `entity:Dispose()`.

**`amm_set_appearance`**

- `payload.logical_id` (required): target from spawn registry.
- `payload.appearance` (required): AMM appearance name.
- `payload.delay_ms` (optional): if `> 0`, CET schedules `ChangeAppearance` after `delay_ms` wall milliseconds via `Cron.After` (useful immediately after spawn while the puppet is still attaching).
- Uses `AMM.API.ChangeAppearance(entity, appearance)`.

**`amm_list_npcs`**

- `payload`: may be empty. CET prints all registry entries to console.

**`amm_list_characters`**

- `payload.limit` (optional, default `25`): max entries to print from AMM catalog.
- CET prints `name` + `record` pairs from `AMM.API.GetAMMCharacters()` to the CET log.

**`amm_list_appearances`**

- `payload.record` (required): `entity_path` / TweakDB-style record string (same field AMM uses for spawn, e.g. `AMM_Character.Silverhand`).
- `payload.custom` (optional): if `true`, uses AMM’s custom appearance path (`GetAppearancesForRecord(record, true)`); default `false` reads from AMM’s `appearances` SQLite table via the API.
- CET prints `appearance[i] <name>` lines to the log — these strings are valid inputs for `amm_set_appearance` / spawn `payload.appearance` when supported.

## Curated catalog (optional, Python-side)

The bridge may load a **`cypher_catalog.v1`** JSON file (`--catalog PATH`) to **reject** `amm_spawn_npc` / `amm_set_appearance` commands before they are sent, when the character or appearance is not in your stream allowlist. This does not replace CET/AMM validation; it prevents LLM or operator typos from burning stream time. See `docs/bridge/catalog-verification.md` and `catalog/curated.v1.example.json`.

## Validation Rules (Sprint)

- Python only treats messages as snapshots if:
  - JSON parse succeeds
  - `schema_version` matches `scene_snapshot.v0.1`
  - required top-level and player fields are present
- CET logs unknown message types and malformed JSON but does not crash.

## Acceptance Mapping

- Observer hardening: stable emission of `SceneSnapshot v0.1`
- One-way transport: Python parses 500+ consecutive snapshots
- Two-way ack: every valid snapshot receives parseable `BridgeAck v0.1`
- Command envelope proof: CET logs handler invocation for at least one `BridgeCommand v0.1`
- **Milestone 0.5 (AMM spawn):** bridge `amm_spawn_npc` (via `spawnname` or validated `character_id`) produces `[Cypher] spawn complete` and a visible puppet; catalog ground truth documented in `docs/bridge/bridge-evidence-log.md` § AMM adapter
- **Milestone 0.6 (multi-actor staging):** `right_m` and bridge `-f`/`-r` flags; optional `delay_ms` on `amm_set_appearance` for post-spawn appearance smoke tests
