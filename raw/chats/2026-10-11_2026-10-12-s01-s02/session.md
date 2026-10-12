# Development session digest — chats 2026-10-11 through 2026-10-12

Compiled from the parent Cursor chat and two subagent threads. Full transcripts are in this folder. The wiki holds facts and spikes; this file holds **what the user said and why it mattered**.

## Scope of these conversations

One continuous Cursor parent chat (`576c9d96-639c-4685-9f42-0bd1b0416dc8`) from first project planning through S-02 roof cast. Two subagent threads ran inside it: S-02 AMM source-read and B2 show-loop (both no-game).

## User constraints that came from chat (not only from docs)

- Use a Karpathy-style wiki as **working memory**, not a design constraint. Challenge any doc assumption.
- Twitch only. No paid effects on rules or dice (cosmetic paid effects OK for Season 0).
- Steam preferred. Game on **C: SSD**; D: is USB HDD for backups ([ADR-012](../../../wiki/decisions/ADR-012-install-path.md)).
- Do not commit unless asked (until session close).
- **S-01:** Do not teleport V to test cameras. Stay on the ripperdoc roof. Do not go downstairs. Do not throw V off the roof.
- Crowd density and composed "shots" are **not** important until much closer to going live. Prove cameras function first.
- Timed automatic cuts were too fast; user wanted a **button to change cameras** and hold each view. Roof prelim frames were "a good prelim."
- **S-02:** Spawn a small cast on the roof, one pose, freeze. Do not teleport V.
- User expected **screenshots to be shown**, not only filed under `raw/evidence/`.
- On the frozen frame: three actors **stacked in one volume** (gold hand through tattooed palm; chrome forearm through skin forearm). User corrected the agent reading it as "one body with others out of frame."
- **Close session** must include the chats, not only wiki + git. Conversations are important project memory.

## Conversation arc (user messages, in order)

### Planning and host setup (2026-10-11)

1. Optimize and plan the project; wiki as memory; full capability; everything changeable.
2. Game installed on C: SSD; D: is HDD.
3. Restore redscript.
4. CET overlay not opening (` key); thought mods were off — later fine.
5. Run the smoke test.
6. Proceed with Phase 0 leftovers; do I have to quit? — user already had OBS; quit for freeze; proceed.

### S-01 camera rig (2026-10-11 evening)

7. **S-01** — start camera spike.
8. Game crashed (HUD settings call).
9. Game reloaded.
10. **"i lost control and died"** — far camera parks teleported V off the roof.
11. **"why do you need to teleport my character?"** — user rejected streaming/crowd test rationale for parks.
12. On rooftop; do I need to go downstairs? — no.
13. Before anything: what does the procedure entail?
14. Why does street crowd matter? — user pushed back again.
15. **"we're not going live for a long while… shouldn't we make sure the cameras function first?"** — scope narrowed to API proof on the roof.
16. Proceed (twice; first in Ask mode blocked).
17. Cuts too fast; **make a button to change camera**. Screenshot provided.
18. **"this was a good prelim"**
19. What's next? — answered: S-02 first slice + B2 parallel.

### No-game parallel work (2026-10-12 morning)

20. Handle **both** S-02 pre-work and B2 in multitask while game is off — done via subagents.

### S-02 roof cast (2026-10-12)

21. Can you take screenshots yourself?
22. Game running — try capture.
23. **"game is up and you can screencapture. can you proceed?"** — S-02 in-game slice.
24. **"you didnt think i would want to see the screenshots?"**
25. **"everyone spawned on top of each other"** — leaving for work; pick up later.
26. **"you're reading the frozen frame as one body but look closer"** — stacked meshes confirmed.
27. Close session; GitHub repo https://github.com/bhoyte/cp2077-vtt
28. Close must **include the chats**; all convos are important.

## Subagent threads (summaries)

### S-02 pre-work (`subagents/74ef9ecd…`)

AMM 2.12.5 source-read: FreezeNPC, PlayAnimationOnTarget, SetNPCAttitude, no SetWeather, pose SQL from `db.sqlite3`. Evidence: [2026-10-12-s02-amm-source.md](../../evidence/2026-10-12-s02-amm-source.md).

### B2 show loop (`subagents/fca5001f…`)

Pure clock, L0 parser, FakeJev, vote book, ChatSim. 22 tests. Quorum N=3 assumed. No Twitch, ledger, or live Jev yet.

## Outcomes tied to these chats

| Topic | Result |
|---|---|
| Phase 0 | Smoke passed; stack frozen; F-019 exe launch verified |
| S-01 | Partial pass: own cameras cut/blend on roof; hotkeys; no parks; F-024 HUD stays |
| S-02 | Partial: three actors pose+freeze ok; **stacked at one point**; V unmoved |
| B2 | First slice in repo + tests |
| Git | `1432364` on `main` at first close; chat archive added in follow-up commit |

## Resume point

See [wiki/now.md](../../../wiki/now.md). Fix spawn separation before workspot samples position. Confirm with hand/arm crops, not a wide guess. Then frame from a roof camera.
