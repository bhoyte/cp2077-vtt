---
type: component
title: Stage — the ArcadeStage CET mod, reconciler, scout tool
status: draft
updated: 2026-10-11
depends_on: [ADR-002, ADR-003, F-001, F-003, F-004, F-007, F-008, F-009]
---

# Stage

## ArcadeStage (CET mod, Lua)
Ported from CypherAgent (ADR-001). Files at mod root: `init.lua`, `Cron.lua`, `cypher_json.lua` (F-003).

Modules (single-file at first, split later):
- **link**: RedSocket client, reconnect with backoff, JSON-lines in/out, `hello` on connect.
- **registry**: logical_id → entity handle + last known state; emits `report.actors`.
- **actors**: ensure/remove through AMM spawn (F-004); appearance; teleport to node (F-008); pose; weapon; dead state.
- **rig**: camera rig, one spawned camera entity per preset (F-007); `cut(cam, blend)` = deactivate current, activate target; V hidden and parked (F-009).
- **beats**: timeline player on Cron; per-op `pcall`; reports failures without aborting the beat.
- **scout**: hotkeys for authoring (below).
- **world**: weather/time (AMM or game systems, verify in S-02).

Rules: `onUpdate` only calls `Cron.Update`; every engine call that isn't `verified` in facts is wrapped in `pcall` and logged with op id.

## Reconciler (Python)
Every `report.actors` and on every StageSpec change: diff desired vs actual → `actor.ensure`/`actor.remove` commands,
rate-limited (≤ 4 spawns in flight). Desync (missing actor for > 3 s, or no heartbeat for > 5 s) → `stage.desynced` event →
show clock pauses → OBS cuts to the failover feed until the stage is green again.

## Scout tool (authoring in-game, the content multiplier)
1. Teleport to a location; fly AMM's free camera to frame a shot.
2. Hotkeys: **Mark node** (V's position + yaw → node), **Mark camera** (active camera pos/rot/fov → camera preset), **Mark park**.
3. Each mark is sent as `scout.mark` to the orchestrator, which appends it to `content/scenes/<scene>.draft.json`.
4. Tag nodes in a text editor, run `arcade scene check` (lints: every slot has a node, every camera sees its subject's node, park point not in any frustum).

Target: author a soundstage in under 1 hour. Five stages for Season 0 = one weekend.
