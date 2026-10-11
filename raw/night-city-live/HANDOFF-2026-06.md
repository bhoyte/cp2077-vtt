# Workspace Handoff — June 2026

Context preserved from the Cursor chat when consolidating two related repos into **`night-city-live`** as the single working project. Read this if you return after a break and wonder why paths or docs don't match memory.

---

## The short version

| Question | Answer |
|----------|--------|
| **Which repo do I use?** | `d:\night-city-live` — open this folder in Cursor |
| **Where is `bridge.py`?** | `d:\night-city-live\server\bridge.py` (not in `cypher-vision`) |
| **Where is the CET mod source?** | `d:\night-city-live\cypher-vision\CypherAgent\` |
| **What happened to `d:\cypher-vision`?** | Shelved. Docs-only refactor + Phase 1 observer; never had the bridge |
| **What do I copy to the game?** | `init.lua`, `Cron.lua`, `cypher_json.lua` — **not** `json.lua` |

---

## Why there were two repos

Two folders diverged while the project was on pause:

### `d:\cypher-vision` (shelved)

- June 2026 doc refactor: lean `docs/`, archived old specs
- `CypherAgent/` reset to **Phase 1 observer only** (~65 lines, no RedSocket)
- Uses `json.lua` + `require("json")` — **breaks on many CET builds**
- **No `server/` or `bridge.py`** — docs incorrectly said "create python_server"

### `d:\night-city-live` (canonical)

- Real bridge implementation from before the pause
- `server/bridge.py` — async TCP on port 2077
- Full `init.lua` (~578 lines) — RedSocket, SceneSnapshot v0.1, AMM spawn
- `cypher_json.lua` — avoids CET `require("json")` name clash
- `cypher-vision/archive/` — copy of historical brainstorms

### Game install (what actually runs)

```
C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077\
  bin\x64\plugins\cyber_engine_tweaks\mods\CypherAgent\
```

This folder matched **night-city-live**, not the shelved cypher-vision workspace. Copying from `d:\cypher-vision\CypherAgent\` **downgraded** the working bridge mod back to observer-only.

---

## Strategic direction (unchanged)

**Build:** TTRPG-style interactive show — AI director + deterministic puppeteering.

**Not v1:** Fully autonomous NPCs, navmesh extraction, real-time LLM combat AI, gang-war simulation.

Python owns rules, dice, viewer votes, and encounter state. CET stages visuals at hand-placed markers. The LLM writes narration and beat plans on **phase transitions**, not every 200ms tick.

Visual summary: [TTRPG feasibility canvas](C:/Users/bento/.cursor/projects/d-night-city-live/canvases/ttrpg-feasibility-review.canvas.tsx).

---

## What's actually done (honest status)

| Phase | Status | Proof |
|-------|--------|-------|
| 1 Observer | Done | Player snapshot JSON every 200ms |
| 2 Wire | Done | `bridge.py` + RedSocket, SceneSnapshot v0.1 |
| 2.5 AMM spawn | Done | `spawnname`, `ammchars`, `setapp`, `despawn` |
| 3 Director | **Next** | Ollama beat plans from encounter state |
| 4 Puppet verbs | Planned | Unified `executeBeat()` at markers |
| 5 Encounter demo | Planned | Full negotiation scene end-to-end |

---

## Commands you'll forget again

From `d:\night-city-live` repo root:

```powershell
# Listen only (snapshots in terminal)
python server/bridge.py --host 127.0.0.1 --port 2077

# Interactive spawn (start BEFORE launching game)
python server/bridge.py --port 2077 --interactive --quiet --catalog catalog/curated.v1.example.json
```

In interactive mode:

```
help
ammchars 20          # read names in CET Console, not bridge terminal
spawnname npc_test Johnny Silverhand
list
despawn npc_test
```

**Prerequisites:** CET, RED4ext, RedSocket, **Appearance Menu Mod**.

**CET console should show:** `[Cypher SOCKET] Connected to Python bridge.` then `[Cypher] spawn complete ...` after spawn.

---

## CET lessons (hard-won)

1. **`require("modules.Cron")` fails** — `Cron.lua` must sit at mod root; use `require("Cron")`.
2. **`require("json")` often returns nil** — use `cypher_json.lua` + `require("cypher_json")`.
3. **RedSocket:** `RegisterListener` before `Connect`; no `\r\n` in send strings.
4. **Start bridge before the game** — connection refused otherwise.
5. **CET overlay pauses the game** — close it while testing movement.
6. **Spawn names are install-specific** — always `ammchars` first; copy exact name from CET console.

---

## What was migrated in June 2026

From `d:\cypher-vision` into `night-city-live`:

- Active `docs/` (00–04) — updated for bridge reality, not Phase 1-only fiction
- `cypher-vision/archive/README.md` — archive index
- `.cursorrules` at repo root
- TTRPG feasibility **canvas** recreated under Cursor project `d-night-city-live/canvases/`

`d:\cypher-vision` was **not deleted** — safe to archive or remove locally when you're confident.

---

## Recommended workflow going forward

1. Open **`d:\night-city-live`** in Cursor (not `cypher-vision`).
2. Edit mod in `cypher-vision/CypherAgent/`.
3. Copy three `.lua` files to game `mods\CypherAgent\`.
4. Run `server/bridge.py` before launching CP2077.
5. Read `docs/00-START-HERE.md` for day-to-day; this file for "why is everything in two places?"

---

## Related paths

| Path | Role |
|------|------|
| [docs/README.md](README.md) | Full doc index |
| [cypher-vision/README.md](../cypher-vision/README.md) | Mod install + bridge test steps |
| [cypher-vision/archive/](../cypher-vision/archive/) | Superseded specs |
| [bridge/bridge-protocol-v0.1.md](bridge/bridge-protocol-v0.1.md) | Wire format |
