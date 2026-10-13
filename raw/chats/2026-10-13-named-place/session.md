# Development session digest — 2026-10-13 morning

Compiled from the parent Cursor chat. Full transcript is in this folder. The wiki holds facts and spikes; this file holds what the user said and why it mattered.

## Scope

One Cursor parent chat (`c83b5494-4666-4ad5-a58c-a1d2f62c582c`). No subagent threads. The game stayed open on the ripperdoc roof. Nobody was standing there at the start.

## User constraints that came from chat

- The three can be spawned again whenever we need them. Do not treat leftover bodies as something to protect.
- A live broadcast will not match the last session. Do not be delicate about the world being exactly as we left it.
- Speak in plain language. "Booth" does not mean anything to the user. Say what the program does.
- `place` should take names, not always drop the same three. One name places that person. Several names place those people. Use the names as they appear in the character list. Design the command so an agent can run it well.
- The user reloaded the mods when asked, then sent a frame and called the result good.
- Spawning is a key part of the broadcast and the next thing to explore. Close the session here.

## Conversation arc

1. Open session. Last night's bridge was the resume. Nothing was listening for the game, and the roof had no people.
2. The user rejected keeping last night's cast, and rejected the jargon.
3. `place` was first written to always spawn Johnny, Hanako, and Song So Ri. The user changed that before it was used: the command must take names.
4. The running game was still on the older mod. The user reloaded it.
5. One command named the three. The reply gave measured positions. V did not move.
6. The user's frame shows them standing apart: Hanako in the center, Song So Ri on the left, Johnny on the right.
7. Close. Next session explores spawning, not posing.

## Outcomes

| Topic | Result |
|---|---|
| Named place | Passed for these three. F-030. The reply positions match a picture of three separate bodies. |
| Session | ArcadeLink 0.1.4. A person already spawned is moved, not copied. People not named stay. |
| Next | Spawning, as a tool the broadcast will depend on. Pose and freeze wait. |

## Resume point

See [wiki/now.md](../../../wiki/now.md). The lineup on the roof is disposable. The next work is learning how spawning should behave when the show is live.
