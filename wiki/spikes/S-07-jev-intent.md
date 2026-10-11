---
type: spike
id: S-07
title: Jev accuracy, latency, and cost on our chat corpus
status: planned
gate: G2
updated: 2026-10-11
depends_on: [F-015]
---

# S-07 — Jev intent

**Corpus.** 500 messages: real chat from comparable interactive streams + playtest chat, each labelled with the option
it votes for (or `none`) given the options shown at the time.

**Procedure.** Run L0 alone, then L0 + Jev at θ ∈ {0.4, 0.5, 0.6, 0.7, 0.8}. Measure from this PC: Jev p50/p95 latency, cost per window, accuracy, coverage.

**Pass.** Combined accuracy ≥ 85 % at ≥ 70 % coverage of free-text votes; p95 < 1 s; cost < US$0.05 per show hour.
Also check L0-only accuracy (it must hold the show alone, R-13).

## Result
_(not run)_
