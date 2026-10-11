# Log

Append-only. Format: `## [YYYY-MM-DD] op | title`. Newest at the bottom. `rg "^## \[" wiki/log.md` lists entries.

## [2026-10-11] ingest | User vision docs, prior project, vendor docs, host audit
- raw: moved the user's two docs into `raw/user/` (v1, immutable); snapshotted 11 night-city-live docs, AMM `camera.lua`, Karpathy gist, Jev docs, compat matrix; wrote the host audit.
- Created sources: src-user-vision, src-night-city-live, src-karpathy-wiki, src-vendor-and-host.
- Registers: facts F-001…F-018, risks R-01…R-14, questions Q-01…Q-09.
- Contradictions recorded: F-006 vs F-007 (exEntitySpawner availability); seat "Fixer" vs streamer "Fixer"; 4-phase vs 5-phase clock.

## [2026-10-11] decide | Initial architecture and plan
- ADR-001…ADR-011 accepted.
- Design pages: show-clock, squads-and-voting, ruleset v0, permadeath, campaign. Components: contracts, orchestrator, stage, intent, broadcast, ledger.
- Plan: roadmap (two tracks, gates G1–G4), phase-0-reboot. Spikes S-01…S-07 planned.

## [2026-10-11] lint | First lint pass
- `python tools/wiki.py lint` clean; status dashboard verified.

## [2026-10-11] decide | User answers Q-01, Q-02, Q-03
- Twitch only; no paid effects on rules or dice (cosmetic only in Season 0); Steam unless GOG is proven necessary. Added F-019 (launching the exe directly avoids Steam updates, hypothesis).

## [2026-10-11] build | B1 rules core, provable dice, balance simulator
- Code: `arcade/dice`, `arcade/rules`, `arcade/sim`, `content/rules/season0.toml`; 21 tests (unit, replay equality, hypothesis termination property).
- Four tuning passes recorded in [ruleset](design/ruleset.md#tuning-history-v0-pass-2026-10-11). New mechanics: Heat, Hold; Taunt and Short circuit reworked.
- Result (4,000 gigs): 5.58 rounds/encounter, 27.6 % death/gig, 0.2 % wipe, 1.0 % stalemate. Seat leverage uneven → Q-10.
