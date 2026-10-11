---
type: spike
id: S-02
title: Puppetry — 6 actors at nodes, poses, freeze, expressions, weapons, no AI interference
status: planned
gate: G1
updated: 2026-10-11
depends_on: [F-004, F-005, F-008, F-012, F-013]
---

# S-02 — Puppetry

**Hypothesis.** We can hold six spawned actors (four party, two enemies, at least one gang record via F-005) at authored
nodes in authored poses for 10+ minutes, and change pose on command, without game AI moving them.

**Pre-work (no game).** Source-read the AMM functions behind F-013 in `D:\night-city-live\AppearanceMenuMod\Modules\`
(`anims.lua`, `tools.lua`, `util.lua`) and record the exact call chains as facts. Query the catalog SQLite for
candidate workspots: aim, crouch-aim, typing, hands-up, kneel-injured, lying-dead, talk-gesture, lean, sit-bar.

**Procedure.**
1. Spawn 6 actors (F-004 path, `try_direct_record` for the gang record). Measure command → visible latency.
2. Teleport each to a node with yaw (F-008). Repeat 20×; note snaps, falls, or floating.
3. Apply a workspot pose per actor; then freeze (AMM FreezeNPC) and unfreeze.
4. Expression + look-at on two actors. Equip a weapon on two actors; check it's visible in hand during a pose.
5. Neutralize AI: attitude group friendly/neutral, god mode; confirm no wandering, fleeing, combat, or reactions to each other or to V; confirm passers-by and NCPD ignore the set.
6. Leave it running for 10 minutes and watch for drift, T-poses, despawns.

**Pass.** Six actors stable for 10 min; ≥ 12 usable poses catalogued with tags; spawn latency p95 < 3 s; weapon visible in at least aim poses.

**Fallback.** Fewer pose types plus heavier camera/FX work ("diorama mode", R-01).

## Result
_(not run)_
