---
type: register
title: Risk register
status: active
updated: 2026-10-13
---

# Risk register

Ranked by likelihood × impact. Each risk has an owner: the spike or phase that retires it.

### R-01 — NPC puppetry can't sell action (poses don't hold, weapons don't show, kills look wrong)
likelihood: medium
impact: high
mitigation: Tableau design (ADR-003) only needs *held* poses + cuts + FX. Fallback ladder: AI-command animation → workspot pose → frozen pose → stylized "diorama" (static pawns, heavy FX, comic-panel overlays).
owner: S-02, S-03

### R-02 — Camera entities can't be spawned/driven from our mod (see F-006 vs F-007 contradiction)
likelihood: low
impact: critical
mitigation: Call AMM's own Camera module via `GetMod("AppearanceMenuMod")`; fallback: player FPP camera on an invisible, collision-free V (teleport V = move camera).
owner: S-01

### R-03 — Scenery degrades or NPCs vanish when the camera is far from V (streaming radius)
likelihood: medium
impact: high
mitigation: Each scene manifest has a `player_park` point inside the set, out of all camera frusta (F-009).
owner: S-01

### R-04 — A game or mod update breaks the stack before a show
likelihood: medium
impact: high
mitigation: Steam "update only on launch", back up the verified mod layer + exe after each verification, preflight smoke test before every show, failover 2D feed. If owned on GOG, use the GOG offline installer for true pinning (Q-03).
owner: Phase 0, S-04

### R-05 — Too few viewers for four squads
likelihood: high
impact: high
mitigation: Adaptive squad merge (below N active voters, everyone votes for every seat), attract mode, bot-backfilled defaults that pick the *character's* personality action, not "take cover".
owner: design/squads-and-voting

### R-06 — Broadcast delay makes vote windows unfair or confusing
likelihood: high
impact: medium
mitigation: Latency-compensated windows + early lock-in (ADR-010), measured delay (S-06).
owner: S-06

### R-07 — Permadeath tuned wrong (party wipes → churn, or no deaths → no stakes)
likelihood: high
impact: high
mitigation: Balance simulator with bot chats; target band set before launch; tune only between seasons, never mid-show.
owner: Phase 2

### R-08 — IP: Cyberpunk RED rules/text (R. Talsorian) and monetization
likelihood: medium
impact: high
mitigation: RED-shaped homebrew with original names and tables, no rulebook text anywhere, no paid effects on rules in Season 0, Streamer Mode for music. CDPR fan-content guidelines permit monetized videos of the game. Contact R. Talsorian before monetizing (Q-02).
owner: ADR-005

### R-09 — PC can't run CP2077 + OBS + overlays + orchestrator together (16 GB RAM, 8 GB VRAM)
likelihood: medium
impact: high
mitigation: 1080p DLSS Quality, no path tracing, 60 fps cap, NVENC encode, minimal browser sources (one overlay page). Upgrade to 32 GB RAM as cheapest insurance.
owner: S-05

### R-10 — CP2077 crashes or desyncs live
likelihood: medium
impact: high
mitigation: Event-sourced state (ADR-007), auto-cut to diegetic "SIGNAL LOST" scene + 2D tactical feed, restage via reconciler on reconnect.
owner: S-04, components/stage

### R-11 — Operator overload (voicing the handler while running ops)
likelihood: medium
impact: medium
mitigation: Normal loop needs zero operator input. Operator console with cue cards, a few hot actions (pause, restage, BRB) on hotkeys or a Stream Deck.
owner: components/broadcast

### R-12 — Chat abuse: brigading, alt accounts, spam, offensive names in MVP banners
likelihood: medium
impact: medium
mitigation: One vote per account per window, squad lock per stream, minimum account age/follow time for squad join, MVP banner only shows names past Twitch AutoMod, operator ban hotkey.
owner: components/intent

### R-13 — Jev outage, pricing, or accuracy problems
likelihood: low
impact: low
mitigation: Jev is an enhancement. The deterministic L0 parser alone runs the show.
owner: S-07

### R-14 — Scope drift (history: two diverged repos, three visions)
likelihood: high
impact: high
mitigation: Hard gates in the roadmap, `now.md` discipline, a vertical slice before any content expansion.
owner: plan/roadmap

### R-15 — C: SSD fills up (51 GB free after the 91 GB install) and starves the pagefile or a Steam verify
likelihood: medium
impact: medium
mitigation: Keep the live game on C: (ADR-012). Put stack zips, full-folder backups, and OBS recordings on D:. Set Steam to update-on-launch. Don't keep a second copy of the game on C:.
owner: plan/phase-0-reboot

### R-16 — A mod reload forgets spawned people, and a crowded mark slides the formation
likelihood: high
impact: medium
mitigation: Keep reloading while this work is in progress. The appearance menu's spawn list and its saved copy were both empty after a reload on 2026-10-13, while the bodies can remain (F-031). `place` now writes each handle to `tagged.json`, and `clear` uses that file. Anyone spawned before the tag has none. A wedge also stepped 4.8 m forward because the previous file still occupied the nearer marks (raw/evidence/2026-10-13-place-wedge.md).
owner: spawning, ADR-013
