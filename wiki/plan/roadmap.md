---
type: plan
title: Roadmap — two tracks, four gates
status: active
updated: 2026-10-11
depends_on: [ADR-003, ADR-008]
---

# Roadmap

Two tracks run in parallel. **Track A** needs the game (risk retirement). **Track B** doesn't (the show itself, built
against the FakeStage). They merge at G3. Estimates are *focused working days*; agents can run Track B work in parallel with you.

```
Track A (game)    P0 reboot ─▶ spikes S-01 S-02 S-03 S-05 ─▶ G1 FIRST LIGHT ─▶ A2 stage integration ─┐
                                                                                                      ├─▶ G3 VERTICAL SLICE ─▶ P4 season 0 ─▶ G4 LAUNCH
Track B (no game) B1 rules+dice+sim ─▶ B2 clock+intent+chatsim ─▶ B3 overlay+fake stage+OBS ─▶ G2 GHOST CABINET ─┘
```

## Gates

| Gate | Definition of done | Status |
|---|---|---|
| **G1 First Light** | One Python command plays a 20 s sequence in CP2077: 4 pawns at nodes, wide → OTS → shot → enemy drops → wide, on the camera rig, captured in OBS at budget. S-01/S-02/S-03 passed or fallback chosen; S-05 run. | open |
| **G2 Ghost Cabinet** | Full show loop playable in a browser with no game: ChatSim crowd (or you + friends in a test channel) → squads → votes with live tally → rules → dice with commit/reveal → tactical feed → permadeath → replacement. Simulator hits balance targets. S-07 run. | open |
| **G3 Vertical Slice** | One soundstage, real game, private Twitch test channel, 45 min of play with ≥ 4 humans; zero operator interventions besides voice; S-04 + S-06 passed; session report ingested. | open |
| **G4 Launch** | 5 soundstages, lobby, memorial pipeline, lifepath, cross-episode persistence, stream-day runbook, 3 full rehearsals. | open |

## Phases

| Phase | Work | Est. days | Exit |
|---|---|---|---|
| P0 Reboot | [phase-0-reboot](phase-0-reboot.md): C: SSD install, redscript, smoke (`spawn complete`), freeze on D: | 1 | done 2026-10-11 |
| A1 Spikes | S-01, S-02, S-03, S-05 (S-04 partially) | 6–9 | G1 |
| A2 Stage integration | Port CypherAgent → ArcadeStage (`stage.v1`), camera rig, actors, beat player, reconciler, scout tool, first soundstage authored | 7–10 | G3 input |
| B1 Rules core | `rules/`, `dice/` (commit, HMAC, verifier), `sim/` with bot policies, property tests, balance pass | 5–7 | sim meets targets in [ruleset](../design/ruleset.md) |
| B2 Show & intent | Show clock (grace, lock-in, pipelining), L0 parser, Jev client, vote book, ChatSim, Twitch EventSub adapter, ledger | 4–6 | recorded-chat replays pass |
| B3 Broadcast | Overlay (HUD, dice, banners, comms, tactical feed), OBS client, operator console | 6–8 | G2 |
| P3 Slice | Merge tracks, one soundstage with 3 beat families (ranged, netrun, stabilize), private playtests | 4–6 | G3 |
| P4 Season 0 | 4 more soundstages, beat variants, gigs, lobby, memorial pipeline, lifepath, runbook, rehearsals | 10–15 | G4 |

**Total: ~45–60 focused days.** The critical path is A1 → A2 (game unknowns); B is pure software and can't block.

## Sequencing rules
1. Don't author content (beats, gigs, stages) before G1. Content built on unverified puppetry gets thrown away.
2. Don't build Twitch-specific UI before G2 is playable with ChatSim.
3. Every spike ends with a **spike-report** into the wiki, even if it failed. Failed spikes are the most valuable pages.
