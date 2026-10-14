# Development session digest — 2026-10-13 evening through 2026-10-14

Compiled from the parent Cursor chat. Full transcript is in this folder. The wiki holds facts and spikes; this file holds what the user said and why it mattered.

## Scope

One Cursor parent chat (`4a7ef6f8-cc7e-4edf-ae05-5478256c9c30`), plus one compaction segment. No subagent threads. The game stayed open on the ripperdoc roof. The cast was Johnny Silverhand, Hanako, and Song So Ri.

## User constraints that came from chat

- Keep placement simple. Change the side-by-side line into a single file, same spacing, first name closest to V. They still face her.
- Then a wedge: first name at the point, second on V's left rear, third on her right rear, about 1.6 m apart.
- Then sequential control. Spawn and despawn each of the three, one at a time, in rank, file, and wedge. The user wanted to watch each step. Only one person in the world at a time.
- The lineup is disposable. Do not move V. Pose and freeze stay deferred.
- Speak in plain language. Do not say "booth."
- "proceed" means the mods were reloaded. Run the live command. Do not place against an old in-memory version.
- A radius sweep of nearby people is too aggressive for street level. Remove only people we spawned. Tag them so a reload that empties the appearance menu does not forget them.
- Reloading the mod will keep happening. Note those quirks; they can show up on a stream.
- User frames are evidence.

## Conversation arc

1. Open on the morning handoff. The user asked for a single file instead of side by side. The frame showed Johnny nearest, then Hanako, then Song So Ri.
2. A wedge followed. Frames showed the three apart, and other bodies still standing farther down the roof. The user called that the way, and asked to despawn everyone.
3. An 18 m sweep was written and then rejected before it was relied on. Clear stayed on the appearance-menu list. After a reload that list was empty, so clear removed nobody while bodies could remain.
4. Place began writing entity ids to `tagged.json`. A clear after the next reload removed exactly those three.
5. A slot command put one name on one mark of rank, file, or wedge. The first sequence spawned Johnny on rank slot 1, then the despawn never replied. Moving clear onto the next game frame still failed: the menu name came back from a text replace that also returns a count, and the list insert treated the name as a position. The user's frame shows Johnny still standing.
6. The fix kept only the name. After one reload, a clear took Johnny off the roof. Then all nine steps completed. Each despawn removed that one person. V did not move. The roof was empty.
7. Close.

## Outcomes

| Topic | Result |
|---|---|
| File and wedge | Observed. File at about 2.7 m, then 1.6 m steps. The first wedge slid to about 7.5 m because nearer marks were taken. |
| Surgical clear | The menu list only, plus tags within 80 m. No street sweep. |
| Tags | Survive a mod reload. `clear` removed the tagged three when the menu list was empty. |
| Sequential slots | Passed on ArcadeLink 0.1.12. Nine cycles, unshifted marks, one person at a time. |
| Still open | Occupied-mark slide (R-16). People spawned before tagging have no tag. Pose and freeze have not run on these formations. |

## Resume point

See [wiki/now.md](../../../wiki/now.md). ArcadeLink in the running game at close was 0.1.12. The roof was empty. Next work is pose and freeze on a formation that stays up.
