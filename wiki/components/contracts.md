---
type: component
title: Contracts — scene manifest v2, StageSpec, beats, wire protocol stage.v1, events
status: draft
updated: 2026-10-13
depends_on: [ADR-002, ADR-003, ADR-006, ADR-007]
---

# Contracts

Pydantic models are the source of truth once code exists (ADR-008). This page is the human-readable spec; keep it in sync.

## 1. Scene manifest v2 (`content/scenes/<scene_id>.json`)

Changes vs spec v1: nodes declare **affordances** (tags), not action lists; cameras are entities with blend presets;
there's a `player_park` point (F-009, R-03); actor slots are separated from nodes; edges give range bands.

```json
{
  "scene_id": "totentanz_balcony",
  "location": {"district": "Watson", "teleport": [-1120.4, 1540.2, 42.1]},
  "player_park": {"pos": [-1131.0, 1552.0, 38.5], "note": "under stairs, outside every camera frustum"},
  "world": {"weather": "AcidRain", "hour": 23, "minute": 40, "crowd": "suppress"},
  "nodes": {
    "n_railing":  {"pos": [-1120.4, 1540.2, 42.1], "yaw": 180, "tags": ["cover:half", "vantage"]},
    "n_terminal": {"pos": [-1124.8, 1543.1, 42.1], "yaw": 90,  "tags": ["console:lights", "console:turret"]},
    "n_bar":      {"pos": [-1117.9, 1548.6, 42.1], "yaw": 0,   "tags": ["cover:full"]}
  },
  "edges": [["n_railing", "n_bar", "mid"], ["n_railing", "n_terminal", "close"]],
  "slots": {
    "party":   {"Solo": "n_railing", "Netrunner": "n_terminal", "Tech": "n_bar", "Face": "n_bar"},
    "enemies": [{"id": "boss_royce", "tier": "Boss", "record": "Character.xxx", "appearance": "…", "node": "n_bar"}]
  },
  "cameras": {
    "cam_wide":      {"pos": [-1115.0, 1535.0, 48.0], "rot": [-35, 25, 0], "fov": 70},
    "cam_ots_solo":  {"pos": [-1121.2, 1538.8, 42.7], "rot": [-5, 175, 0], "fov": 45, "follow": "Solo"},
    "cam_react_boss":{"pos": [-1120.0, 1546.0, 42.5], "rot": [0, -10, 0],  "fov": 35}
  }
}
```
Rotations are `[pitch, yaw, roll]` in degrees. Cameras with `follow` are re-derived relative to that actor's node when actors move.

## 2. StageSpec (desired baseline, orchestrator → reconciler)

```json
{"scene_id": "totentanz_balcony", "rev": 42,
 "world": {"weather": "AcidRain", "hour": 23, "minute": 40},
 "player_park": [-1131.0, 1552.0, 38.5],
 "actors": {"solo": {"record": "…", "appearance": "…", "node": "n_railing", "pose": "aim_crouch", "weapon": "rifle", "state": "alive"},
            "boss_royce": {"…": "…", "state": "dead"}},
 "active_camera": "cam_wide"}
```

## 3. Beat timeline (orchestrator → CET, played locally with Cron)

```json
{"beat_id": "b_000317", "template": "ranged.headshot.kill", "duration_ms": 4300,
 "ops": [
  {"t": 0,    "op": "camera.cut",  "cam": "cam_ots_solo", "blend": 0},
  {"t": 0,    "op": "actor.pose",  "actor": "solo", "pose": "aim_stand"},
  {"t": 650,  "op": "fx.spawn",    "fx": "muzzle_rifle", "at": "solo:weapon"},
  {"t": 650,  "op": "cue",         "name": "sfx.rifle_shot"},
  {"t": 700,  "op": "camera.cut",  "cam": "cam_react_boss", "blend": 0},
  {"t": 760,  "op": "actor.kill",  "actor": "boss_royce", "style": "ragdoll"},
  {"t": 2600, "op": "camera.cut",  "cam": "cam_wide", "blend": 1.4}
 ],
 "end_state": {"actors": {"boss_royce": {"state": "dead"}}}}
```
`cue` ops are forwarded to the overlay/OBS (audio and banners live outside the game). Unknown ops are logged and skipped, never fatal.

## 4. Wire protocol `stage.v1` (TCP JSON lines, ADR-002)

Envelope: `{"type": "cmd" | "ack" | "report", "v": "stage.v1", "id": "...", "op": "...", "args": {...}}`

| Direction | op | Purpose |
|---|---|---|
| → game | `ping` | Liveness / RTT |
| → game | `scene.load` | Teleport V to `player_park`, set world, spawn the camera rig |
| → game | `actor.ensure` / `actor.remove` | Idempotent per actor (record, appearance, node, pose, weapon, state) |
| → game | `camera.cut` | `{cam, blend}` outside beats (windows, holds) |
| → game | `beat.play` | Timeline above |
| → game | `scout.mark` | Authoring: capture current V or free-camera transform |
| ← game | `hello` | `{mod_version, game_version, amm_version}` on connect |
| ← game | `ack` | `{id, ok, error?}` for every cmd |
| ← game | `report.actors` | Actual registry `{logical_id: {exists, pos, state}}` every 1 s and on change |
| ← game | `report.beat` | `{beat_id, status: done | failed, failed_ops: [...]}` |
| ← game | `report.heartbeat` | 1 Hz: `{fps, player_pos, active_camera}` |

## 5. Ledger events (ADR-007), selection

Show layer: `session.started{commit}` · `squad.joined` · `window.opened{slot, options}` · `vote.cast{user, option, layer, conf}` ·
`window.closed{tally, winner, tiebreak?}` · `roll{i, purpose, faces, value}` · `character.created` · `beat.played{beat_id, status}` ·
`stage.desynced` · `operator.action` · `session.ended{seed}`

B2 slice (`arcade/show`, `arcade/intent`): the clock emits
`window.opened{slot, seat, options, viewer_close_at, server_close_at, open_seat}`,
`window.extended{slot, viewer_close_at, server_close_at}`,
`vote.cast{user, option, layer, conf, slot}`,
`window.closed{slot, tally, winner, tied, reason}` with `reason` of `timer` or `locked_in`.
`tied` is true when at least one vote is in and no option leads. The tie-break roll is not drawn in this slice.

Rules layer (implemented, `arcade/rules/events.py`; folding them over the starting encounter reproduces its state exactly):
`encounter.started` · `initiative.rolled` · `initiative.set{order}` · `round.started` · `heat.rose` · `turn.started` ·
`attack.rolled` / `check.rolled{natural, extra, modifier, total, dv, success}` · `damage.applied{dice, raw, location, sp, loss, chip, crit}` ·
`injury.added` · `bled` · `healed` · `status.changed{ALIVE|FLATLINING|DEAD|FLED}` · `death_save{roll, threshold, success}` ·
`stabilized` · `medkit.used` · `cover.changed` · `pinned` · `taunted` · `blackout` · `ability.used` · `held` · `action.spent` ·
`encounter.ended{victory|wipe|stalemate}`. Beat selection keys off these (e.g. `damage.applied` with `crit` → crit beat family).

## 6. Overlay state (orchestrator → overlay, WebSocket)
Full snapshot on connect, then JSON-patch deltas: `{phase, slot, timer{ends_at_viewer, server_close_at}, options[], tally{}, party[], enemies[], initiative[], dice?, banners[], comms[], commit}`.

## 7. Live session `table.v0` (ADR-013)

What the socket speaks now. `stage.v1` above waits. One JSON object per line, `\n` or `\r\n`. Game is the client. `tools/booth.py` is the server on `127.0.0.1:2077`.

`hello` (game → booth, on every attach):

```json
{"type":"hello","schema":"table.v0","mod":"ArcadeLink","version":"0.1.4","player":{"x":0,"y":0,"z":0,"facing_x":0,"facing_y":0},"actors":[]}
```

`player` is null when no pawn is loaded. `actors` lists whoever this session spawned and can still measure. Each actor is `{name, x, y, z}`. `name` is the character-list spelling. A row may include `error` when that person is missing or did not land on the mark.

`status` (listener → game), then the same shape back with the request id:

```json
{"type":"status","id":"b1"}
```

```json
{"type":"status","id":"b1","schema":"table.v0","mod":"ArcadeLink","version":"0.1.4","player":{"x":0,"y":0,"z":0,"facing_x":0,"facing_y":0},"actors":[{"name":"Hanako","x":0,"y":0,"z":0}]}
```

`place` (listener → game) takes `names`, the character-list spellings. One name puts that person in front of V. Several names put those people in a line, in the order given, about 1.6 m apart. V does not move. People not named are left where they are. A person already spawned under that name is moved, not copied. The reply uses the list's spelling in `name`, plus the measured position. A failed name has `error` and may include `matches` (up to five list spellings) when the name was ambiguous.

```json
{"type":"place","id":"b2","names":["Johnny Silverhand","Hanako"]}
```

```json
{"type":"place","id":"b2","schema":"table.v0","mod":"ArcadeLink","version":"0.1.4","player":{"x":0,"y":0,"z":0,"facing_x":0,"facing_y":0},"actors":[{"name":"Johnny Silverhand","x":0,"y":0,"z":0},{"name":"Hanako","x":0,"y":0,"z":0}]}
```

No `names`, or an empty list, replies with `"error":"say who"` and spawns nobody. An unknown name replies `"error":"not in catalog"` on that row. Several list hits reply `"error":"say which one"` and `matches`. A unique shorter name is accepted and the reply's `name` is the full list spelling.

`python tools/booth.py status` and `python tools/booth.py place "Hanako" "Johnny Silverhand"` send the request through the local control port `127.0.0.1:2078` and print the reply. Several names may also be one comma-separated argument.
