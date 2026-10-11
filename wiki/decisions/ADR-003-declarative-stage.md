---
type: decision
id: ADR-003
title: Declarative stage + beat timelines (the tableau model)
status: accepted
updated: 2026-10-11
revisit_if: S-02/S-03 show live AI animation is reliable enough to drive directly
depends_on: [F-004, F-007, F-008, F-011]
---

# ADR-003 — The stage is declarative; action is told in beats

**Context.** The spec sends imperative one-shot payloads ("snap actor, trigger firing anim, cut camera"). Imperative
commands drift: a crash, reload, or failed spawn leaves the game in an unknown state (F-011). Also, CP2077 NPC
animation control is the project's biggest unknown (R-01).

**Decision.** Two layers:

1. **Baseline (declarative).** The orchestrator owns a `StageSpec`: scene id, weather/time, V's park point, the set
   of cameras, and each actor's {record, appearance, node, pose, weapon, alive/dead}. CET reports what actually exists.
   A reconciler diffs and sends only the corrections. Idempotent: sending the same spec twice does nothing.
2. **Beats (imperative, ephemeral).** An action outcome becomes a timeline of ops at millisecond offsets
   (cut, pose, FX, kill, look-at). CET plays it locally and reports `beat.done`. When the beat ends, the baseline is
   updated to the beat's end state (e.g. the target is now `dead` at its node), so a restage reproduces it.

**Why this optimizes the project.**
- Crash recovery, save/load, and "restage" are the same code path.
- Beats are **data** (authored templates with variants per outcome: miss / hit / crit / kill), so content scales
  without code, and an LLM can help author them offline.
- Jump cuts (spec principle 4) hide every teleport, so nothing needs pathfinding or locomotion.
- The animation risk degrades gracefully: if live animation fails, beats fall back to held poses + FX + cuts.

**Rejected.** Per-frame polling of commands; any use of game combat AI to produce outcomes; navmesh movement.
