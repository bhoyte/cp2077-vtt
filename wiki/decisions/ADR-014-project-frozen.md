---
type: decision
id: ADR-014
title: Freeze the project; Night City still has no live director
status: accepted
updated: 2026-10-15
revisit_if: the user explicitly reopens, or a live director exists for a world with this weight
depends_on: [ADR-003, ADR-013]
---

# ADR-014 — The project is frozen

**Context.** Place and clear of one named person already work (ArcadeLink 0.1.12). The user wanted full spawn control for a campaign, a promo, and machinima, including people sitting and lying on real furniture, with chat choosing the path while the game is on. Feature-by-feature puppetry, World Builder, Native Interactions, and sit-anywhere mods were weighed against that. A recorded gunfight was rejected as too small. A board-game loop with the game off was rejected as not the show.

The same limit shelved the project once before. REDmod is still a compiler for scripts, tweaks, sounds, and animations. It is not a live hand on a person, a chair, or a camera. The working ceiling is still CET, the appearance menu, and World Builder. No other current game has Night City's weight and that hand. The ones that can seat a person ship an editor, and then the city is yours to build.

**Decision.**

- Development stops. Do not resume pose, furniture, a campaign slice, or further mod stacking unless the user reopens.
- The design already written stays written. Gates stay defined. They are not in progress.
- The last verified cast state stands. ArcadeLink 0.1.12 can place and clear one named person on an empty rank, file, or wedge mark. Tags survive a reload. V is not moved. The street is not swept. The occupied-mark slide (R-16) stays recorded and is not being fixed.
- The stack pin is unchanged (ADR-012).

**Rejected.** Treating a map-only loop as the vertical slice. Treating one action sequence as proof of a campaign. Switching games to escape the compromise.
