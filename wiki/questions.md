---
type: register
title: Open questions
status: active
updated: 2026-10-11
---

# Open questions

Each question has a `default:` we build on until it's answered. Answering one = edit `answer:`, then run **decide** if it changes an ADR.

### Q-01 — Twitch only, or YouTube too?
blocks: [components/intent]
default: Twitch only for Season 0; ingest is an adapter interface so YouTube can be added later.
answer: Twitch only (user, 2026-10-11).

### Q-02 — Any monetization tied to gameplay (bits, channel points, subs affecting rules)?
blocks: [ADR-005, R-08]
default: No paid effect on rules or dice in Season 0. Channel points only for cosmetic perks (squad badge, memorial candle).
answer: No paid effects on rules or dice; cosmetic perks only in Season 0 (user, 2026-10-11).

### Q-03 — Is CP2077 also owned on GOG?
blocks: [R-04, plan/phase-0-reboot]
default: Steam only. Pin with "update on launch" + mod-layer backups.
answer: Steam only; user can buy on GOG if absolutely necessary (2026-10-11). Steam plan: update-on-launch + mod-layer zip + a full game-folder backup on D: for rollback; test whether launching the exe directly avoids forced updates (F-019).

### Q-04 — Is Phantom Liberty owned (Dogtown sets, extra assets)?
blocks: [design/campaign]
default: Base-game locations only.
answer:

### Q-05 — Is the crew's handler voiced live by the streamer, or partly pre-recorded / TTS?
blocks: [components/broadcast]
default: Live voice + a soundboard of pre-recorded stingers. D:\cppc already has an ElevenLabs workflow if TTS is wanted later.
answer:

### Q-06 — Target cadence and show length?
blocks: [plan/roadmap, design/campaign]
default: Weekly, ~2 h (≈2 gigs). Drives how many soundstages Season 0 needs (5).
answer:

### Q-07 — Budget for a RAM upgrade (16 → 32 GB), Jev credits, video generation?
blocks: [R-09, design/permadeath]
default: RAM upgrade recommended (~US$50–80). Jev cost is negligible (F-015). Memorial videos via the existing Hailuo workflow.
answer:

### Q-08 — Does AMM's Camera class respond when instantiated from another CET mod, or must we call through AMM's module table?
blocks: [S-01]
default: Try our own spawn of `simple_free_camera.ent` first; fall back to AMM's module.
answer:

### Q-09 — Can CP2077 keep rendering at full rate while unfocused (operator working on a second monitor)?
blocks: [S-04, S-05]
default: Assume yes; verify. If not, a dedicated operator machine or a hardware Stream Deck is needed.
answer:

### Q-10 — How do Netrunner and Face squads get ≥ 20 % of decision leverage?
blocks: [design/ruleset, design/squads-and-voting]
default: Model Ping (telegraph the next enemy action, so other squads vote on better information), Hijack (turret from a `console` affordance), and Call a Favor in the sim, then re-run the ablations. Accept a Solo/Tech-heavy split for Season 0 if those don't close the gap; the overlay can still give every squad a moment per encounter.
answer:
