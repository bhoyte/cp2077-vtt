---
type: decision
id: ADR-004
title: Per-message intent resolution — deterministic first, Jev for free text, live tally
status: accepted
updated: 2026-10-11
supersedes: spec §4C "ingest aggregated chat buffer as State → one Choice"
revisit_if: S-07 shows Jev accuracy < 85% on our labelled chat corpus or p95 latency > 1 s
depends_on: [F-015]
---

# ADR-004 — Intent pipeline

**Context.** The spec classifies the whole chat buffer once, at window close. That is opaque (chat can't see the vote
moving), unattributable (who gets MVP credit?), easy to game (one long message can dominate the buffer), and it puts a
network call on the critical path. Latency of the classifier doesn't matter anyway: the vote window is 10–15 s.

**Decision.** Classify **each message as it arrives**, during the window:

| Layer | Handles | Cost |
|---|---|---|
| L0 deterministic | `1`–`9`, `!1`, option keywords/aliases, mapped emotes | 0 ms, free |
| L1 Jev `choice` | Free-text messages L0 can't parse; options = current valid actions + `none` (chatter) | async, ~US$0.00003 each |
| Gate | Accept L1 only if confidence ≥ threshold (start 0.6, tune in S-07) | — |

- One vote per account per window; the latest message wins (people change their minds when they see the tally).
- The live tally is broadcast to the overlay on every change, which makes the vote itself a show.
- MVP attribution = accounts whose final vote matched the winner, ordered by how early they committed.
- Ties are broken by a visible tie-break roll from the provable dice service (not by model probability, which viewers can't audit).
- Jev is also useful off the critical path: picking which pre-written handler line or beat variant fits a situation (selection, not generation — ADR-009).

**Consequences.** The show runs fully with L0 only (R-13). Free text becomes a bonus that rewards in-character chat.
