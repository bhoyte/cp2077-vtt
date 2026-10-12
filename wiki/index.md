---
type: hub
title: Index — every page, one line each
status: active
updated: 2026-10-11
---

# Index

Start at [now](now.md). Schema and operations: [AGENTS.md](../AGENTS.md). Timeline: [log](log.md).

## Hubs
- [overview](overview.md) — the project on one page: five reframes, architecture, what exists, what's unknown
- [glossary](glossary.md) — project vocabulary

## Registers
- [facts](facts.md) — engine/mod/vendor/host claims with evidence status and stack scope (F-001…)
- [risks](risks.md) — ranked risks with owners (R-01…)
- [questions](questions.md) — open questions with working defaults (Q-01…)

## Plan
- [roadmap](plan/roadmap.md) — two tracks, four gates (First Light, Ghost Cabinet, Vertical Slice, Launch), estimates
- [phase-0-reboot](plan/phase-0-reboot.md) — exact reinstall + mod restore + smoke test + freeze steps

## Decisions
- [ADR-001](decisions/ADR-001-canonical-repo.md) — this repo is canonical; port from night-city-live
- [ADR-002](decisions/ADR-002-transport.md) — RedSocket TCP JSON lines replaces file polling
- [ADR-003](decisions/ADR-003-declarative-stage.md) — declarative StageSpec + beat timelines (tableau model)
- [ADR-004](decisions/ADR-004-intent-pipeline.md) — per-message L0 → Jev intent, live tally
- [ADR-005](decisions/ADR-005-ruleset.md) — RED-shaped homebrew ruleset; seat 4 is "Face"
- [ADR-006](decisions/ADR-006-provable-dice.md) — commit/reveal HMAC dice
- [ADR-007](decisions/ADR-007-event-sourced-ledger.md) — event-sourced SQLite ledger
- [ADR-008](decisions/ADR-008-stack.md) — Python + TS + Lua; schemas as truth; FakeStage first-class
- [ADR-009](decisions/ADR-009-llm-boundary.md) — no generative AI in the authoritative loop
- [ADR-010](decisions/ADR-010-show-clock.md) — latency grace, early lock-in, pipelined slots
- [ADR-011](decisions/ADR-011-install-and-pin.md) — superseded: had said install on D:
- [ADR-012](decisions/ADR-012-install-path.md) — keep the game on the C: SSD; pin 2.31; freeze backups on D:

## Spikes
- [S-01](spikes/S-01-camera-rig.md) — partial: roof cameras switch and hold; HUD still draws; far park killed V
- [S-02](spikes/S-02-puppetry.md) — puppetry; first roof slice posed and froze three actors, full soak not run
- [S-03](spikes/S-03-staged-violence.md) — gunfire FX, hit reactions, death on command
- [S-04](spikes/S-04-resilience.md) — reconnect, restage, crash failover, soak, unfocused rendering
- [S-05](spikes/S-05-capture-and-perf.md) — OBS capture and performance budget on this PC
- [S-06](spikes/S-06-broadcast-delay.md) — measure Twitch delay, set vote grace L
- [S-07](spikes/S-07-jev-intent.md) — Jev accuracy, latency, cost on a labelled chat corpus

## Design
- [show-clock](design/show-clock.md) — slot timeline, round budget, camera grammar
- [squads-and-voting](design/squads-and-voting.md) — seats, membership, voting, low-population behaviour, engagement
- [ruleset](design/ruleset.md) — v0 rules: stats, checks, combat, armor, death saves, abilities, enemies, balance targets
- [permadeath](design/permadeath.md) — flatline sequence, memorials rendered at birth, replacement
- [campaign](design/campaign.md) — gig anatomy, downtime lobby, persistence, Season 0 stages

## Components
- [contracts](components/contracts.md) — scene manifest v2, StageSpec, beats, wire protocol stage.v1, events, overlay state
- [orchestrator](components/orchestrator.md) — module map, invariants, test strategy
- [stage](components/stage.md) — ArcadeStage CET mod, reconciler, scout authoring tool
- [intent](components/intent.md) — ingest, L0 parser, Jev request shape, vote book
- [broadcast](components/broadcast.md) — overlay layers, OBS scenes, operator console
- [ledger](components/ledger.md) — event store, projections, session reports

## Sources
- [src-user-vision](sources/src-user-vision.md) — the user's spec + philosophy: kept / changed / dropped / added
- [src-night-city-live](sources/src-night-city-live.md) — prior project: evidence and reusable assets
- [src-karpathy-wiki](sources/src-karpathy-wiki.md) — the LLM Wiki pattern and our extensions
- [src-vendor-and-host](sources/src-vendor-and-host.md) — Jev docs, patch compatibility, host audit, AMM camera source
