# Encounter System

Design doc for TTRPG-style interactive encounters: authoritative state in Python, AI-generated narration, deterministic staging in CET.

---

## Core loop

```
Setup → Present choices → Collect vote → Roll dice → Resolve → Stage beat → Update state → (repeat or end)
```

**Turn-based.** The LLM may take seconds. The game waits on Python, not the reverse.

---

## Encounter definition

Store per encounter (JSON or YAML in `encounters/`):

```json
{
  "id": "kabuki_alley_negotiation",
  "location": "Watson, Kabuki — alley behind noodle stand",
  "markers": {
    "player": {"x": 0, "y": 0, "z": 0, "yaw": 180},
    "npc_fixer": {"x": 2, "y": 0, "z": 0, "yaw": 0},
    "camera_wide": {"x": -3, "y": 5, "z": 2}
  },
  "npcs": {
    "npc_fixer": {"archetype": "Character.xxx", "role": "fixer"}
  },
  "phases": ["intro", "negotiation", "resolution"]
}
```

Markers are hand-authored in-game (read position from bridge snapshots / CET console), not navmesh-derived.

For NPC spawn today, use AMM catalog names from `ammchars` in `bridge.py` interactive mode. Encounter JSON should store the resolved `amm_name` or `record` per NPC.

---

## Encounter state (Python, authoritative)

```json
{
  "encounter_id": "kabuki_alley_negotiation",
  "phase": "negotiation",
  "player": {"hp": 80, "eddies": 450, "rep_fixers": 2},
  "npcs": {"npc_fixer": {"hp": 60, "attitude": "neutral"}},
  "last_vote": null,
  "last_roll": null,
  "history": []
}
```

Viewer choice + dice roll **mutate this object**. The director reads it; it does not invent HP or outcomes.

---

## Viewer choice + dice flow

1. **Director presents scene** — narration text + 2–4 options with skill tags
2. **Vote window** — chat poll, terminal input, or timed default (for offline dev)
3. **Resolve choice** — e.g. `"intimidate"` (Cool check)
4. **Roll** — `1d10 + skill + modifier` vs difficulty (Cyberpunk RED–style, simplified)
5. **Outcome tier** — critical fail / fail / success / critical success
6. **Director writes beat** — dialogue + `verbs[]` for CET
7. **State update** — attitude change, eddies lost, rep shift

### Example roll (terminal dev mode)

```
Options: [1] Pay 200 eddies  [2] Intimidate (Cool)  [3] Walk away
Choice: 2
Roll: 1d10(7) + Cool(4) = 11 vs DV 12 → FAIL
Outcome: fixer calls backup
```

---

## Scene beat schema

What Python sends to CET:

```json
{
  "beat_id": "intimidate_fail",
  "narration": "You step forward. The fixer's hand twitches toward his iron.",
  "lines": [
    {"speaker": "fixer", "target": "npc_fixer", "text": "Wrong move, choom."}
  ],
  "verbs": [
    {"verb": "play_animation", "target": "npc_fixer", "args": {"anim": "gesture_threaten"}},
    {"verb": "set_attitude", "target": "npc_fixer", "args": {"group": "hostile"}},
    {"verb": "spawn_npc", "args": {"id": "alley_thug_b", "amm_name": "Maelstrom Grunt", "marker": "alley_thug_b"}},
    {"verb": "show_subtitle", "args": {"text": "Backup arriving.", "duration": 4}}
  ],
  "next_phase": "combat_or_flee"
}
```

CET executes `verbs` in order. Use `Cron.After` between steps if pacing matters.

**Today:** `spawn_npc` maps to the existing `amm_spawn_npc` bridge command. Other verbs are Phase 4 work.

---

## Visual verb vocabulary (v1)

| Verb | Args | CET action | Status |
|------|------|------------|--------|
| `spawn_npc` | `id`, `amm_name` or `record`, `marker` | AMM spawn at marker offset | ✅ low-level |
| `despawn_npc` | `id` | AMM despawn | ✅ low-level |
| `move_to_marker` | `target`, `marker` | Teleport | Planned |
| `set_attitude` | `target`, `group` | hostile / friendly / neutral | Planned |
| `play_animation` | `target`, `anim` | Workspot animation | Planned |
| `show_subtitle` | `text`, `duration` | On-screen text | Planned |
| `wait` | `seconds` | Delay next verb | Planned |

Extend only after Phase 4 proves the minimum set.

---

## Negotiation example (full beat sequence)

**Scene:** Fixer wants 500 eddies for a datapad location. Player has 450.

| Phase | Viewer options | Dice | Staged outcome |
|-------|----------------|------|----------------|
| intro | — | — | Spawn fixer, wide camera, director sets scene |
| negotiation | Pay / Haggle (Persuasion) / Intimidate (Cool) / Leave | Per choice | Different verb chains |
| resolution | — | — | State updated; encounter ends or escalates |

**Haggle success (example verbs):**
```json
{
  "verbs": [
    {"verb": "play_animation", "target": "npc_fixer", "args": {"anim": "think"}},
    {"verb": "show_subtitle", "args": {"text": "350 eddies. Final offer.", "duration": 3}}
  ],
  "state_delta": {"player.eddies": -350, "player.rep_fixers": 1}
}
```

**Intimidate crit success:**
```json
{
  "verbs": [
    {"verb": "play_animation", "target": "npc_fixer", "args": {"anim": "cower"}},
    {"verb": "set_attitude", "target": "npc_fixer", "args": {"group": "friendly"}}
  ],
  "state_delta": {"player.eddies": -200, "player.rep_fixers": -1}
}
```

---

## AI director prompt (sketch)

System role: *Cyberpunk encounter director. You receive authoritative state and dice results. Output narration and a beat plan using only the allowed verb list. Never contradict state. Never invent dice outcomes.*

Structured output via Ollama `format` + Pydantic model matching beat schema.

**Input:** encounter state + outcome tier + choice made  
**Output:** `narration`, `lines[]`, `verbs[]`, `state_delta`, `next_phase`

---

## What the director must NOT do

- Decide dice results (Python rolls)
- Issue arbitrary coordinates (use marker names)
- Call unimplemented verbs
- Run combat turn-by-turn in real time (stage outcomes, not simulate gunfights)

Combat in v1 = narrative beat + attitude change + spawn/despawn. Full shootout simulation is out of scope.

---

## Authoring workflow

1. Pick a location in-game
2. Start bridge; walk around and record marker coordinates from snapshots / CET console
3. Run `ammchars` and note exact spawn names for each NPC role
4. Write encounter JSON with markers + AMM catalog names
5. Script 3–5 outcome beat plans by hand (before LLM)
6. Wire director to fill narration flavor only
7. Add LLM variation once puppet verbs work

Hand-authored beats de-risk the demo. LLM adds flavor later.

---

## Stream overlay (future)

Not required for Phase 5. When ready:
- Stats panel (HP, eddies) from Python state
- Vote timer + options from encounter phase
- Narration text box synced to `lines[]`

See [cypher-vision/archive/new-spec/new-spec-2.md](../cypher-vision/archive/new-spec/new-spec-2.md) for broadcast pacing notes.
