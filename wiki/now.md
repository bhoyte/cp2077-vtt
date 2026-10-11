---
type: hub
title: Now — current focus and handoff
status: active
updated: 2026-10-11
---

# Now

**Focus:** Phase 0 (reinstall + restore the stack) on Track A, and B1 (rules core + provable dice + simulator) on Track B, in parallel.
**Active gates:** G1 First Light (Track A), G2 Ghost Cabinet (Track B). See [roadmap](plan/roadmap.md).
**Orientation:** [overview](overview.md) · [glossary](glossary.md) · how this wiki works: [AGENTS.md](../AGENTS.md), [src-karpathy-wiki](sources/src-karpathy-wiki.md).

## Next actions
1. **You:** Steam install to `D:\SteamLibrary` (C: is too small, ADR-011), then follow [phase-0-reboot](plan/phase-0-reboot.md) through the smoke test.
2. **You:** answer the open questions or accept their defaults ([questions](questions.md)): Q-01 platform, Q-02 monetization, Q-03 GOG, Q-06 cadence.
3. **Agent (no game needed):** scaffold `arcade/` (uv project), build `dice/` (commit, HMAC draws, verifier) and `rules/` from [ruleset](design/ruleset.md) with property tests.
4. **Agent:** `sim/` balance simulator; tune v0 numbers to the balance targets; record results in the ruleset page.
5. **Agent (pre-work for S-02):** source-read AMM `anims.lua` / `tools.lua` / `util.lua` and turn the F-013 claims into source-read facts; query `amm_universe.sqlite` for pose and FX candidates.
6. **Then, with the game installed:** S-01 camera rig (the highest-value unknown), then S-02, S-03, S-05.

## Blockers
- Game not installed; redscript missing (F-017).
- OBS not installed (needed for S-05, S-01 frame-stepping).

## Last handoff (2026-10-11)
Wiki created and seeded from the user's two docs, the night-city-live evidence, AMM camera source, Jev docs, and a host audit.
11 ADRs accepted, 7 spikes planned, ruleset v0 drafted. Nothing has been built yet in this repo.
