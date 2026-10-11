---
type: decision
id: ADR-010
title: Latency-compensated, pipelined show clock with early lock-in
status: accepted
updated: 2026-10-11
supersedes: spec §5 fixed 5-phase sequential clock
revisit_if: Playtests show viewers miss outcomes because the next window overlaps the cinematic
depends_on: [F-016]
---

# ADR-010 — Show clock

**Problems with the spec clock.**
1. Twitch viewers see the stream seconds late (F-016). A 12 s window on the server is ~8 s for a viewer, and their last
   votes land after close.
2. Strictly sequential phases (window → roll → cinematic → enemy) leave each squad idle ~75 % of the time and run
   ~25 s per action.
3. Fixed windows waste time when chat agreed in 4 s.

**Decision.**
- **Viewer-time windows.** The server keeps accepting votes for `L` seconds after the on-screen timer hits zero
  (`L` = measured broadcast delay, default 3 s with low-latency mode, set per stream). Votes are timestamped on arrival.
- **Early lock-in.** If the leader holds ≥ 60 % of ≥ N voters, stable for 3 s, the window closes early: "LOCKED IN".
- **Pipelining.** When the next initiative slot is a party seat, its command window opens as the current cinematic
  starts (the dice result is already on screen). Enemy slots never take a window.
- **Adaptive length.** Base 12 s; +3 s if fewer than N votes after 6 s; minimum 6 s.

Timing estimates and the full round diagram: [design/show-clock](../design/show-clock.md).
