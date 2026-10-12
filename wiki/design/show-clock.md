---
type: design
title: Show clock — round structure and timing budget
status: draft
updated: 2026-10-12
depends_on: [ADR-010, F-016]
---

# Show clock

## One party slot (pipelined)

```
 t=0        t=12   t=12+L        t=14.3            t=19
 |--WINDOW--|--L---|             |                 |
 [options + live tally]          |                 |
                    close→resolve(≤0.3s)           |
                    |--DICE 2.0s--|--BEAT 3–6s------|
                                  [next party seat's WINDOW opens here if it acts next]
```
- `L` = broadcast-delay grace (default 3 s). The on-screen timer shows 12 s; the server closes at 12 + L.
- Early lock-in can end the window at ~5–8 s.
- Enemy slot: dice 1.5 s + beat 2–4 s, no window. Consecutive enemies are batched into one "enemy volley" beat (one wide shot plus quick reaction cuts) when they share a target.

## Budget per round (4 seats, 4 enemies)

| Mode | Party slots | Enemy slots | Round |
|---|---|---|---|
| Spec (sequential, 15 s windows) | 4 × ~25 s | 4 × ~5 s | ~120 s |
| This design, no early lock | 4 × ~19 s | 2 volleys × ~5 s | ~85 s |
| This design, typical (early lock + pipelining) | 4 × ~12 s | 2 × ~5 s | **~60 s** |

An encounter of 4–6 rounds runs 4–8 minutes. A gig (approach check, 1–2 encounters, extraction, payout) is ~35–50 minutes,
so a 2-hour show is 2 gigs plus a downtime lobby.

## Camera grammar per slot (default beat skeleton)

1. Window: **ready shot** of the active character (medium, slow push-in via camera blend), overlay shows options.
2. Dice: hold the ready shot. Dice overlay sits over it.
3. Beat: action shot (over-the-shoulder) → impact/reaction shot (target) → **wide** to re-establish geography.
4. Enemy volley: wide → victim close-up.

## Non-combat phases

| Phase | Window | Notes |
|---|---|---|
| Approach / skill challenge | 20 s, one per squad in parallel | All four squads vote at once on their own seat's approach |
| Negotiation (Face-led) | 15 s | Other squads may `!assist` |
| Downtime lobby | 45–60 s polls | Spending, upgrades, rent |
| Lifepath (replacement) | 3 × 20 s | Whole crew votes |

## Slice assumptions (2026-10-12)

`arcade/show/` follows the combat-slot diagram and ADR-010. Approach, negotiation, downtime, and lifepath windows are not scheduled yet. These numbers are not pinned in the design, so the code pins them on `ClockConfig` (overridable):

- Quorum **N is 3**. ADR-010 uses N for early lock and the +3 s extension and does not define it. Three means two accounts cannot lock a window. This is separate from squad `N_min` (default 2), which only decides an open seat.
- **Minimum 6 s** clamps the scheduled viewer window (`window_s` below 6 is rejected). Early lock is separate and can close sooner, once the leader has held ≥ 60 % of ≥ N votes for 3 s (the design's ~5–8 s band). A further vote for the same leader does not restart that 3 s hold.
- A ballot counts when `window_open ≤ ts < server_close`. The on-screen timer is zero during grace; the server still accepts until `viewer_close + L`. The +3 s extension check runs when simulated time moves *past* `open + 6 s`, so a ballot timestamped on that instant is included. An empty tally closes on the timer with no winner; temperament is not applied in this slice.
- Default durations: resolve 0.3 s, party dice 2.0 s, party beat **4 s** (inside 3–6), enemy dice 1.5 s, enemy beat **3 s** (inside 2–4).
- Consecutive enemy slots with the same non-empty target collapse into one volley: one dice interval and one beat. Differing or missing targets stay separate.
- The next party window opens at the instant the previous beat starts, and does not overlap the previous window. Enemy slots never open a window. A tie leaves `winner` unset; the clock does not roll the tie-break die.
