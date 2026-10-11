---
type: spike
id: S-04
title: Resilience — reconnect in any order, restage, crash failover, 60-minute soak, unfocused rendering
status: planned
gate: G3
updated: 2026-10-11
depends_on: [F-002, F-010, F-011]
---

# S-04 — Resilience

**Procedure.**
1. Start the game first, then the orchestrator 60 s later: does the CET backoff loop connect? (Tests whether a failed RedSocket can `Connect()` again; otherwise destroy/recreate the socket.)
2. Kill the orchestrator mid-scene, restart: ledger replay → reconciler restages to identical StageSpec.
3. Kill the game mid-beat: OBS auto-cuts to TACTICAL within 5 s; relaunch → load save → stage reconnects → restage → resume.
4. Soak: 60 min, a beat every 15 s, 6 actors. Track game RAM, FPS, registry count (entity leaks), CET errors.
5. Focus: game unfocused while the operator types in another app on monitor 2 (Q-09). Rendering rate and audio?

**Pass.** All five behave; zero manual steps in 2 beyond relaunching the game; no leak over 60 min.

## Result
_(not run)_
