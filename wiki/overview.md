---
type: hub
title: Overview — Night City Arcade
status: active
updated: 2026-10-12
depends_on: [F-001, F-004, F-007]
---

# Night City Arcade — the project on one page

**What it is:** a live broadcast where Twitch chat *is* the crew. Viewers join one of four squads, each piloting one
edgerunner. A deterministic TTRPG engine resolves every action with provably-fair dice. Cyberpunk 2077 is the stage:
pawns, cameras and effects are puppeted to render each outcome as a cut-together TV-style shot sequence.
Death is permanent. The streamer is off-camera: the operator, and the diegetic voice of the crew's handler.

Source vision: [user spec](../raw/user/system-specification.v1.md), [core philosophy](../raw/user/core-philosophy.v1.md) — summarized and critiqued in [sources/src-user-vision](sources/src-user-vision.md).

**Operating model ([ADR-013](decisions/ADR-013-operated-table.md)).** An operator runs the table. The operator may be a person or an agent with tools. The first tool is the session: the game keeps the pieces, redials `127.0.0.1:2077`, and answers `status` with the measured player position. Rules and dice stay deterministic. Twitch, OBS, beat timelines, and the self-healing reconciler wait until that session holds.

## The five reframes (what changed from the original spec)

1. **CP2077 is a tableau renderer, not a simulation.** Every outcome is a short authored *beat*: a timeline of
   camera cuts, poses, FX, and kills played inside the game. No game AI or game combat ever decides anything.
   This turns the hardest risk (animation control) into a content problem with a graceful fallback ([ADR-003](decisions/ADR-003-declarative-stage.md)).
2. **The stage is declarative and self-healing.** The orchestrator holds the *desired* scene; the CET mod reports
   *actual* actors; a reconciler diffs and fixes. Game crashes, reloads, despawns → automatic restage ([ADR-003](decisions/ADR-003-declarative-stage.md)).
3. **Votes are per-message, live, and latency-compensated.** Deterministic parsing first, Jev only for free text,
   a visible live tally, windows that account for Twitch broadcast delay, early lock-in, pipelined turns
   ([ADR-004](decisions/ADR-004-intent-pipeline.md), [ADR-010](decisions/ADR-010-show-clock.md)).
4. **"Never fudge" becomes provable.** Seed commitment at stream start, every roll derived by HMAC, seed revealed at
   the end; anyone can verify every roll ([ADR-006](decisions/ADR-006-provable-dice.md)).
5. **The show runs without the game.** The full loop (chat → votes → rules → overlay) runs against a fake stage
   with a 2D tactical feed. It is the dev harness, the CI test, *and* the on-air failover if CP2077 crashes
   ([ADR-008](decisions/ADR-008-stack.md), [components/broadcast](components/broadcast.md)).

## Architecture

```
 Twitch EventSub ──▶ ingest ──▶ intent (L0 parser → Jev) ──▶ vote tally ──┐
                                                                          ▼
 operator console ◀──▶  ORCHESTRATOR (Python asyncio, event-sourced)  ◀── rules core (pure)
                          │        │            │                          dice (HMAC, committed seed)
                          │        │            └──▶ ledger (SQLite event log)
                          │        ▼
                          │   director: outcome → beat template → bound timeline
                          │        ▼
                          │   stage reconciler ──TCP JSON-lines (RedSocket)──▶ CET "Stage" mod ──▶ AMM / game
                          ▼                                                        │ reports: actors, acks, beat.done
                    overlay (browser source, WS)  +  OBS (obs-websocket v5)  ◀──────┘ (game capture)
```

Details: [components/orchestrator](components/orchestrator.md), [components/stage](components/stage.md),
[components/intent](components/intent.md), [components/broadcast](components/broadcast.md),
[components/ledger](components/ledger.md), [components/contracts](components/contracts.md).

## What already exists (inherited from `D:\night-city-live`)

- RedSocket TCP bridge, CET ↔ Python, verified on patch 2.31 (F-001).
- NPC spawn / appearance / despawn through AMM from our own CET mod (F-004).
- AMM entity catalog exported to SQLite: 4,363 entities, 30k appearances, 43,765 workspots (F-012).
- A homebrew ruleset bible written for a single protagonist ([sources/src-night-city-live](sources/src-night-city-live.md)).

## What is unknown (and gates everything)

Camera entities driven from our mod (S-01), pose/animation puppetry (S-02), staged violence (S-03),
operational resilience (S-04), and the performance budget on this PC (S-05). See [plan/roadmap](plan/roadmap.md).

## Design pillars (kept from the original vision)

Chat is the crew · Four seats, horizontal bonds · Transparent dice, permanent death · TV direction via jump cuts ·
The operator stays behind the curtain. Seat 4 is renamed **Face** because "Fixer" is the streamer's persona ([ADR-005](decisions/ADR-005-ruleset.md)).

Game design: [show-clock](design/show-clock.md) · [squads-and-voting](design/squads-and-voting.md) · [ruleset](design/ruleset.md) ·
[permadeath](design/permadeath.md) · [campaign](design/campaign.md). Terms: [glossary](glossary.md).
Registers: [facts](facts.md) · [risks](risks.md) · [questions](questions.md).
