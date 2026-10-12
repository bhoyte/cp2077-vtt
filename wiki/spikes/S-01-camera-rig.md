---
type: spike
id: S-01
title: Camera rig — spawn, cut, blend, hide V, streaming radius
status: partial
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

Partial, 2026-10-11. Evidence: [raw/evidence/2026-10-11-s01-camera.md](../../raw/evidence/2026-10-11-s01-camera.md).

`exEntitySpawner.Spawn` is callable from ArcadeSpike (F-006). Run 1 flatlined on `GetVar("/interface", "hud")` (F-023) after a menu-puppet spawn. A first loaded-save attempt did not resolve entities within 2 s.

Run 2 (22:16, same save, mods reloaded) did. Three cameras resolved in about 1 s, ids `10031371ULL`–`10031373ULL`, each with a `camera` component. `Activate`/`Deactivate` returned ok for blend 0 (A, then B) and blend 1.5 (C). That is the API result only: no frame step, so a flash-free cut is not proven. Q-08: our own spawn was enough; AMM's Camera module was not driven.

The same run locked V (restriction effects + TPP head) and teleported to 5 / 30 / 80 / 150 m. The far hops dropped V about 14 m and the player flatlined. Despawn cleared the lock after the death. No RED4ext crash. Evidence: [run 2](../../raw/evidence/2026-10-11-s01-camera-run2.md).

Run 3 (22:33) spawned cameras, then a second mod reload wiped them before the cut. Evidence: [run 3](../../raw/evidence/2026-10-11-s01-camera-run3.md).

Run 4 (22:35, rooftop, one reload) kept the same Lua state. Three cameras, then blend 0 to A, blend 0 to B, blend 1.5 to C, all `ok=true`. Player coordinates did not change until despawn teleported back to the same subject point. Restrictions and the head swap were cleared. No frame capture, so a flash-free cut and the blend's source are still unseen. Evidence: [run 4](../../raw/evidence/2026-10-11-s01-camera-run4.md).

The player grabbed one roof frame after run 4 (`raw/evidence/2026-10-11-s01-roof-frame.jpg`): HUD still drawn, a full body in the right of frame. The timed cuts were too short to judge. Manual CET hotkeys now hold each camera until the next press: next (hard cut), blend (1.5 s), release (no teleport).

Prelim, 22:46–22:50, same roof. Hotkeys held each camera. The log shows hard cuts and 1.5 s blends all returning ok. Four frames (`raw/evidence/2026-10-11-s01-roof-prelim.md`) are four different angles: one includes V's full body, three do not. The HUD and a cyan crosshair stay in every frame. Detail on the roof stays full. Hiding V was not part of this pass.

Still open: whether a hard cut flashes the player camera, where the blend starts, hiding V and the HUD, streaming. Do not repeat an unguided far teleport.
