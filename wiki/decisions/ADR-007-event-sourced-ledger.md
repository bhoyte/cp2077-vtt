---
type: decision
id: ADR-007
title: Event-sourced state in SQLite (the Ledger)
status: accepted
updated: 2026-10-11
revisit_if: Event volume makes replay on restart slower than 2 s (add snapshots)
depends_on: []
---

# ADR-007 — Event-sourced ledger

**Decision.** Every fact the show produces is an append-only event in SQLite: `vote.cast`, `window.closed`,
`roll`, `damage.applied`, `death_save`, `character.flatlined`, `beat.played`, `operator.paused`, … Current state is a
pure fold over events (`rules.apply(state, event)`).

**Gets us.**
- Crash recovery: restart the orchestrator, replay, and it's back in the exact state.
- Audit: the dice log (ADR-006) and vote attribution come straight from the table.
- Highlights: timestamps of crits, deaths, and clutch saves feed VOD clipping and the memorial wall.
- Wiki ingestion: post-show reports are generated from the ledger into `raw/sessions/` (playtest-ingest op).
- Campaign persistence across episodes (characters, eddies, faction heat, viewer service records).

**Shape.** `events(seq INTEGER PK, ts, session_id, type, payload_json)` plus projection tables rebuilt from events. Stdlib `sqlite3`.
