---
type: spike
id: S-01
title: Camera rig — spawn, cut, blend, hide V, streaming radius
status: planned
gate: G1
updated: 2026-10-11
depends_on: [F-006, F-007, F-008, F-009]
---

# S-01 — Camera rig

**Hypothesis.** Our mod can spawn N camera entities (`simple_free_camera.ent`, F-007), place them, and switch with
blend 0 (hard cut) or blend > 0 (move), with V hidden and parked within ~30 m without visible quality loss.

**Procedure** (scratch CET mod `ArcadeSpike`, commands over the existing bridge):
1. In-world, after session start, call `exEntitySpawner.Spawn("base\\entities\\cameras\\simple_free_camera.ent", transform, '')`, then poll `Game.FindEntityByID` every 0.1 s for ≤ 2 s (AMM's pattern, raw/amm/camera.lua). Log whether `exEntitySpawner` is nil **at onInit vs. inside a Cron callback after load**, which tests the timing explanation for F-006.
2. If it's nil in our context: `GetMod("AppearanceMenuMod")` and log the table's keys to find its Camera module; drive that instead (Q-08).
3. Spawn three cameras at hand-picked transforms. `component:SetFOV(f)`; orientation via `EulerAngles.new(...)` → `:ToQuat()` → `SetLocalOrientation` (check EulerAngles constructor argument order on NativeDB first).
4. Hard cut A→B: `A.component:Deactivate(0,false)` then `B.component:Activate(0,false)`. Record OBS at 60 fps and step frames for any FPP flash between them.
5. Blend B→C with 1.5 s. Does it interpolate from B or from the player camera?
6. Hide V: replicate AMM's `Util:AddPlayerEffects()` + `Tools:ToggleHead()` (source-read them first). Check for HUD elements, crosshair, or V's shadow in all shots.
7. Streaming: park V at 5 / 30 / 80 / 150 m from the subject; screenshot each (LOD, NPC presence, collision). Proves or refutes F-009.

**Pass.** Three presets, hard cut with zero intermediate frames, working blend, V invisible (incl. shadow), no HUD, no quality loss with V parked ≤ 30 m.

**Fallback.** (a) AMM's module; (b) the player's FPP camera with V invisible and noclip: teleporting V moves the camera. Cuts become teleports.

## Result
_(not run)_
