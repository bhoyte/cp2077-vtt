---
type: component
title: Ledger — SQLite event store and projections
status: draft
updated: 2026-10-11
depends_on: [ADR-007]
---

# Ledger

- File: `data/ledger.sqlite` (gitignored), WAL mode, one writer (orchestrator).
- `events(seq INTEGER PRIMARY KEY, ts_ms INTEGER, session_id TEXT, type TEXT, payload TEXT)` — append-only.
- Projections (rebuildable): `characters`, `viewers`, `squad_members`, `memorials`, `crew` (eddies, heat), `rolls`.
- Snapshots every 500 events per session for fast restart (only if replay > 2 s, ADR-007 revisit).
- **Session report** generator → `raw/sessions/YYYY-MM-DD-<session>.md`: pacing stats (window lengths, lock-in rate, votes per window per squad), deaths, crits, Jev hit rate, desync incidents. The wiki ingests it (playtest-ingest op), so design pages learn from every show.
