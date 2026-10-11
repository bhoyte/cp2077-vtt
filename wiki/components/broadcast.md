---
type: component
title: Broadcast — overlay, OBS, failover feed, operator console
status: draft
updated: 2026-10-11
depends_on: [ADR-006, ADR-008, ADR-010]
---

# Broadcast

## Overlay (one browser source, layered)
- **Turn HUD**: active seat, options 1–4 with live tally bars, viewer-time countdown, LOCKED IN stamp.
- **Initiative rail**: portraits in order, current slot highlighted, flatline/stabilized states.
- **Party strip**: per seat: HP bar, head/body armor bars that visibly crack on chip, wound state, ability charges.
- **Dice layer**: 3D dice displaying the predetermined value (cosmetic only, ADR-006) + math line `7 + IRON 6 + 2 = 15 vs DV 15 → HIT`.
- **Banners**: MVPs ("Led by @NeonRider, @ZeroCool + 42"), CRIT, FLATLINED, LOCKED IN, OPEN SEAT, INSERT COIN.
- **Comms box**: non-active squads' chat, squad-colored.
- **Fairness chip**: `commit: 3f9a…` always visible; "verify roll #n" deep link after the show.
- **Tactical feed** (failover / FakeStage): 2D node map with pawns, range lines, cover icons; same data, no game needed.

## OBS (obs-websocket v5)
Scenes: `GAME` (game capture + overlay) · `TACTICAL` (failover) · `BRB/SIGNAL LOST` (diegetic) · `MEMORIAL` · `LOBBY` · `ATTRACT`.
The orchestrator switches scenes from events, plays media stingers, and takes portrait screenshots (permadeath pipeline).

## Operator console (local web page on a second monitor)
- Status lights: stage link, heartbeat FPS, Jev, Twitch, OBS, ledger.
- Hot actions: Pause clock · Resume · Restage scene · BRB · Set broadcast delay L · Ban/timeout · End session (reveals seed).
- Cue cards for the handler voice: briefing text, a suggested line per beat (selected from pools, ADR-009).
- No action can change a roll, an outcome, or a vote (by construction: the console has no such endpoints).
