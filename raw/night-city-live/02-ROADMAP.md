# Roadmap

Phased plan with honest CET limits. Each phase should produce something testable before moving on.

---

## Phase 1 — Observer ✅ DONE

**Goal:** Prove CET can read game state and emit JSON.

**Delivered:**
- `cypher-vision/CypherAgent/init.lua` polls every 200ms via `Cron.Every(0.2, ...)`
- Snapshot: player position, facing, `is_in_combat`, `is_dead`
- JSON via `cypher_json.lua` (avoids CET `require("json")` clash)

**Test:** JSON lines ~5×/sec; values change when you move/fight.

---

## Phase 2 — The Wire ✅ DONE

**Goal:** Two-way TCP between game and Python.

**Delivered:**
1. `server/bridge.py` — async TCP on `127.0.0.1:2077`, `\r\n`-delimited messages, `BridgeAck` responses
2. `init.lua` — RedSocket connect, `SceneSnapshot v0.1` each tick, command envelope handler
3. Protocol docs: [bridge/bridge-protocol-v0.1.md](bridge/bridge-protocol-v0.1.md), [bridge/bridge-evidence-log.md](bridge/bridge-evidence-log.md)

**Test:** Walk in-game → coordinates appear in Python terminal; CET logs `[Cypher SOCKET] Connected`.

**CET notes:**
- `GetMod("RedSocket")` must not be nil
- `RegisterListener` before `Connect`
- Do not include `\r\n` in send strings
- Start `bridge.py` before launching the game

---

## Phase 2.5 — AMM Spawn Lab ✅ DONE (bridge milestone)

**Goal:** Prove Python can spawn and manage NPCs via Appearance Menu Mod.

**Delivered:**
- Bridge commands: `amm_spawn_npc`, `amm_set_appearance`, `amm_despawn_npc`, `amm_list_characters`, etc.
- Interactive CLI in `bridge.py` (`spawnname`, `ammchars`, `setapp`, `despawn`)
- Curated catalog preflight: `catalog/curated.v1.example.json`

**Test:** `python server/bridge.py --port 2077 --interactive --quiet` → `spawnname npc_test Johnny Silverhand` → NPC appears in front of player.

**Not yet:** beat-plan executor, encounter markers, attitude/animation verbs as a unified vocabulary.

---

## Phase 3 — The Brain (Director, not fighter)

**Goal:** Ollama generates scene narration and beat plans from encounter state — not real-time combat decisions.

**Build:**
1. `server/encounter.py` (or module) — encounter state machine (phases: setup → vote → resolve → staging)
2. `server/director.py` — Ollama call with structured output (Pydantic schema for beats + lines)
3. Director input = state + dice result + viewer choice. Output = beat plan JSON (see [04-ENCOUNTER-SYSTEM.md](04-ENCOUNTER-SYSTEM.md))

**Test:** Type a viewer choice in terminal → get back narration + verb list. Game optional for this phase.

**Rate limit:** One LLM call per phase transition, not every 200ms tick.

**Effort:** ~1–2 weekends.

---

## Phase 4 — Puppet Verbs

**Goal:** CET executes a fixed verb vocabulary at encounter markers.

**Minimum verb set:**

| Verb | CET approach | Status |
|------|----------------|--------|
| `spawn_npc` | AMM `SpawnNPC` (via bridge command today) | ✅ via `amm_spawn_npc` |
| `despawn_npc` | AMM despawn + registry cleanup | ✅ via `amm_despawn_npc` |
| `move_to_marker` | `TeleportationFacility:Teleport(npc, pos, rot)` | Planned |
| `set_attitude` | `GetAttitudeAgent():SetAttitudeGroup(...)` | Planned |
| `play_animation` | Workspot system (study CyberScript / AMM source) | Planned |
| `show_subtitle` | CET overlay or `print` + OBS capture | Planned |
| `set_weather` / `set_time` | Game time/weather APIs (optional polish) | Optional |

**Build:**
1. `encounters/kabuki_alley_01.json` — marker coordinates + NPC definitions
2. `init.lua` — `executeBeat(plan)` loops verbs with error logging
3. Hotkey or bridge command to load encounter and run a test beat

**Test:** Python sends one beat → NPC teleports to marker and plays an animation.

**Effort:** 2–4 weekends (animations are the research sink).

---

## Phase 5 — TTRPG Encounter Demo

**Goal:** One complete scripted encounter end-to-end.

**Suggested scene:** Alley negotiation — fixer wants eddies, viewer picks talk / intimidate / walk away, dice decides outcome, puppet layer stages result.

**Flow:**
1. Load encounter markers in an alley
2. Present choices (terminal input simulates viewer vote)
3. Roll dice in Python (authoritative)
4. Director writes dialogue + beat plan
5. CET stages visuals
6. State updates (fixer attitude, player rep)

**Test:** Record a 2–3 minute clip showing vote → dice → staged outcome.

**Effort:** 1–2 weekends after Phase 4.

---

## Beyond Phase 5 (v2+ ideas)

Not scheduled. Documented so old brainstorms have a home.

| Idea | Summary | Blocker |
|------|---------|---------|
| **Live stream integration** | Twitch/YouTube chat votes → Python | Needs overlay + chat bot |
| **Campaign ledger** | SQLite memory across sessions | Phase 5 stable first |
| **Macro/micro gang sim** | Python simulates factions; game spawns hit squads when player enters cell | Scale + content authoring |
| **Smallville in Night City** | Multiple autonomous agents | Conflicts with puppet model; revisit later |

---

## Prerequisites checklist

- [ ] Cyberpunk 2077 + REDmod DLC
- [ ] CET + RED4ext installed, overlay works
- [ ] RedSocket installed
- [ ] Appearance Menu Mod installed (spawn commands)
- [ ] Python 3.10+ (bridge uses stdlib only — no pip for Phase 2)
- [ ] `pip install ollama pydantic` (Phase 3+)
- [ ] Ollama + `llama3.2:3b` pulled (Phase 3+)

Install details were in the old v0.1 spec; still valid. See [cypher-vision/archive/cypher_v01_spec.md](../cypher-vision/archive/cypher_v01_spec.md) if needed.
