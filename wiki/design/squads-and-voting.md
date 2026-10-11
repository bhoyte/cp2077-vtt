---
type: design
title: Squads, joining, voting, and keeping every squad busy
status: draft
updated: 2026-10-11
depends_on: [ADR-004, ADR-010]
---

# Squads and voting

## Seats

| Seat | Command | Signature stat | Identity |
|---|---|---|---|
| Solo | `!solo` | IRON | Guns, breach, protection |
| Netrunner | `!net` / `!netrunner` | JACK | Cameras, quickhacks, turrets, lights |
| Tech | `!tech` | WRENCH | Medicine, cover, doors, devices |
| Face | `!face` | TALK | Taunts, deals, favors, negotiation |

## Membership rules
- Join by command or channel-point redemption. One seat per account per stream; one switch allowed per stream (betrayal is content: overlay announces the defector).
- Minimum account age / follow time (configurable) to join, to blunt alt-account brigading (R-12).
- Service record per viewer (ledger): votes cast, MVPs, characters lost, gigs survived. Shown in the lobby and on the memorial wall.

## Voting
- Options are numbered 1–4 (max four, "four buttons per joystick"). Each option is an action + target pair built by the director from rules-legal actions (see [ruleset](ruleset.md)).
- Live tally bars per option; voter count; lock-in indicator.
- Free text ("smoke the boss from the left column") counts through Jev (ADR-004) and gets highlighted in the comms box when it decides the vote: it's rewarded, not just tolerated.

## Low-population behaviour (R-05)
- **Open seat.** If a squad has fewer than `N_min` (default 2) active members in the last 10 min, its window is open to the whole crew, with an "OPEN SEAT" banner. It reverts automatically when the squad refills.
- **Temperament default.** Zero votes → the character acts by its own temperament (reckless / cautious / loyal / greedy, set at creation), picking from its options by a fixed priority. Quiet chat still produces character, not "take cover" loops.
- **Attract mode.** Pre-show and when chat is empty: the cabinet plays itself on a demo gig with temperament defaults and an "INSERT COIN — type !solo !net !tech !face" banner.

## Keeping inactive squads engaged
- **Comms box.** Messages from non-active squads appear in a squad-colored comms feed (spec §4A).
- **Assist (experiment E-1).** During another seat's window, any squad can spend its once-per-encounter Assist if ≥ 50 % of its active members type `!assist` → +2 to that roll. Tests whether cross-squad coordination ("Techs, assist the Solo!") emerges. Kill it if it adds noise.
- **Telegraphed enemy intent.** The Netrunner's Ping shows next round's enemy plan to everyone, so all squads have something to argue about.
- **Squad directives.** Each gig gives each squad a public bonus objective that may conflict (Face: keep the target alive for a bonus; Solo: bounty if he dies), straight from the philosophy doc.
