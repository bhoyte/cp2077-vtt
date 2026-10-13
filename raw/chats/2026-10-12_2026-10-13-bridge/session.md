# Development session digest — 2026-10-12 evening through 2026-10-13

Compiled from the parent Cursor chat. Full transcript is in this folder. The wiki holds facts and spikes; this file holds what the user said and why it mattered.

## Scope

One Cursor parent chat (`53c6db4a-4e2d-422a-8152-3a4d2dd228ef`). No subagent threads. The game stayed open on the ripperdoc roof. The previous session's three actors were still in the world at the start.

## User constraints that came from chat

- Place Johnny, Hanako, and Song So Ri in front of V, not stacked. Do not teleport V. Do not despawn them until the user has looked. Take screenshots and show them.
- The user corrected a stacked reading again with their own frames (day and night).
- Reloading the CET overlay during a livestream is unacceptable. The bridge has to survive the operator coming and going.
- This is not a product that runs itself. An agent is the operator from the start. Tools, not a scheduler.
- OBS and Twitch are premature while placement and the socket are still the problem.
- Do not stretch the Cypher proof-of-concept into the show engine. Build a session for the job.
- Do not quit the game to write that session. The cast stays.
- Close session includes the chat archive.

## Conversation arc

1. Open session. Resume was the stacked roof cast.
2. Game is up. Separate the three, leave them, capture frames.
3. Several reloads missed the listener because Cypher dials once and the probe was not up yet.
4. `TeleportationFacility:Teleport` returned ok and never moved them. User: "still on top of each other."
5. `Tools:TeleportNPCTo` put them on three marks. User: "good job, you got it."
6. That success raised the real problem: a livestream cannot depend on Reload all mods. The user wants an agent to run the broadcast, so the bridge is the harness.
7. Parallel Track B (OBS, Twitch) is early. Focus on the bridge.
8. Reimagine the session instead of mutating the proof. Agreed shape: the game keeps the pieces, redials, answers `status` with measured positions. A process holds port 2077 and does not exit after one cast.
9. What we are building is an operated table. The broadcast waits. ADR-013 records that.
10. Built ArcadeLink and `tools/booth.py`. CypherAgent stopped dialing. First hello and `status` worked. `IsConnected` stayed true after the booth died, so that build did not redial. A booth ping every second fixed it.
11. 02:24 redial verified with no second reload. `status` returned V at -1536.78, 1195.77, 57.00. The three were not commanded.

## Outcomes

| Topic | Result |
|---|---|
| S-02 separation | Passed for three actors. Facility teleport does not move fresh AMM puppets (F-008 note). `TeleportNPCTo` does (F-028). |
| Session | ArcadeLink 0.1.2 redials without a CET reload (F-029). `status` only. Actor list still empty. |
| Show | Twitch, OBS, beat timelines, and the reconciler stay later (ADR-013). |

## Resume point

See [wiki/now.md](../../../wiki/now.md). Next command is `place` on this session, using `TeleportNPCTo`, reply includes measured positions. Do not teleport V. Do not reload CET to send a command. The booth should already be the way in.
