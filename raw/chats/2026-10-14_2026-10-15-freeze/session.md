# Development session digest — 2026-10-14 evening through 2026-10-15

Compiled from the parent Cursor chat. Full transcript is in this folder. The wiki holds the freeze; this file holds what the user said and why it mattered.

## Scope

One Cursor parent chat (`aaa7611a-c182-47ed-b0a0-c0df68d72209`). No subagent threads. No compaction segment. No live game commands. The user was in V's apartment for one frame. ArcadeLink stayed 0.1.12.

## User constraints that came from chat

- Full spawn control for a campaign, promo material, and campaign machinima, without hashing out one formation at a time.
- They would rather the agent infer the destination than be told each layout.
- A CET reload cannot be assumed. They asked if it could be done from this side. It cannot.
- Environment interaction matters. Two people on the couch and one on the bed, in this apartment, was the example.
- Chat drives decisions live. A replay of a campaign that already happened is a different, easier problem. A cut-together action scene does not prove a campaign.
- The game has to be on for a vertical slice. A map with the game off is not the show.
- Compromises are why this was shelved the first time. They had hoped the tech would have caught up.
- Speak in plain language. Do not say "booth."

## Conversation arc

1. Opened on the formations handoff. Place and clear of one person work. Pose was the written next step.
2. The user asked for the whole spawn surface, not another formation. The destination named was one person, one mark, an optional pose, an optional freeze, and a saved cast file.
3. They asked about sitting on real furniture. The pose system spawns an invisible seat at the person's feet. The apartment couch and bed are never queried. Lining a clip up by eye is possible. Using the furniture is not what the current path does.
4. World Builder can bake people onto spots when a room loads. Sit-anywhere and Native Interactions are prompts for V, or more pose clips. None of them take a person `place` spawned and sits them on the couch.
5. They recognized that path as a quest mod. The table was restated as marks, held poses, and cuts. They accepted the logic, then said live chat still has to be ready for a campaign, not one gunfight.
6. A recorded exchange was rejected as too tactical. The chat, dice, and seats can be simulated, and they said the game still has to be on or it is not a vertical slice. The slice that matches that is one gig, watched in the city, choice then roll then picture.
7. They said the compromises keep growing, which is why they shelved it before. No current game has Night City's weight and a live director. REDmod is still a compiler. Editors that can seat a person make you build the city.
8. They froze the project and closed the session.

## Outcomes

| Topic | Result |
|---|---|
| Spawn control | Named, not built. Person, mark, facing, pose, freeze, cast file. Formations stay shortcuts. |
| Furniture | Not available as a command. Alignment is a saved mark. World Builder bakes a different cast. |
| Campaign proof | A gunfight does not prove it. A map with the game off does not prove it. The slice would be one gig in the city. Not started. |
| Other games | None have this world and that hand. |
| Freeze | [ADR-014](../../../wiki/decisions/ADR-014-project-frozen.md). Do not resume unless the user reopens. |

## Resume point

See [wiki/now.md](../../../wiki/now.md). The project is frozen. ArcadeLink in the running game was still 0.1.12. No cast was placed in this stretch.
