---
type: decision
id: ADR-013
title: The live work is an operated table; the session redials and answers status
status: accepted
updated: 2026-10-13
revisit_if: a self-running show is what we actually take on air
depends_on: [F-001, F-002, ADR-009]
---

# ADR-013 — Operated table

**Context.** The overview describes an orchestrator that plays the show, a reconciler that heals the scene, and a loop that can run with the game off. The bridge in the repo is a proof that JSON lines cross RedSocket: CypherAgent dials once inside `onInit`, prints results to `scripting.log`, and a one-shot probe scrapes that log. A failed dial never retries (F-002). Reloading the CET overlay is the only way back, and a reload forgets Lua handles while the bodies stay in the world.

The operator of this project is a person working with an agent. Chat, Twitch, and OBS are how an audience uses the table later. They are not the next tool.

**Decision.**

- Night City Arcade is an operated table. Cyberpunk 2077 is the table. Rules and dice stay deterministic (ADR-009). An agent calls tools; it does not invent outcomes.
- The first tool is the **session**. `ArcadeLink` dials `127.0.0.1:2077` and, while down, destroys the socket and dials again every 2 seconds. On attach it sends `hello`. It answers `status` and `place`. Both replies are on the socket, with the same id, and include the measured player position.
- The world will not match the last visit. `place` takes character-list names. One name puts that person in front of V. Several names in one call put those people in a line, in that order. It does not move V, and it does not move or remove anyone the call did not name. A person already spawned under that name is moved, not copied. The reply is where they actually are, using the list's spelling.
- `tools/booth.py` binds that port and stays up. It is not a cast script and it does not decide a show. `booth.py status` prints where V is. `booth.py place "Hanako"` places one person. Extra arguments place those people.
- CypherAgent no longer dials. The log-scraping probe is not the way in. `stage.v1` beat timelines and the reconciler stay written down for later (ADR-002, ADR-003). They are not this session.
- One CET reload loads this mod. After that, restarting the listener must not require another reload. A new command still needs one reload so the running game picks up the new file.

**Not in this cut.** `pose`, `freeze`, cameras, Twitch, OBS.
