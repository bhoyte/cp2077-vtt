---
type: component
title: Orchestrator — module map and boundaries
status: draft
updated: 2026-10-11
depends_on: [ADR-007, ADR-008]
---

# Orchestrator

Python 3.11 asyncio process. Hexagonal: a pure core with adapters around it.

```
arcade/
  rules/        pure: state, apply(event), legal_actions, resolve(action, dice) → events, enemy_ai   (no I/O, no clock, no random)
  dice/         seed commit, HMAC draws, rejection sampling, roll log, verifier CLI
  show/         the clock: slots, windows (latency grace, early lock), pipelining, phase machine
  intent/       L0 parser, Jev client (async, timeout, circuit breaker), per-user vote book, tally
  ingest/       Twitch EventSub adapter; ChatSim adapter (bot crowds, replays of recorded chat)
  director/     action → beat template choice (variant by outcome) → binding (actors, cameras, nodes) → timeline
  stage/        StageSpec, reconciler, RedSocket server, FakeStage (2D), file-drop fallback
  broadcast/    overlay WebSocket server (snapshot + patches), OBS client (obs-websocket v5)
  ledger/       SQLite event store, projections, session reports → raw/sessions/
  operator/     local console (pause, resume, restage, BRB, ban, set L), Stream Deck HTTP hooks
  sim/          balance simulator (headless: rules + dice + bot policies, 10k encounters/minute)
content/        scenes/*.json, beats/*.json, gigs/*.toml, barks/*.toml, catalog/curated.json
```

## Invariants
- `rules` is the only module that changes game state, and only by emitting events.
- Every external effect (stage, overlay, OBS) is derived from events, so replaying the ledger re-derives them.
- Any adapter can die and restart without corrupting state; the show clock pauses on stage desync > 5 s.

## Test strategy
- Rules: hypothesis property tests (HP never < 0 except flatline semantics, SP never < 0, initiative is a permutation), golden encounter replays from fixed seeds.
- Show clock: simulated time, recorded chat fixtures, latency-grace edge cases.
- End-to-end in CI: ChatSim → orchestrator → FakeStage → overlay snapshot assertions.
