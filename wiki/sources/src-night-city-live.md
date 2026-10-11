---
type: source
title: Prior project night-city-live (D:\night-city-live) — evidence and reusable assets
status: current
updated: 2026-10-11
raw: [raw/night-city-live/bridge-evidence-log.md, raw/night-city-live/bridge-protocol-v0.1.md, raw/night-city-live/03-CET-MOD-REFERENCE.md, raw/night-city-live/01-ARCHITECTURE.md, raw/night-city-live/02-ROADMAP.md, raw/night-city-live/04-ENCOUNTER-SYSTEM.md, raw/night-city-live/HANDOFF-2026-06.md, raw/night-city-live/night-city-live-ruleset-design.md, raw/night-city-live/perplexity-deep-search-brief.md, raw/night-city-live/sanity-check-ttrpg-live-stream.md, raw/night-city-live/amm_universe_summary.md]
---

# Source: night-city-live (March–July 2026)

**What it was.** An LLM-GM TTRPG show with one chat-controlled V, Ollama writing beat plans, and CET puppeteering via AMM.
Its Milestone 0 and 0.5 were completed and documented with evidence. That evidence is now F-001…F-006 and F-010.

## Reusable assets (port per ADR-001)
| Asset | Path | Use |
|---|---|---|
| CET mod with RedSocket client, AMM spawn adapter, command dispatcher (~578 lines) | `D:\night-city-live\cypher-vision\CypherAgent\init.lua` | Basis of ArcadeStage |
| `cypher_json.lua`, `Cron.lua` | same folder | As-is (F-003) |
| Async TCP bridge (stdlib) | `D:\night-city-live\server\bridge.py` | Basis of `stage/` server + smoke test |
| AMM catalog SQLite builder + 20 MB index | `server/build_amm_universe_sqlite.py`, `catalog/amm_universe.sqlite` | Pose/FX/actor discovery for S-02/S-03 and the curated catalog |
| Catalog allowlist pattern | `server/catalog.py`, `catalog/curated.v1.*.json` | Curated pawns per seat |
| AMM source snapshot | `D:\night-city-live\AppearanceMenuMod\` | Source-reading for F-013 |

## Lessons carried forward
Never invent CET APIs (their `.cursorrules` lists fabricated ones) · start-order fragility (→ reconnect, S-04) · spawn names are install-specific (→ curated catalog with records, not names) · edit one repo only (→ ADR-001).

## Where the new plan diverges
Live LLM director → offline authoring + selection (ADR-009). One protagonist → four seats with initiative (ADR-005).
Abstracted scene-level combat → initiative-level combat (turn order is the squad structure). Its "Death Counter" (3 rounds,
audience intervention) survives in spirit as death saves + Tech Stabilize.

## Also on disk (not ingested yet)
`D:\cppc` audio-drama pipeline: lore integration framework, Cyberpunk linguistics guide (slang for barks), Hailuo i2v and ElevenLabs tutorials. **Ingest candidates** for P4 content work.
