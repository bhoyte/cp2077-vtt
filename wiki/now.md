---
type: hub
title: Now — current focus and handoff
status: active
updated: 2026-10-11
---

# Now

**Focus:** Phase 0 (reinstall + restore the stack) on Track A; on Track B, B1 is done (rules core + provable dice + simulator), B2 is next.
**Active gates:** G1 First Light (Track A), G2 Ghost Cabinet (Track B). See [roadmap](plan/roadmap.md).
**Orientation:** [overview](overview.md) · [glossary](glossary.md) · how this wiki works: [AGENTS.md](../AGENTS.md), [src-karpathy-wiki](sources/src-karpathy-wiki.md).

## Next actions
1. **You:** Steam install to `D:\SteamLibrary` (C: is too small, ADR-011), then follow [phase-0-reboot](plan/phase-0-reboot.md) through the smoke test.
2. **You (optional):** remaining open questions in [questions](questions.md), especially Q-06 cadence and Q-10 seat leverage.
3. **Agent (B2, no game needed):** show clock (grace window, early lock-in, pipelining), L0 intent parser, vote book, ChatSim crowd, ledger; drive `arcade.rules` from it.
4. **Agent:** model Ping / Hijack / Call a Favor in the sim and re-run the seat ablations (Q-10).
5. **Agent (pre-work for S-02):** source-read AMM `anims.lua` / `tools.lua` / `util.lua` and turn the F-013 claims into source-read facts; query `amm_universe.sqlite` for pose and FX candidates.
6. **Then, with the game installed:** S-01 camera rig (the highest-value unknown), then S-02, S-03, S-05.

## Blockers
- Game not installed; redscript missing (F-017).
- OBS not installed (needed for S-05, S-01 frame-stepping).

## Last handoff (2026-10-11)
B1 built: `arcade/dice` (HMAC-SHA256 draws, commit/reveal, verifier CLI), `arcade/rules` (event-sourced engine, enemy AI,
config + `content/rules/season0.toml`), `arcade/sim` (Monte Carlo gigs, crowd policy, seat ablations). 21 tests pass (`uv run pytest`).
Season 0 numbers hit all four lifecycle targets; seat leverage is uneven (see [ruleset](design/ruleset.md), Q-10).
Rule changes made by the sim: lower DVs, Heat from round 6, Taunt = enemy loses its next action, repeatable Short circuit.
