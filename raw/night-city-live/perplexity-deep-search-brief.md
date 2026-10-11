# Night City Live — Deep Search Brief for Perplexity

> **Purpose**: This document brings an AI research assistant up to speed on the Night City Live project, details every capability we have confirmed, identifies every gap, and asks targeted questions so Perplexity can find mods, APIs, techniques, or workarounds that close them.

---

## 1. What Night City Live Is

**Night City Live** is a live Twitch stream where an LLM acts as the Game Master of a homebrew TTRPG campaign. Cyberpunk 2077 is the rendering engine — it produces real-time machinima that the audience watches. Twitch chat votes to control the protagonist (V).

### The stack (already built and partially verified)

| Layer | Tech | Status |
|---|---|---|
| **Chat** | `twitchio` Python lib reads Twitch chat votes | Designed, not wired yet |
| **GM Server** | Python server — calls LLM, tracks state in SQLite + ChromaDB, emits structured JSON commands | Core loop designed |
| **TCP Bridge** | `RedSocket` mod — CP2077 connects out to the Python server on port 2077 | **Verified in-game** (Milestone 0) |
| **Game Engine** | Cyber Engine Tweaks (CET) + Appearance Menu Mod (AMM) execute Lua inside CP2077 | **Verified**: spawn, despawn, set appearance, list characters/appearances, multi-actor offset placement |

### The genre (needs a name)
Turn-based, VTT-style, machinima, livestream, viewer-participation, homebrew TTRPG campaign rendered in a AAA game engine. Think *Critical Role* meets *Red vs Blue* meets *Twitch Plays Pokémon* — in Night City.

---

## 2. Confirmed Capabilities (what we CAN do today or know how to wire)

### Already working through the bridge (Python → CET → AMM)
- Spawn any NPC by name or TweakDB record (`amm_spawn_npc`)
- Place multiple actors with forward/lateral meter offsets
- Set NPC appearance (`amm_set_appearance`, with optional delay)
- Despawn NPCs (`amm_despawn_npc`)
- List AMM characters and appearances
- Catalog validation (curated JSON allowlist prevents LLM typos)
- Full-text search over 4,363 entities via `entities_fts` in derived SQLite index

### Known AMM functions we can wire with one new CET handler each
| Capability | AMM function to call | Notes |
|---|---|---|
| **Weather** (16 presets) | `WeatherSystem:SetWeather(preset, transition)` | Rain, Fog, Sandstorm, Sunny, Toxic Rain, etc. |
| **Time of day** | `Tools:SetTime({hour, minute})` | Minute-level precision |
| **Freeze world** | `Tools:FreezeTime()` / `Tools:SetSlowMotionSpeed(factor)` | 0.000001x to 5x |
| **Teleport player** | `Tools:TeleportToLocation(loc)` | 121 built-in + user locations with tags |
| **Teleport any entity** | `Util:TeleportTo(handle, pos, rot)` | Instant; or `Util:TeleportNPCTo` via AI cmd |
| **AI walk/run/sprint to position** | `Util:MoveTo(puppet, pos, walkType, stealth)` | Walk, Run, Sprint; navmesh-dependent |
| **AI follow target** | `Util:FollowTarget(puppet, target, distance)` | Configurable distance |
| **AI hold position** | `Util:HoldPosition(puppet, duration)` | Seconds |
| **AI rotate to face** | `Util:RotateTo(puppet, pos)` | Face a world point |
| **Facial expression** | `Tools:ActivateFacialExpression(target, face)` | Dozens of presets with categories |
| **LookAt** | `Tools:ActivateLookAt()` | Head + chest tracking; target = V, NPC, prop, or camera; configurable stiffness |
| **Freeze NPC** | `Tools:FreezeNPC(handle, true/false)` | Time-dilation freeze, preserves pose |
| **Set hostile** | `Util:SetHostileRole(puppet)` | Full hostile + combat trigger vs player |
| **Trigger combat between NPCs** | `Util:TriggerCombatAgainst(handle, target)` | Mutual hostility |
| **Team combat** | `Director:SetHostileTowards(puppet, target, group)` | Team A vs Team B |
| **Set companion/follower** | `Util:ToggleCompanion(ent)` | Toggle follower role |
| **God mode** (any entity) | `Util:SetGodMode(entity, bool)` | |
| **Spawn vehicle** | `Spawn:SpawnVehicle(spawn)` | Separate path from SpawnNPC |
| **Mount NPC into vehicle seat** | `Scan:AssignSeats(entities)` via `AIMountCommand` | front_left/right, back_left/right |
| **Vehicle follow player** | `Scan:SetDriverVehicleToFollow(driver)` | `AIVehicleFollowCommand` |
| **Vehicle drive to map point** | `Scan:SetDriverVehicleToGoTo(driver, dest)` | `AIVehicleToNodeCommand`, arrival detection |
| **Vehicle doors/windows/engine** | `Util:ToggleDoors/Windows/Engine` | Per-door granularity |
| **Play voice line** | `Util:PlayVoiceOver(handle, vo)` | Pre-recorded game VO barks |
| **Play pose/animation** | `Poses:PlayAnimationOnTarget(target, anim)` | From favorited workspot anims |
| **Scale entity** | `Tools:SetScale(components, values)` | Per-axis X/Y/Z |
| **Spawn prop** | `Props:SpawnProp(spawn, pos, angles)` | Thousands of DB items |
| **Spawn/activate free camera** | `Camera:Spawn() / Camera:Activate()` | 6-DOF, FOV, zoom, roll, lock |
| **Equip weapon on NPC** | `Util:EquipGivenWeapon(puppet, weapon)` | |
| **Cyberpsycho mode** | `Tools:SetCyberpsycho(entity, targets)` | NPC attacks random nearby targets with VFX |
| **Player invisibility** | `Tools:ToggleInvisibility()` | V invisible to all NPCs |

### AMM Director (built-in machinima sequencer)
- Waypoint-based choreography: actors walk through nodes with per-node appearance, expression, pose, VO, LookAt, attack
- Sequential / Random / OnlyOne sequence modes per actor
- All actors run simultaneously on independent 0.1s tick timers
- Scripts save/load as JSON in `User/Scripts/`
- Triggers auto-fire when player enters a radius
- **Key limitation**: cameras are manual only (no keyframes, no scripted cuts)

---

## 3. Known External Mods That Fill Gaps

### Otis_Inf / IGCS Camera Tools
- **What**: external camera tool (not CET-based) with keyframed camera paths
- **Key feature**: catmull-rom spline interpolation, multiple paths switchable via hotkeys, per-node FoV/ToD/fog interpolation, ease-in/out, camera shake, constant speed mode, path playback tied to player location
- **Status**: v1.0.45 (July 2025), CP2077 v2.2+ compatible, Patreon-supported
- **Docs**: https://opm.fransbouma.com/camerapaths.htm
- **Integration**: runs alongside (not through the bridge); operator flies camera manually or plays back paths
- **Gap filled**: camera paths and cinematic camera work

### Audioware
- **What**: custom audio playback mod for CP2077
- **Key feature**: play .wav/.ogg/.mp3/.flac in-game with localized subtitles, spatial panning, reverb, EQ; integrates with vanilla AudioSystem
- **Status**: v1.9.2 (April 4, 2026), CP2077 2.31 compatible
- **GitHub**: https://github.com/cyb3rpsych0s1s/audioware
- **Requires**: Codeware, TweakXL, RED4ext, redscript
- **Gap filled**: custom voice lines (LLM narration → ElevenLabs TTS → .wav → Audioware)

### CyberScript
- **What**: JSON-driven scripting framework for custom quests, dialogues, events
- **Key feature**: custom dialogue trees with player choices, phone conversations, quest objectives, NPC interactions with poses, custom fixers/factions
- **Status**: v5.1.4 (May 2025), requires CET + Codeware + Audioware + Native Settings UI
- **Nexus**: https://www.nexusmods.com/cyberpunk2077/mods/6475
- **Gap filled**: dialogue, quest structure, branching narrative, NPC conversation

---

## 4. The Gaps — What We CANNOT Do Yet

### Hard engine limits (no known mod solution)
| Gap | Why it matters | Known workaround |
|---|---|---|
| **Custom lip sync** | NPCs don't mouth custom audio; only pre-recorded game VO has lip sync | Frame shots to avoid mouth close-ups during custom audio; use VO barks for dialogue, narration for custom text |
| **Custom animation creation** | Can't create new animations; limited to game's existing workspot/pose library | Large existing library (43,765 workspots in DB); community pose packs expand it |
| **Ragdoll/physics control** | Death/knockback animations are engine-driven | Use `FakeDeathSignal` + freeze for controlled "death" poses |
| **NPC interior pathfinding** | AI navmesh is unreliable inside buildings | Teleport NPCs to positions inside interiors instead of walk commands |
| **Persistent spawned entities** | All spawns vanish on save/load | Re-spawn on session start from saved state |

### Gaps where a mod MIGHT exist (SEARCH NEEDED)
| Gap | What would solve it | Search query suggestion |
|---|---|---|
| **Automated camera cuts/switching** | A mod or CET script that can switch between cameras on a timer or trigger, or that can be controlled via TCP/IPC | `Cyberpunk 2077 CET camera switching automated cuts cinematic mod 2025 2026` |
| **Subtitle/text overlay in-game** | Display custom text on screen (not just Audioware subtitles) — for narrator text, vote prompts, character dialogue | `Cyberpunk 2077 custom HUD text overlay subtitle mod CET ImGui 2025 2026` |
| **NPC conversation animations** | Make NPCs play talking/gesturing animations during dialogue (not just idle poses) | `Cyberpunk 2077 NPC talking animation gesture conversation mod workspot 2025 2026` |
| **Crowd/ambient NPC control** | Spawn or control background crowd density, types, behavior for atmosphere | `Cyberpunk 2077 crowd density control NPC population mod 2025 2026` |
| **Radio/music control** | Play specific radio stations or custom music in-game, controllable via script | `Cyberpunk 2077 radio station control custom music playback mod CET 2025 2026` |
| **Screen effects / post-processing** | Trigger visual effects (screen shake, color grading, vignette, glitch) for dramatic moments | `Cyberpunk 2077 screen effect post processing visual filter mod CET 2025 2026` |
| **NPC scheduling / patrol routes** | Give NPCs persistent patrol behavior (walk between points on a loop) without using Director's manual system | `Cyberpunk 2077 NPC patrol route schedule behavior mod 2025 2026` |
| **Save/restore full scene state** | Snapshot all spawned entities + positions + appearances + weather and restore on command | `Cyberpunk 2077 scene state save restore snapshot mod preset 2025 2026` |
| **OBS integration / scene switching** | Trigger OBS scene changes from the bridge (e.g., cut to title card, switch camera overlay) | `OBS WebSocket API Python scene switching overlay control 2025 2026` |
| **Twitch chat overlay in-game** | Show Twitch chat or vote UI inside CP2077 | `Cyberpunk 2077 Twitch chat overlay mod CET ImGui stream 2025 2026` |
| **LLM-generated CyberScript JSON** | Can an LLM dynamically write CyberScript quest/dialogue JSON and hot-reload it? | `CyberScript hot reload JSON runtime quest creation dynamic 2025 2026` |
| **Otis_Inf programmatic control** | Can IGCS camera paths be triggered or switched from an external script/TCP? | `Otis_Inf IGCS API external control camera path trigger programmatic 2025 2026` |

---

## 5. The Architecture We're Building Toward

```
Twitch Chat (votes)
       ↓
Python GM Server (LLM + game state + ChromaDB memory)
       ↓ structured JSON commands
TCP Bridge (RedSocket)
       ↓
CET mod handler (CypherAgent/init.lua)
       ↓ dispatches to:
  ├── AMM (spawn, appearance, movement, combat, weather, props, poses)
  ├── Audioware (custom voice/narration playback)
  ├── CyberScript (dialogue trees, quest events) [if hot-reload works]
  └── Direct CET/game API (teleport, time, effects)

Camera: Otis_Inf IGCS (manual or keyframed, runs alongside)
Stream: OBS captures game + overlays + audio
```

### What the LLM outputs (target command vocabulary)

The LLM Game Master would return JSON like:

```json
{
  "narration": "The neon-soaked alley falls silent as four Maelstrom gangers step out of a battered van...",
  "commands": [
    {"action": "set_weather", "preset": "rainy_night"},
    {"action": "set_time", "hour": 23, "minute": 30},
    {"action": "spawn_vehicle", "logical_id": "van_1", "record": "Vehicle.v_standard25_mahir_supron_فurgon", "forward_m": 8},
    {"action": "spawn_npc", "logical_id": "mael_1", "record": "Character.gang_maelstrom_ranged2_m_hard", "forward_m": 6, "right_m": -2},
    {"action": "spawn_npc", "logical_id": "mael_2", "record": "Character.gang_maelstrom_melee_m_hard", "forward_m": 6, "right_m": 2},
    {"action": "set_appearance", "logical_id": "mael_1", "appearance": "maelstrom_yourface_01"},
    {"action": "set_hostile", "logical_id": "mael_1", "target": "player"},
    {"action": "set_expression", "logical_id": "mael_1", "expression": "aggressive"},
    {"action": "play_vo", "logical_id": "mael_1", "vo": "fear_toll"},
    {"action": "play_narration", "audio_file": "scene_12_narration.wav"}
  ],
  "vote_prompt": {
    "text": "What does V do?",
    "options": ["1: Draw weapon", "2: Talk your way out", "3: Run"]
  }
}
```

---

## 6. What We Need From This Deep Search

### Priority 1: Real-time cinematic control
1. Is there ANY way to programmatically trigger Otis_Inf camera path playback or switching from an external process? (CLI, named pipe, shared memory, hotkey simulation?)
2. Are there other CP2077 camera mods that support scripted/automated camera movement?
3. Is there a CET-based camera path system that we could control through the bridge?

### Priority 2: In-game text and UI
4. What mods exist for displaying custom text/UI overlays in CP2077? (for narration, vote prompts, dialogue)
5. Can CET ImGui windows be used as a transparent overlay during gameplay (not just in mod menus)?
6. Are there mods that show Twitch chat or external text in CP2077?

### Priority 3: Audio pipeline
7. Can Audioware audio be triggered from CET Lua at runtime (not just via YAML manifest pre-registration)?
8. Is there a way to dynamically register new audio files with Audioware without restarting the game?
9. What is the latency from "file exists on disk" to "playing in game" with Audioware?

### Priority 4: Dialogue and narrative
10. Can CyberScript quests/dialogues be hot-reloaded at runtime, or do they require game restart?
11. Is there a simpler alternative to CyberScript for just showing dialogue UI + choices without the full quest system?
12. Are there mods that provide a visual novel / dialogue box overlay for CP2077?

### Priority 5: Ecosystem and integration
13. What CP2077 mods exist for controlling crowd density or ambient NPC behavior?
14. Are there mods for triggering screen effects (glitch, flash, shake, color grade) from CET?
15. What is the current state of OBS WebSocket integration for Python? Can we switch scenes, trigger overlays, and control recording from the bridge?
16. Are there any existing projects attempting LLM-driven or AI-directed machinima in any game engine? What approaches did they take?

### Priority 6: Hard limits — are they really hard?
17. Is there ANY mod or technique for approximate lip sync in CP2077? (Even something that opens/closes the mouth on a timer?)
18. Can facial expressions be rapidly cycled to simulate talking?
19. Are there animation replacement mods that could map custom animations to existing workspot slots?

---

## 7. Game Version and Mod Stack (for compatibility filtering)

- **Cyberpunk 2077**: v2.31 (latest as of April 2026)
- **CET**: v1.37.1+
- **RED4ext**: v1.29.0+
- **redscript**: 0.5.27+
- **Codeware**: v1.19.0
- **AMM**: v2.12.5
- **ArchiveXL**: v1.26.3
- **RedSocket**: v0.5.0

Any mods found should be compatible with this stack or have been updated within the last 12 months.

---

## 8. Success Criteria

The "cinematic engine" is successful if it can:

1. **Stage a scene** in < 5 seconds from LLM output (spawn actors, set weather/time, position everyone)
2. **Run dialogue** with visible text and audible voice (custom or game VO)
3. **Choreograph movement** (NPCs walk to marks, look at each other, emote)
4. **Trigger combat** that looks intentional, not random
5. **Cut cameras** between angles (even if manual via IGCS hotkeys initially)
6. **Show votes** to viewers and apply results within one "turn"
7. **Narrate** with AI-generated voice over the scene
8. **Loop** this for 2-4 hour streams without crashes or state corruption

If mods exist that get us closer to ANY of these, we want to know about them.
