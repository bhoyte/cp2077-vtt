---
type: decision
id: ADR-002
title: Game transport is RedSocket TCP with JSON lines (replaces action_event.json polling)
status: accepted
updated: 2026-10-12
supersedes: spec §4D "CET listens on onUpdate for action_event.json"
revisit_if: RedSocket breaks on a future patch and isn't updated within 2 weeks
depends_on: [F-001, F-002]
---

# ADR-002 — Transport

**Context.** The spec polls a JSON file every frame. CET's file I/O is sandboxed to the mod folder, file polling needs
atomic-rename discipline, and it has no back-channel. RedSocket TCP is already verified on 2.31 (F-001).

**Decision.**
- Python orchestrator = TCP server on `127.0.0.1:2077`; CET `ArcadeStage` mod = client.
- One JSON object per line; envelope `{type, v:"stage.v1", id, op, args}`; game replies with `ack`/`report` messages ([contracts](../components/contracts.md)).
- CET retries the connection with backoff, so start order no longer matters (verify in S-04).
- Whole beat timelines are sent at once and **timed inside the game** (Cron), so network jitter never affects cut timing.

**Live session.** Until a show exists, the protocol on this socket is `table.v0` ([ADR-013](ADR-013-operated-table.md)): the client redials, and the only request is `status`. `stage.v1` waits.

**Fallback.** File-drop transport (`inbox/NNNN.json`, written with atomic rename) behind the same interface, kept for emergencies only.
