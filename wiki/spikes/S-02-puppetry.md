---
type: spike
id: S-02
title: Puppetry — 6 actors at nodes, poses, freeze, expressions, weapons, no AI interference
status: partial
gate: G1
updated: 2026-10-13
depends_on: [F-004, F-005, F-008, F-012, F-013, F-025, F-026]
---

# S-02 — Puppetry

**Hypothesis.** We can hold six spawned actors (four party, two enemies, at least one gang record via F-005) at authored
nodes in authored poses for 10+ minutes, and change pose on command, without game AI moving them.

**Pre-work (no game).** Done 2026-10-12. Source-read AMM 2.12.5 (`Modules/anims.lua`, `tools.lua`, `util.lua`, plus the callers in `init.lua`). Evidence: [2026-10-12-s02-amm-source.md](../../raw/evidence/2026-10-12-s02-amm-source.md). Facts: F-013, F-025, F-026. The in-game procedure below has not run.

**Procedure.** Spawn and teleport stay on F-004 / F-008. Puppetry calls, from the source-read:

1. Spawn 6 actors (F-004 path, `try_direct_record` for the gang record). Measure command → visible latency.
2. Teleport each to a node with yaw (F-008 `Game.GetTeleportationFacility():Teleport`). Repeat 20×; note snaps, falls, or floating.
3. Pose, then freeze. `t` is an AMM target with `.handle` and `.hash`. `anim` is `{name, ent, comp, rig}` from a `workspots` row (`ent` is always `base\amm_workspots\entity\workspot_anim.ent`, `comp` is `amm_workspot_base` for the candidates below).
   - `AMM.Poses:PlayAnimationOnTarget(t, anim, true)`
   - `AMM.Tools:FreezeNPC(t.handle, true)` then `AMM.Tools:FreezeNPC(t.handle, false)`
   - Pass no `caller`, so the anim stays in `Poses.activeAnims` and unfreeze replays it.
4. Expression, look-at, weapon.
   - `AMM.Tools:ActivateFacialExpression(t, face)` with `face` from `AMM:GetPersonalityOptions()` (`category` + `idle`; see evidence). Needs `ReactionManager` and `AnimationControllerComponent` on `t.handle`.
   - Look-at: set `AMM.Tools.currentTarget = t`, `AMM.Tools.lookAtTarget` to another target or nil (nil looks at V), `AMM.Tools.selectedLookAt = AMM.Tools.lookAtOptions[1]` (name `"All"`), then `AMM.Tools:ActivateLookAt()`. That calls `Util:NPCLookAt`.
   - Weapon: `Util:GetPlayerWeapon()`, then `Util:EquipGivenWeapon(t.handle, weapon:GetItemID().tdbid, nil)`, then `Util:EquipPrimaryWeaponCommand(t.handle)`. `Util` is not `AMM.Util` (nil). Confirm the bare `Util` global is visible from CypherAgent before this step; `pcall` it.
5. Neutralize AI. `AMM.Tools:SetNPCAttitude(t, EAIAttitude.AIA_Friendly)` (F-026; optional target/group). `Util:SetGodMode(t.handle, true)` (same `Util` visibility check). Do not call `Util:TriggerCombatAgainst` on this set; it forces `AIA_Hostile` and `TriggerCombat`. Confirm no wandering, fleeing, combat, or reactions to each other or to V; confirm passers-by and NCPD ignore the set.
6. Leave it running for 10 minutes and watch for drift, T-poses, despawns.

`AMM.Tools:ToggleInvisibility()` only calls `Game.GetPlayer():SetInvisible`. Do not use it on actors.

Weather and time are not part of this procedure. If a later beat needs them: `AMM.Tools:SetTime(minutes)` and `AMM.Tools.weatherSystem:SetWeather(cname, 10.0, 5)` (F-025). There is no `SetWeather` on Tools or Util.

**Candidate poses** (table `workspots`, `anim_comp = amm_workspot_base`). Pick the rig that matches the spawned body. `photomode_poses` has no aim, typing, kneel, dead, or bar rows.

| Role | anim_name | rigs |
|---|---|---|
| aim | `aim_loop` | Big, Man Average, Woman Average |
| aim | `stand__rh_gun_aim__01` | Man Average, Player Man, Woman Average |
| aim | `tpp_aim_loop` | Player Man, Player Woman |
| crouch-aim | `action___crouch_and_shoot` | Man Average, Woman Average |
| crouch (no aim) | `action_crouch` | Man Average, Woman Average |
| typing | `sit_chair_table_keyboard__2h_on_keyboard__01` | Big, Man Average, Player Man, Player Woman, Woman Average |
| typing | `sit_chair_table_lean0__2h_on_keyboard__01__typing__01` | Big, Man Average, Woman Average |
| hands-up | `stand_cheer__2h_up__01__gesture_handsup__01` | Man Average, Woman Average |
| hands-up | `stand__2h_hands_up__01` | Woman Average only |
| hands-up | `stand__2h_up__surrender__01` | Big only |
| kneel | `kneel__rk_on_ground__01` | Big, Fat, Man Average, Woman Average |
| kneel-injured | `takemura__kneel__rh_hold_arm__wounded__01` | Man Average only |
| kneel-injured | `songbird__kneel__rh_on_pipe__01__pain__01` | Woman Average only |
| lying-dead | `lie_ground_0__dead__01` | Big, Man Average, Woman Average |
| lying-dead | `lie_ground_180__dead__01` | Big, Man Average, Woman Average |
| talk-gesture | `stand__2h_on_hip__01__talk__neutral__01` | Big, Fat, Man Average, Woman Average |
| talk-gesture | `stand__2h_on_sides__01__gesture_hold__01` | Big, Man Average, Woman Average |
| lean | `idle_leaning_01` | Man Average, Woman Average |
| lean | `stand_lean0__2h_elbow_on_counter__01` | Man Average, Woman Average |
| sit-bar | `sit_barstool_bar_lean0__2h_on_bar__01` | Big, Man Average, Player Man, Player Woman, Woman Average |

No shared-rig kneel-injured name exists. The two kneel-injured clips are character names that still live on Man Average / Woman Average.

**Pass.** Six actors stable for 10 min; ≥ 12 usable poses catalogued with tags; spawn latency p95 < 3 s; weapon visible in at least aim poses.

**Fallback.** Fewer pose types plus heavier camera/FX work ("diorama mode", R-01).

## Result

First slice only (2026-10-12), on the ripperdoc roof. Not the six-actor, 10-minute procedure.

Johnny Silverhand, Hanako, and Song So Ri spawned through `AMM.Spawn`, took `stand__2h_on_hip__01__talk__neutral__01`, were set friendly, and froze. Each call returned ok. V's position stayed `-1538.17, 1197.07, 57.00`. They were despawned after the frames.

The first-person frame is three bodies in one volume, not one actor with the others out of shot. In [2026-10-12-s02-frozen.png](../../raw/evidence/2026-10-12-s02-frozen.png) a gold hand passes through a pale tattooed palm, and a chrome forearm passes through a skin forearm. Crops: [hands](../../raw/evidence/2026-10-12-s02-frozen-hands.png), [arm](../../raw/evidence/2026-10-12-s02-frozen-arm.png). Two side cameras also missed (off the roof, then inside the wall).

Separation pass (20:19, same roof, cast left in place). `Teleport` returned ok, then `GetWorldPosition` was polled for ~2.4 s with retries. All three stayed at `-1537.50, 1196.47, 57.00` (AMM's shared 1 m spawn). Pose and freeze ran there. [2026-10-12-s02-separated-b.png](../../raw/evidence/2026-10-12-s02-separated-b.png) shows a second face through Johnny's face and a gold hand through his hand. The same-tick theory does not explain this pass: the facility call never moved the puppets. Weapons, expressions, look-at, and the 10-minute soak have not run.

NPC-command pass (21:54). `Tools:TeleportNPCTo` put each puppet on a different mark (distance 0.00, held through freeze). [2026-10-12-s02-aitp.png](../../raw/evidence/2026-10-12-s02-aitp.png) shows three separate bodies in front of V. A 5 m sweep had cleared 15 leftovers at the old stack point. Weapons, expressions, look-at, and the 10-minute soak have not run.

Named place (2026-10-13 09:59), through the session rather than the probe. One command named Johnny Silverhand, Hanako, and Song So Ri. The reply put them about 1.6 m apart. [2026-10-13-place-names.png](../../raw/evidence/2026-10-13-place-names.png) shows three separate bodies, Hanako centered. They were not posed or frozen. Weapons, expressions, look-at, and the 10-minute soak have not run.

Evidence: [2026-10-12-s02-roof-cast.md](../../raw/evidence/2026-10-12-s02-roof-cast.md), [2026-10-12-s02-separate.md](../../raw/evidence/2026-10-12-s02-separate.md), [2026-10-12-s02-aitp.md](../../raw/evidence/2026-10-12-s02-aitp.md), [2026-10-13-place-names.md](../../raw/evidence/2026-10-13-place-names.md).
