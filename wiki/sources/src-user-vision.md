---
type: source
title: User vision docs (spec v1 + core philosophy) — what we kept, changed, dropped
status: current
updated: 2026-10-11
raw: [raw/user/system-specification.v1.md, raw/user/core-philosophy.v1.md]
---

# Source: the user's vision (2026-10-11)

Two docs: the *System Specification* (architecture, subsystems, schemas, guardrails) and *The Core Philosophy* (why: the arcade cabinet, four joysticks, shared stakes).

## Kept as pillars
Arcade-operator paradigm · four squads with turn-gated votes · discrete node graph + jump cuts · no generative LLM in the
real-time loop · transparent dice and permanent death · MVP credit · conflicting squad directives · downtime lobby · lifepath enemies seeding encounters · memorial vault.

## Changed (with reasons)

| Spec item | Now | Why | Where |
|---|---|---|---|
| `action_event.json` polled each frame | RedSocket TCP JSON lines | Already verified (F-001), has a back-channel, no file races | ADR-002 |
| Imperative per-action payload | Declarative StageSpec + beat timelines | Crash/reload recovery, content as data, animation-risk fallback | ADR-003 |
| Jev classifies the whole chat buffer at close | Per-message L0 → Jev, live tally | Transparency, attribution, spam resistance, no critical-path call | ADR-004 |
| Tie → Jev probability, then coin | Tie → visible provable roll | Viewers can audit a roll, not a model probability | ADR-004/006 |
| Fixed 10–15 s windows, 5 sequential phases | Viewer-time grace + early lock-in + pipelining | Broadcast delay; ~120 s → ~60 s rounds | ADR-010 |
| Cyberpunk RED rules as-is | RED-shaped homebrew, original names, simulator-tuned | R. Talsorian policy (R-08); tuning is required if you never fudge | ADR-005 |
| Seat 4 "Fixer" | Seat 4 "Face" | Streamer is the Fixer; two Fixers confuse chat | ADR-005 |
| `valid_actions` listed per node | Node affordance tags → generated actions | Authoring cost; consistency | design/ruleset |
| Death save `1d10 ≤ Body` | `d10 ≤ MEAT + 1 − n`, natural 10 fails, Stabilize by Tech | Escalation and team rescue are the drama | design/ruleset |
| Low velocity → auto "take cover" | Open seat + temperament defaults + attract mode | "Take cover" loops are dead air | design/squads-and-voting |
| Pre-rendered generic memorials | Per-character memorial rendered at creation + live epitaph | A generic clip can't show *this* character | design/permadeath |
| Pawn mesh-collapse heartbeat → `AMM.Teleport()` | Reconciler restages from StageSpec | One mechanism for every desync | components/stage |
| IGCS freecam for programmatic cuts | Spawned camera entities | IGCS isn't scriptable externally; AMM's camera entity is (F-007) | S-01 |
| "Complete HUD Remover" | Native HUD toggles + camera entities (HUD likely absent) | Verify in S-01 before adding mods | S-01 |

## Dropped / deferred
YouTube ingest (Q-01) · Sora/Runway generic stingers (replaced by in-engine captures + Hailuo i2v from portraits) ·
"Sub-150 ms" as a requirement (irrelevant inside a 12 s window, ADR-004).

## Added (not in the docs)
Provable dice · event-sourced ledger · FakeStage + tactical failover feed · scout authoring tool · balance simulator ·
latency-compensated windows · operator console with no outcome-changing controls · telegraphed enemy intent · Assist experiment.

## Contradictions found in the source
- Seat 4 = "Fixer" vs streamer = "the Fixer" → resolved by ADR-005.
- Philosophy doc: 4-phase tick; spec: 5 phases → superseded by ADR-010.
- Spec §3 shows IPC as "`action_event.json` / WebSocket"; CET has no native WebSocket → ADR-002.
