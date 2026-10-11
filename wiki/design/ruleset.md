---
type: design
title: Ruleset v0 — RED-shaped homebrew (all numbers provisional, simulator-tuned)
status: draft
updated: 2026-10-11
depends_on: [ADR-005, ADR-006]
---

# Ruleset v0

Original names and numbers (ADR-005). Every number is a knob in `rules/config.toml`, set by the balance simulator,
frozen per season.

## Stats (7, range 2–8 at creation, cap 10)
IRON (guns) · BLADE (melee) · GHOST (stealth, evasion, initiative) · JACK (netrunning) · WRENCH (tech, medicine, devices) · TALK (social) · MEAT (body, HP, death saves)

## Check
`d10 + STAT + Specialty + modifiers ≥ DV`
- **Specialty**: +2 on the seat's signature actions at creation; can grow to +4 through downtime.
- **Spike**: a natural 10 rolls another d10 and adds it (once).
- **Glitch**: a natural 1 rolls another d10 and subtracts it.
- DV ladder: Easy 8 · Standard 12 · Hard 15 · Severe 18 · Mythic 22.
- **Wounded** (HP ≤ half): −2 to all checks.

## Initiative
`d10 + GHOST` (Solo +2). Ties: higher GHOST, then a dice draw. Rolled once per encounter, shown as the initiative rail on the overlay.

## Ranged combat (node graph)
- Base DV by range band between nodes: close 12 · mid 15 · far 18.
- Target cover: half +2, full +4. Blackout (Netrunner): enemy ranged −2.
- **Aimed head shot**: −6 to hit; damage after armor is doubled.
- **Suppress**: no damage; target must pass GHOST DV 15 or lose its next move and be **Pinned** (−2 to attacks).
- Melee: opposed `d10 + BLADE` vs `d10 + max(BLADE, GHOST)`.

## Damage and armor
- Weapons: light pistol 2d6 · heavy pistol 3d6 · rifle 4d6 · shotgun 5d6 (close only) · blade 3d6 · fists 1d6+MEAT/2.
- **Critical**: two or more 6s on damage dice → +5 damage and roll on our injury table (d6, original effects, e.g. *Glass Eye*: −2 IRON).
- **Armor (SP)** per location (body, head): damage > SP → HP loses (damage − SP) and that SP drops by 1. Damage ≤ SP → no HP loss, no chip. The chip is shown on the overlay as a cracking armor bar.

## HP and death
- `HP = 15 + 5 × MEAT` (MEAT 5 → 40).
- At 0 HP → **FLATLINING**: no actions. At the start of each of the character's turns, a death save:
  success if `d10 ≤ MEAT + 1 − n` (n = death saves already made this encounter); a natural 10 always fails.
  Taking damage while flatlining forces an immediate extra save. One failure = **permanent death**.
- **Stabilize** (Tech, WRENCH vs DV 13, +2 with a medkit): ends death saves, sets HP to 1.
- Example, MEAT 5, nobody helps: survive 3 turns ≈ 0.6 × 0.5 × 0.4 = 12 %. The Tech squad's speed decides it.

## Seat abilities (once per encounter unless noted)
| Seat | Ability | Effect |
|---|---|---|
| Solo | Overclock | One extra attack this turn at −2 |
| Netrunner | Blackout · Hijack · Short · Ping | From scene `net` affordances: enemy ranged −2 for 2 rounds; take a turret; 2d6 ignoring SP vs a chromed target; reveal next enemy actions |
| Tech | Patch (each ally once) · Deploy cover · Stabilize (unlimited) | Heal 2d6; node cover half → full; see above |
| Face | Taunt · Call a Favor (once per gig) | TALK vs enemy resolve: enemy targets the Face or loses its action; gig-specific NPC intervention for eddies/rep |

## Enemies
| Tier | Atk bonus | HP | SP | Weapon | Notes |
|---|---|---|---|---|---|
| Mook | +8 | 15 | 4 | 2d6 | Flees at ≤ 5 HP if leader down |
| Soldier | +11 | 25 | 7 | 3d6 | Uses cover |
| Elite | +13 | 35 | 11 | 4d6 | One trick per encounter |
| Boss | +14 | 60 | 13 | 4d6 | Two actions per round; one signature move |

Enemy AI = utility scoring over the same action set (prefer targets that are wounded, in the open, or taunting), with
the provable dice stream as tie-breaker (ADR-006). Deterministic, auditable, and telegraphable by Ping.

## Action generation (replaces per-node `valid_actions` lists)
`options = seat_actions ∩ node_affordances(node.tags) ∩ legal(state)` → ranked → top 4 (always includes one defensive option).
Scene authors tag nodes (`cover:half`, `console:turret`, `door:weldable`, `vantage`), not actions. New actions automatically become available everywhere they make sense.

## Balance targets (simulator, v0)
- Encounter length 4–6 rounds.
- P(at least one permanent death per gig) 25–35 %. P(party wipe per gig) < 3 %.
- Each seat decides ≥ 20 % of encounter outcomes (no dead seats).
