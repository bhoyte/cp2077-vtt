---
type: decision
id: ADR-001
title: This repo is canonical; night-city-live is an upstream to port from, not to continue
status: accepted
updated: 2026-10-11
revisit_if: Porting the bridge costs more than 2 days
depends_on: [F-001, F-004]
---

# ADR-001 — Canonical repo

**Context.** Three folders hold versions of this idea: `D:\cypher-vision` (shelved), `D:\night-city-live` (working bridge,
single-protagonist LLM-GM vision), and this repo (arcade-cabinet vision). The 2026-06 handoff shows a regression
caused by editing the wrong copy.

**Decision.** `c:\Users\bento\Desktop\cp2077-vtt` is the only place work happens. From night-city-live we **port**
(not copy wholesale): the RedSocket client loop, the AMM spawn adapter, `cypher_json.lua`/`Cron.lua`, the catalog
SQLite builder, and the hard-won CET lessons (now facts F-001…F-013). The prior docs are frozen in `raw/night-city-live/`.

**Consequences.** The CET mod gets a new name (`ArcadeStage`) and a new protocol version (`stage.v1`), so the old and
new mods can never be confused in the game folder. night-city-live stays read-only.

**Rejected.** Continuing night-city-live in place: its docs encode a different product (LLM GM, one Chat-V, Ollama in the loop).
