---
type: decision
id: ADR-006
title: Provably fair dice via seed commitment and HMAC derivation
status: accepted
updated: 2026-10-11
revisit_if: never (it's cheap); extend only
depends_on: []
---

# ADR-006 — Provable dice

**Context.** "Never fudge the dice" (philosophy doc) is a promise viewers can't check. When a beloved character dies,
some of chat will accuse the operator.

**Decision.**
- At stream start: generate a 256-bit `seed`, publish `commit = SHA-256(seed)` on the overlay and in a chat message.
- Every random draw `i` = HMAC-SHA256(seed, `"{session}:{i}:{purpose}"`), mapped to a die by rejection sampling (no modulo bias).
- `purpose` labels each draw (`init:solo`, `attack:solo:d10`, `damage:solo:d6#2`, `enemy-ai:ganger2`). Enemy decisions use the same stream, so they're auditable too.
- At stream end: reveal `seed` and publish the roll log. A small public verifier script recomputes every roll.
- 3D dice on the overlay are cosmetic. They *display* the already-determined value and never generate one.

**Consequences.** The rules core never calls `random`. Replays are deterministic (ADR-007). Moments like "verify the death roll" become content.
