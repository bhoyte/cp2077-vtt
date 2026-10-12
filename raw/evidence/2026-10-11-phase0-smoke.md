# Phase 0 smoke — 2026-10-11

Bridge: `python tools/smoke_bridge.py` → `D:\night-city-live\server\bridge.py --port 2077 --interactive --quiet`.
Game already running (pid 44076). Cypher does not auto-reconnect; after CET reload of CypherAgent:

- 20:42:23 `[Cypher SOCKET] Disconnected`
- 20:42:33 `[Cypher SOCKET] Connected to Python bridge.`
- Bridge: `connected: ('127.0.0.1', 55886)` then sent `ammchars-1`, `spawnname-2`

CET `scripting.log`:
- `[Cypher AMM] characters total=19 showing=19`
- `character[4] name=Johnny Silverhand record=AMM_Character.Silverhand`
- `[Cypher] spawn queued logical_id=npc_test character=AMM_Character.Silverhand`
- 20:42:35 `[Cypher] spawn complete logical_id=npc_test`

Also tonight (earlier): RED4ext 1.30.0 + ArchiveXL 1.26.3 + Codeware 1.19.0 + RedSocket 0.5.0 on product 2.31; redscript compiled RedSocket/ArchiveXL/Codeware into `r6\cache\final.redscripts.modded`.
