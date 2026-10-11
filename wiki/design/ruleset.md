---
type: design
title: Ruleset v0 — RED-shaped homebrew (simulator-tuned, Season 0 candidate)
status: draft
updated: 2026-10-11
depends_on: [ADR-005, ADR-006, ADR-007]
---

# Ruleset v0

Original names and numbers (ADR-005). Code: `arcade/rules/` (engine, events, enemy AI). Every number is a knob:
defaults in `arcade/rules/config.py`, Season 0 overrides in `content/rules/season0.toml`, set by the balance simulator
(`python -m arcade.sim --rules content/rules/season0.toml --ablate`), frozen per season. **The TOML is the source of
truth for numbers; this page explains them.** If they disagree, the TOML wins and this page is stale.

## Stats (7, range 2–8 at creation, cap 10)
IRON (guns) · BLADE (melee) · GHOST (stealth, evasion, initiative) · JACK (netrunning) · WRENCH (tech, medicine, devices) · TALK (social) · MEAT (body, HP, death saves)

A stat already folds in training (there are no separate skills), so DVs sit lower than in RED.

## Check
`d10 + STAT + Specialty (+2 on the seat's signature stat) + modifiers ≥ DV`
- **Spike**: a natural 10 rolls another d10 and adds it. **Glitch**: a natural 1 rolls another d10 and subtracts it.
- Non-combat DV ladder: Easy 8 · Standard 12 · Hard 15 · Severe 18.
- **Wounded** (HP ≤ half): −2 to all checks.
- Every roll is drawn from the provable dice stream with a purpose label (`r3:solo:attack:d10`), so the overlay can show it and anyone can verify it (ADR-006).

## Initiative
`d10 + GHOST` (Solo +2). Ties: higher GHOST, then a dice draw. Rolled once per encounter → initiative rail on the overlay.

## Turn loop
Each round, combatants act in initiative order with 1 action (Boss: 2). Start of turn: flatlining → death save instead of acting;
bleeding injuries tick; pinned → this turn's attacks −2. **Hold** is always legal (the vote-timeout default).

## Ranged combat (node graph)
- Base DV by range band between nodes: **close 8 · mid 11 · far 14**. The crew adds **+2 weapon skill**; enemies use their tier specialty.
- Target cover: half +2, full +4. **Take cover** moves you to your node's best cover (party start in the open).
- **Aimed head shot**: −6 to hit; damage after armor doubled.
- **Suppress**: target makes GHOST vs DV 15 or is **Pinned** (its next turn's attacks −2).
- **Heat**: from round 6, every node's cover drops one step at the start of each round (full → half → none). The scene is
  coming apart; this ends turtling and keeps encounters inside the show clock. Stalemate at round 12 is a failsafe, not a mechanic.
- Melee (not yet in code): opposed `d10 + BLADE` vs `d10 + max(BLADE, GHOST)`.

## Damage and armor
- Weapons: light pistol 2d6 · heavy pistol 3d6 · rifle 4d6 · shotgun 5d6 (close only).
- **Armor (SP)** per location (body, head): damage > SP → HP loses (damage − SP) and that SP drops by 1. Damage ≤ SP → nothing.
- **Critical**: two or more 6s on the damage dice → **+5 HP loss applied after armor** (it never gets soaked), and party
  members roll the injury table (d6: glass eye IRON −2 · cracked ribs all −1 · burned hand IRON −1/BLADE −2 · concussion JACK/TALK −2 · shrapnel leg GHOST −2 · gut shot bleed 2/turn until patched).

## HP and death
- `HP = 15 + 5 × MEAT` (MEAT 5 → 40). Enemies at 0 HP die; Mooks flee at ≤ 5 HP once no leader is standing.
- Party at 0 HP → **FLATLINING**: no actions. Start of each own turn: death save, success if `d10 ≤ MEAT + 1 − n`
  (n = saves already made this encounter); natural 10 always fails. Damage while flatlining forces an extra save. One failure = **permanent death**.
- **Stabilize** (Tech, WRENCH vs DV 13, +2 with a medkit, 2 medkits per gig): back to ALIVE at 1 HP.
- Encounter ends with someone standing → flatlining crew are carried out (stabilized). Nobody standing → they die.
- **Breather** between the encounters of one gig: each surviving crew member heals 2d6.

## Seat abilities
| Seat | Action | Effect |
|---|---|---|
| Solo | Overclock (1/encounter) | Two attacks at −2 on one target |
| Netrunner | Blackout (1/encounter) | JACK vs DV 13: enemy attacks −2 for 2 rounds |
| Netrunner | Short circuit (repeatable) | JACK vs DV 15: 2d6 ignoring armor |
| Tech | Patch (each ally once per encounter) | WRENCH vs DV 12: heal 2d6, stops bleeding |
| Tech | Deploy cover (1/encounter) | Ally to full cover |
| Tech | Stabilize | See above |
| Face | Taunt (repeatable, one pending per enemy) | TALK vs resolve (Mook 10 · Soldier 12 · Elite 14 · Boss 16): the enemy loses its next action |

Not yet in code (need scene affordances or gig layer): Netrunner Hijack (take a turret) and Ping (telegraph enemy intent), Face Call a Favor (once per gig).

## Enemies
| Tier | IRON + specialty | HP | SP | Weapon | Trick |
|---|---|---|---|---|---|
| Mook | 5 + 0 | 10 | 0 | light pistol | Flees |
| Soldier | 6 + 1 | 18 | 2 | heavy pistol | — |
| Elite | 8 + 2 | 35 | 6 | rifle | Lock-on: one attack at +4 |
| Boss | 7 + 2 | 45 | 5 | rifle | 2 actions/round; Rampage: one attack at −2 on every standing crew member |

Enemy AI (`arcade/rules/ai.py`) = utility scoring over the same legal actions: prefer wounded targets and targets in the open,
avoid finishing the flatlining (−100), lock-on/rampage when they pay. Ties within 2 points are broken by a provable d6, so
enemy choices are deterministic, auditable, and replayable (ADR-007).

## Action generation (planned, replaces per-node `valid_actions` lists)
`options = seat_actions ∩ node_affordances(node.tags) ∩ legal(state)` → ranked → top 4 (always one defensive option).
Scene authors tag nodes (`cover:half`, `console:turret`, `door:weldable`, `vantage`), not actions. Today `legal_actions` implements the `legal(state)` part.

## Balance targets and Season 0 results
Gig = opener (street: 3 Mooks + Soldier, or squad: 2 Soldiers + 2 Mooks) then closer (elite: Elite + 2 Soldiers, or boss: Boss + 2 Mooks),
random range bands (close 25 % / mid 55 % / far 20 %) and node cover. Crowd = noisy heuristic policy, 15 % uniformly random votes.

4,000 gigs, seed 1, 2026-10-11:

| Target | Band | Result |
|---|---|---|
| Rounds per encounter | 4–6 | 5.58 (p90 = 8) |
| P(≥ 1 permanent death per gig) | 25–35 % | 27.6 % |
| P(party wipe per gig) | < 3 % | 0.2 % |
| P(stalemate per encounter) | < 1 % | 1.0 % (at the edge) |

By gig shape, death rate is street+elite 15 % · squad+elite 17 % · street+boss 37 % · squad+boss 42 %. Boss gigs being
about 2.5× deadlier is a feature if the gig board shows it (risk vs payout is a crowd choice); see [campaign](campaign.md).

Crowd skill matters, which is what makes voting meaningful: P(death) is 22 % with a perfect crowd, 28 % at 15 % chaos,
35 % at 30 %, and 46 % at 50 % chaos (wipes stay < 3 % even then; rounds rise to 6.5).

**Seat balance (open).** Two ablations, each comparing extra party loss (deaths + 2 × wipe) per gig:
- *Seat power* (the seat only holds): Solo 55 % · Tech 21 % · Netrunner 12 % · Face 12 %.
- *Vote leverage* (the seat's squad votes at random): Solo 37 % · Tech 34 % · Netrunner 15 % · Face 14 %.

The target "every seat ≥ 20 %" is met for Solo and Tech only. Swapping weapons barely moves it; the missing lever is
choice depth for Netrunner and Face (Hijack, Ping, Call a Favor are not modeled yet). Tracked as Q-10.

## Tuning history (v0 pass, 2026-10-11)
1. RED-like DVs (12/15/18) with 2–8 stats: 12-round stalemates, 92 % death, 17 % wipe. Stats already include training, so DVs had to drop.
2. DVs 8/11/14 + 2 weapon skill: still 73 % death; the Boss (SP 13) was immune to pistols and dealt ~156 damage per fight.
3. Enemy armor and accuracy down (SP 0/2/4–6/5): all lifecycle targets pass; boss gigs 4× deadlier than elite gigs; 5 % stalemates.
4. Heat (round 6), Taunt = lose next action, repeatable Short circuit, Solo IRON 8 → 7, Elite up / Boss down: current numbers.
