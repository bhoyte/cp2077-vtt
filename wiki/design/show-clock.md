---
type: design
title: Show clock — round structure and timing budget
status: draft
updated: 2026-10-11
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
