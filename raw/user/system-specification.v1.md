# System Specification: Autonomous "Arcade Cabinet" Virtual Production Engine for CP2077 TTRPG Broadcasts

## 1. Document Overview & System Purpose
This document provides the complete, updated architectural specification for an autonomous, live-streamed *Cyberpunk* TTRPG production engine. 

The system operates as an **interactive, headless "arcade cabinet"**:
* **Zero Streamer On-Screen Persona:** The broadcaster acts strictly as an off-camera arcade operator, system facilitator, and diegetic world voice (e.g., an in-universe Fixer over a holo-call).
* **Audience as the Party ("Chat Engagement 2.0"):** The live chat audience is partitioned into four distinct squad roles (Solo, Netrunner, Tech/Medtech, Fixer) who collectively debate, vote on, and execute all party actions.
* **Deterministic Visual Soundstage:** *Cyberpunk 2077* (REDengine 4) functions as the real-time physical diorama via discrete coordinate nodes, animation triggers, and virtual camera cuts.
* **Sub-150ms Intent Resolution:** TypeSafe AI’s System-1 discriminative model (`Jev`) maps role-specific chat consensus directly to validated engine macros with zero text-generation latency and zero parsing hallucinations.
* **Authentic TTRPG Rules Execution:** Initiative turns, $1\text{d}10 + \text{Stat} + \text{Skill}$ vs. Difficulty Value (DV) mechanics, armor ablation (Stopping Power), and high-stakes permadeath are resolved mechanically and surfaced on broadcast overlays.

---

## 2. Core Architectural Principles

1. **The Arcade Operator Paradigm:** Parasocial streamer-viewer interactions are eliminated. Audience engagement is redirected horizontally toward inter-chat collaboration, role rivalries, and collective stakes.
2. **Faction-Partitioned Action Space:** Chat viewers claim one of four character seats (`!solo`, `!netrunner`, `!tech`, `!fixer`). Voting windows strictly authenticate inputs against the character whose turn is active in the initiative order.
3. **Discrete Node-Graph Spatialization:** Night City encounters are modeled as pre-authored spatial graphs. Entities snap to tagged interaction points (cover, consoles, booths), bypassing volatile live AI pathfinding.
4. **Cinematic Jump-Cut Direction:** Continuous character locomotion between distant nodes is replaced by immediate camera cuts and shot-reverse-shots, masking entity repositioning and emulating television direction.
5. **Strictly Typed Decision Dispatching:** Large autoregressive LLMs (GPT-4, Claude) are banned from the real-time operational loop. All chat intent is resolved via discriminative System-1 classification (`Jev`) targeting fixed enum action spaces.
6. **Unyielding Tabletop Stakes (Permadeath):** Dice rolls and Death Saves are fully transparent and never fudged. A flatlined character triggers an in-engine ragdoll, an on-screen memorial sequence, and a roster reset.

---

## 3. High-Level System Architecture

```
+-----------------------------------------------------------------------------------------+
|                                    BROADCAST LAYER                                      |
|  OBS Studio: Headless CP2077 Visuals | Squad Turn HUD | 3D Dice Overlays | Memorial UI  |
+-----------------------------------------------------------------------------------------+
                                             ^
                                             | Raw Video Capture (No HUD)
+--------------------------------------------+--------------------------------------------+
|                          IN-ENGINE RUNTIME (CP2077 / REDengine)                         |
|  - Cyber Engine Tweaks (CET) Lua IPC Listener                                           |
|  - Appearance Menu Mod (AMM): Spawned Edgerunner Pawns & Scene Dressing                 |
|  - Programmatic Camera Controller: Tactical Iso, Over-the-Shoulder, Reaction Cuts       |
+-----------------------------------------------------------------------------------------+
                                             ^
                                             | Local IPC (`action_event.json` / WebSocket)
+--------------------------------------------+--------------------------------------------+
|                      MIDDLEWARE ORCHESTRATOR & RULES ENGINE                             |
|  - TTRPG State Machine: Initiative Queue, HP/SP Counters, Stat Checks, Death Saves      |
|  - Command Ingest: Twitch/YT Chat WebSocket, Squad Role Filters, Vote Timers            |
|  - Dice Simulator: 1d10 + Stat + Skill vs DV, Critical Injury Determinator              |
+-----------------------------------------------------------------------------------------+
                                             │
                                             v State Payload & Candidate Action Set
+-----------------------------------------------------------------------------------------+
|                    DECISION & ROUTING ENGINE (TypeSafe AI / Jev)                        |
|  - System-1 Discriminative Decision Loop (~70–150ms latency)                            |
|  - Evaluates: [Squad Chat Window + Current Node State] -> Typed Enum Action ID          |
+-----------------------------------------------------------------------------------------+
```

---

## 4. Subsystem Specifications

### Subsystem A: Chat Ingest & Squad Management
* **Role Partitioning:**
  * Viewers assign themselves to roles via commands or Channel Point redemptions: `!solo`, `!netrunner`, `!tech`, `!fixer`.
  * The middleware tracks viewer affiliation in an in-memory session cache.
* **Input Pooling:**
  * During an active turn, the orchestrator opens a **10–15 second voting window**.
  * Messages from non-active squads are ignored for action voting, but routed to a dedicated squad-comms overlay box.
  * Inputs can be discrete (e.g., `1`, `2`, `3`) or freeform natural language (e.g., *"suppress the boss from the left column"*).

### Subsystem B: Middleware Orchestrator & TTRPG Rules Engine
* **Runtime:** Node.js or Python local daemon.
* **Responsibilities:**
  * **Turn Sequencer:** Maintains the TTRPG Initiative order across active Edgerunners and opposing NPCs.
  * **Dice Evaluation:** Resolves checks deterministically using standard Cyberpunk rules:
    $$\text{Total} = 1\text{d}10 + \text{Stat} + \text{Skill}$$
    $$\text{Success Criteria} = \text{Total} \ge \text{DV}$$
  * **Damage & Armor Tracking:** Deducts weapon damage from armor Stopping Power (SP), applies remaining damage to HP, and rolls for critical injuries on double-6 damage rolls.
  * **Death Save Watcher:** Triggers $1\text{d}10 \le \text{Body}$ check when an Edgerunner hits 0 HP. If failed, transitions engine to `FLATLINED` state.
  * **Attribution Engine:** Tracks which chat users voted for the winning action and publishes their usernames to the broadcast overlay.

### Subsystem C: Decision & Intent Layer (TypeSafe AI / Jev)
* **Model Type:** Non-autoregressive System-1 decision model.
* **API Integration:**
  * Ingests aggregated chat buffer as `State`.
  * Evaluates against the active node's `valid_actions` array using the `Choice` primitive.
* **Output:** A calibrated, strictly typed action string (e.g., `action_solo_suppressive_fire`) delivered in $\le 150\text{ ms}$ with zero markdown formatting or syntax errors.

### Subsystem D: In-Engine Staging & Stunts (CP2077)
* **Core Mod Dependencies:**
  * **Cyber Engine Tweaks (CET):** Runs `init.lua`, exposing the engine loop to the middleware IPC.
  * **Appearance Menu Mod (AMM):** Places Edgerunner pawns, enemy gangs, weapons, and prop dressing.
  * **Otis_Inf IGCS Freecam or AMM Director Camera:** Moves and binds camera vectors programmatically.
  * **Complete HUD Remover:** Provides an uncluttered camera feed for stream output.
* **Execution Flow:**
  * CET listens on `onUpdate` for incoming payloads in `action_event.json`.
  * Instantly sets pawn coordinates, switches animation stances, updates decals/effects, and executes camera cuts.

### Subsystem E: Narrative Stinger & Memorial Pipeline
* **Tools:** MiniMax Hailuo, SeaDance, RunWay, or Sora.
* **Scope:**
  * **Narrative Bridges:** Pre-rendered 5–15 second clips for district travel, AV arrivals, corporate boardroom cuts, or deep Old Net runs.
  * **The Memorial Vault:** Pre-rendered noir vignettes used when an Edgerunner flatlines, memorializing the lost character before the chat creates a replacement.

---

## 5. Round Structure & Execution Sequence (The "Arcade Clock")

```
                 [ Initiative Queue: Solo Turn Begins ]
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │ PHASE 1: COMMAND WINDOW (10 - 15 Seconds)               │
       │ - CP2077 Camera: Tactical Overview                      │
       │ - OBS Overlay: "SOLO TURN: Action Options Displayed"    │
       │ - Ingest: Middleware pools active Solo chat votes       │
       └─────────────────────────────────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │ PHASE 2: CONSENSUS & INTENT ROUTING (~100 ms)           │
       │ - TypeSafe Jev evaluates chat buffer -> Valid Enum ID   │
       │ - Middleware validates action against active node       │
       └─────────────────────────────────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │ PHASE 3: MECHANICAL ROLL & MATH (2 - 4 Seconds)         │
       │ - Automated dice roller triggers in OBS                 │
       │ - Math resolves: Total vs. DV                           │
       │ - Overlay displays: HIT / MISS / CRITICAL / SP LOSS     │
       └─────────────────────────────────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │ PHASE 4: IN-ENGINE CINEMATIC CUT (3 - 5 Seconds)        │
       │ - Middleware dispatches `action_event.json` to CET      │
       │ - CET snaps actor transform & triggers firing animation │
       │ - Camera cuts to dramatic over-the-shoulder angle       │
       │ - Chat MVP attribution banner displays on stream        │
       └─────────────────────────────────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │ PHASE 5: WORLD / ENEMY REACTION (3 - 5 Seconds)         │
       │ - Opposing NPC script executes retaliation turn         │
       │ - Damage applied to Player SP / HP                      │
       │ - Turn passes to Netrunner -> Loop repeats              │
       └─────────────────────────────────────────────────────────┘
```

---

## 6. Data Schemas & Contracts

### 1. Scene Manifest (`scene_manifest.json`)
Defines the spatial geometry, node roles, valid actions, and camera angles for an encounter.

```json
{
  "scene_id": "totentanz_upper_balcony",
  "environment": {
    "world_anchor": [-1120.4, 1540.2, 42.1],
    "lighting_preset": "totentanz_strobe_red",
    "weather": "AcidRain"
  },
  "nodes": {
    "node_solo_railing": {
      "assigned_role": "Solo",
      "transform": { "x": -1120.4, "y": 1540.2, "z": 42.1, "yaw": 180.0 },
      "default_anim": "aim_rifle_crouch",
      "valid_actions": [
        "action_solo_headshot",
        "action_solo_suppressive_fire",
        "action_solo_fall_back"
      ]
    },
    "node_netrunner_terminal": {
      "assigned_role": "Netrunner",
      "transform": { "x": -1124.8, "y": 1543.1, "z": 42.1, "yaw": 90.0 },
      "default_anim": "typing_cyberdeck_intense",
      "valid_actions": [
        "action_netrunner_overheat",
        "action_netrunner_blackout",
        "action_netrunner_turret_hack"
      ]
    }
  },
  "camera_presets": {
    "cam_tactical_wide": {
      "position": [-1115.0, 1535.0, 48.0],
      "rotation": [-35.0, 25.0, 0.0],
      "fov": 70.0
    },
    "cam_solo_action": {
      "position": [-1121.2, 1538.8, 42.7],
      "rotation": [-5.0, 175.0, 0.0],
      "fov": 45.0
    },
    "cam_enemy_reaction": {
      "position": [-1120.0, 1546.0, 42.5],
      "rotation": [0.0, -10.0, 0.0],
      "fov": 35.0
    }
  }
}
```

### 2. Live Game State (`game_state.json`)
Maintained by the middleware orchestrator and synchronized with OBS overlays.

```json
{
  "session_id": "gig_049_maelstrom_heist",
  "phase": "COMMAND_WINDOW",
  "active_turn": {
    "role": "Solo",
    "character_name": "Valkyrie",
    "node_id": "node_solo_railing",
    "time_remaining_ms": 8200
  },
  "party_status": {
    "Solo": { "hp": 35, "max_hp": 45, "sp_body": 8, "sp_head": 11, "status": "ALIVE" },
    "Netrunner": { "hp": 28, "max_hp": 30, "sp_body": 4, "sp_head": 0, "status": "ALIVE" },
    "Tech": { "hp": 32, "max_hp": 35, "sp_body": 11, "sp_head": 11, "status": "ALIVE" },
    "Fixer": { "hp": 0, "max_hp": 25, "sp_body": 0, "sp_head": 0, "status": "FLATLINED" }
  },
  "opponents": [
    { "id": "boss_royce", "hp": 18, "max_hp": 60, "sp": 5, "status": "PINNED" }
  ]
}
```

### 3. Action Execution Payload (`action_event.json`)
Dispatched from Middleware to the CET Lua listener upon vote and dice resolution.

```json
{
  "event_id": "evt_99812401",
  "timestamp": 1728666015400,
  "role": "Solo",
  "action_id": "action_solo_headshot",
  "target_node": "node_solo_railing",
  "animation": "fire_rifle_recoil",
  "camera_cut": "cam_solo_action",
  "dice_outcome": {
    "roll": 9,
    "stat_plus_skill": 14,
    "total": 23,
    "dv": 17,
    "success": true,
    "critical_injury": "Lost Eye"
  },
  "squad_mvps": ["@KiroshiKing", "@ChromedOut", "@NetGhost"]
}
```

---

## 7. Edge Cases, Permadeath, & System Guardrails

| Condition | Cause | System Remediation |
| :--- | :--- | :--- |
| **Deadlock / Tie Vote** | Chat vote is split 50/50 when the command timer expires. | Middleware uses Jev’s calibrated probability score to select the highest-probability option; if exactly equal, triggers a 1-second "Tie-Breaker Coin Toss" overlay. |
| **Low Chat Velocity** | Late-night hours or low viewer concurrency results in zero votes. | Fallback timer auto-triggers the safest defensive node macro (`action_fall_back` / `action_take_cover`) to maintain broadcast momentum. |
| **Pawn Mesh Collapse** | CP2077 engine glitch causes an actor to sink into terrain or T-pose. | CET heartbeat script monitors pawn transform delta. If altitude anomalies occur, CET fires `AMM.Teleport()` back to the scene manifest's origin coordinates. |
| **Character Permadeath** | Player character fails a Death Save ($1\text{d}10 > \text{Body}$). | 1. CP2077 pawn triggers ragdoll state.<br>2. OBS flashes red `FLATLINED` full-screen banner.<br>3. Video player queues pre-rendered AI memorial stinger.<br>4. Middleware locks role until chat completes an expedited replacement lifepath poll. |
| **Downtime Loop Transition** | Combat ends and crew returns to base. | Orchestrator loads the "Arcade Lobby" manifest (e.g., El Coyote Cojo bar), switching from 15-second combat ticks to 60-second narrative spending polls (*Rent, Cyberware, Hustle Charts*). |

---

## 8. Implementation Checklist for Agents & Engineers

1. **Host Environment Setup:**
   * Install *Cyberpunk 2077* (v2.1+), Cyber Engine Tweaks (CET), and Appearance Menu Mod (AMM).
   * Install an IGCS/Freecam utility and verify custom camera binding hotkeys.
   * Toggle off all native HUD elements via CET debug settings.
2. **Scene & Graph Authoring:**
   * Build 3–5 core encounter soundstages in Night City (e.g., Afterlife booth, Totentanz balcony, Badlands fuel depot).
   * Record entity coordinate vectors via CET (`Game.GetPlayer():GetWorldPosition()`) and serialize into `scene_manifest.json`.
3. **Deploy CET Lua Event Bridge:**
   * Place `init.lua` inside `bin/x64/plugins/cyber_engine_tweaks/mods/arcade_vtt/`.
   * Ensure `init.lua` polls `action_event.json` each frame, handling entity snapping, animation playback, and camera cuts.
4. **Deploy Middleware Orchestrator:**
   * Build Node.js/Python server connecting Twitch/YouTube IRC to the local rules engine.
   * Integrate the TypeSafe AI / Jev API using the `Choice` primitive mapped to `valid_actions`.
   * Expose local WebSockets for the OBS browser overlay (displaying active squad, countdown timer, dice animations, and HP/SP status).
5. **Pre-Render Narrative Media:**
   * Generate 5–15 second video clips (district travel transitions, Net dives, trauma team arrivals, memorial plates) and configure them as OBS media stingers.