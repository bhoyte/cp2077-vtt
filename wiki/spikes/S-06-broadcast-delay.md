---
type: spike
id: S-06
title: Measure Twitch broadcast delay and set the vote grace L
status: planned
gate: G3
updated: 2026-10-11
depends_on: [F-016]
---

# S-06 — Broadcast delay

**Procedure.** Test channel, low-latency mode on. The overlay shows a large server clock and a countdown. Two or three
helpers on different devices type `now` the instant the countdown shows 0. The orchestrator logs arrival times.
`L = arrival − server_zero`, which includes typing reaction time (deliberately: that's what a real vote experiences).
Repeat 20 times.

**Pass/output.** p50 and p90 of L; default L = p90, rounded up to 0.5 s; record in ADR-010.

## Result
_(not run)_
