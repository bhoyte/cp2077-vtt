---
type: decision
id: ADR-013
title: The live work is an operated table; the session redials and answers status
status: accepted
updated: 2026-10-12
revisit_if: a self-running show is what we actually take on air
depends_on: [F-001, F-002, ADR-009]
---

# ADR-013 — Operated table

**Context.** The overview describes an orchestrator that plays the show, a reconciler that heals the scene, and a loop that can run with the game off. The bridge in the repo is a proof that JSON lines cross RedSocket: CypherAgent dials once inside `onInit`, prints results to `scripting.log`, and a one-shot probe scrapes that log. A failed dial never retries (F-002). Reloading the CET overlay is the only way back, and a reload forgets Lua handles while the bodies stay in the world.

The operator of this project is a person working with an agent. Chat, Twitch, and OBS are how an audience uses the table later. They are not the next tool.

**Decision.**

- Night City Arcade is an operated table. Cyberpunk 2077 is the table. Rules and dice stay deterministic (ADR-009). An agent calls tools; it does not invent outcomes.
- The first tool is the **session**. The game keeps the pieces. `ArcadeLink` dials `127.0.0.1:2077` and, while down, destroys the socket and dials again every 2 seconds. On attach it sends `hello`. The only request it answers is `status`. The reply is on the socket, with the same id, and includes the measured player position. The actor list is empty until a later cut.
- `tools/booth.py` binds that port and stays up. It is not a cast script and it does not decide a show. `booth.py status` prints the reply.
- CypherAgent no longer dials. The log-scraping probe is not the way in. `stage.v1` beat timelines and the reconciler stay written down for later (ADR-002, ADR-003). They are not this session.
- One CET reload loads this mod. After that, restarting the booth must not require another reload.

**Not in this cut.** `place`, `pose`, `freeze`, `clear`, cameras, Twitch, OBS.
