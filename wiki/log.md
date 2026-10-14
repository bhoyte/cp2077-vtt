# Log

Append-only. Format: `## [YYYY-MM-DD] op | title`. Newest at the bottom. `rg "^## \[" wiki/log.md` lists entries.

## [2026-10-11] ingest | User vision docs, prior project, vendor docs, host audit
- raw: moved the user's two docs into `raw/user/` (v1, immutable); snapshotted 11 night-city-live docs, AMM `camera.lua`, Karpathy gist, Jev docs, compat matrix; wrote the host audit.
- Created sources: src-user-vision, src-night-city-live, src-karpathy-wiki, src-vendor-and-host.
- Registers: facts F-001…F-018, risks R-01…R-14, questions Q-01…Q-09.
- Contradictions recorded: F-006 vs F-007 (exEntitySpawner availability); seat "Fixer" vs streamer "Fixer"; 4-phase vs 5-phase clock.

## [2026-10-11] decide | Initial architecture and plan
- ADR-001…ADR-011 accepted.
- Design pages: show-clock, squads-and-voting, ruleset v0, permadeath, campaign. Components: contracts, orchestrator, stage, intent, broadcast, ledger.
- Plan: roadmap (two tracks, gates G1–G4), phase-0-reboot. Spikes S-01…S-07 planned.

## [2026-10-11] lint | First lint pass
- `python tools/wiki.py lint` clean; status dashboard verified.

## [2026-10-11] decide | User answers Q-01, Q-02, Q-03
- Twitch only; no paid effects on rules or dice (cosmetic only in Season 0); Steam unless GOG is proven necessary. Added F-019 (launching the exe directly avoids Steam updates, hypothesis).

## [2026-10-11] build | B1 rules core, provable dice, balance simulator
- Code: `arcade/dice`, `arcade/rules`, `arcade/sim`, `content/rules/season0.toml`; 21 tests (unit, replay equality, hypothesis termination property).
- Four tuning passes recorded in [ruleset](design/ruleset.md#tuning-history-v0-pass-2026-10-11). New mechanics: Heat, Hold; Taunt and Short circuit reworked.
- Result (4,000 gigs): 5.58 rounds/encounter, 27.6 % death/gig, 0.2 % wipe, 1.0 % stalemate. Seat leverage uneven → Q-10.

## [2026-10-11] ingest | CP2077 installed on C: SSD
- Evidence: raw/env/host-audit-2026-10-11-c-install.md. Path `C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077`, exe 2.31, 91 GB, Phantom Liberty depot + `archive\pc\ep1`.
- Mod layer survived in-place. Community redscript still missing (F-017). C: 51 GB free; D: is a Toshiba USB HDD (F-020, F-021).
- Q-04 answered yes. ADR-012 supersedes ADR-011. Phase 0 rewritten: no move to D:; remaining work is pin + redscript + smoke + freeze to `D:\cp2077-stack\`.

## [2026-10-11] ingest | Restored redscript v0.5.31
- Downloaded official zip to `D:\cp2077-stack\redscript-v0.5.31-windows.zip`; extracted into the C: game root.
- Added `engine\tools\scc.exe`, `scc_lib.dll`, `engine\config\base\scripts.ini`, `r6\config\cybercmd\scc.toml`. Evidence: raw/env/redscript-restore-2026-10-11.md. F-017 updated.

## [2026-10-11] spike-report | Phase 0 smoke: Johnny spawn on 2.31
- Bridge connected after CypherAgent reload (no auto-reconnect). `ammchars` 19; `spawn complete logical_id=npc_test`.
- Evidence: raw/evidence/2026-10-11-phase0-smoke.md. Re-verified F-001, F-004; F-002 note updated.

## [2026-10-11] ingest | OBS 32.2.2 present; Steam already pinned
- OBS exe `C:\Program Files\obs-studio\bin\64bit\obs64.exe` FileVersion 32.2.2 (F-022). Steam `AutoUpdateBehavior` is 1. Freeze + F-019 still need the game closed.

## [2026-10-11] spike-report | Phase 0 freeze + F-019 exe launch
- Zip `D:\cp2077-stack\stack-2.31-20261011.zip`; full copy `D:\cp2077-stack\game-2.31\` (5141 files, 85 GB). Evidence: raw/evidence/2026-10-11-stack-freeze.md.
- F-019: exe start verified (pid 12320, RED4ext 1.30.0 on 2.31). Pending-update skip still untested. Phase 0 marked done.

## [2026-10-11] spike-report | S-01 camera rig, partial
- ArcadeSpike + `tools/s01_probe.py`. Menu: three cameras spawned, then crash on `/interface` `hud` (F-023).
- Loaded save: Spawn callable, entities unresolved in 2 s; cuts failed; restrictions, TPP head, and park 5/30/80/150 returned ok.
- Evidence: raw/evidence/2026-10-11-s01-camera.md. F-006 rewritten. S-01 status partial.

## [2026-10-11] spike-report | S-01 run 2: cameras cut, far park killed V
- Loaded save: three `simple_free_camera.ent` resolved, cut blend 0 and 1.5 returned ok. Q-08 answered: own spawn is enough.
- Park 80/150 dropped V (z 57 → 43) and the player flatlined. No RED4ext crash. Probe no longer auto-parks past 30 m.
- Evidence: raw/evidence/2026-10-11-s01-camera-run2.md. F-006 updated.

## [2026-10-11] spike-report | S-01 run 3: second reload wiped the cameras
- Rooftop, no teleport. Three cameras spawned, then ArcadeSpike loaded again and the cuts ran against an empty rig.
- Despawn cleared the lock. Player position unchanged. Probe now aborts if the connection changes mid-sequence.
- Evidence: raw/evidence/2026-10-11-s01-camera-run3.md.

## [2026-10-11] spike-report | S-01 run 4: roof cuts returned ok
- One reload. Blend 0 to cam_a, blend 0 to cam_b, blend 1.5 to cam_c, all ok. Player unmoved. Despawn cleared the lock.
- No frame capture, so the picture is still unconfirmed. Evidence: raw/evidence/2026-10-11-s01-camera-run4.md.

## [2026-10-11] decide | S-01 camera switches are manual hotkeys
- Timed cuts were too short to judge. One roof frame shows the HUD and a body still in view.
- ArcadeSpike hotkeys: next (hard cut), blend 1.5 s, release with no teleport. Each camera stays until the next press.

## [2026-10-11] spike-report | S-01 roof camera prelim
- Hotkeys cut and blended on the roof. Four frames are four held angles. HUD and crosshair stay. V is in frame when she stands in the shot.
- F-024 verified. Evidence: raw/evidence/2026-10-11-s01-roof-prelim.md.

## [2026-10-12] spike-report | S-02 puppetry pre-work, no game
- Source-read AMM 2.12.5. F-013 is source-read. Added F-025 (weather) and F-026 (`SetNPCAttitude`).
- `SetWeather` is missing. No shared kneel-injured workspot. S-02 stays planned.
- Evidence: raw/evidence/2026-10-12-s02-amm-source.md.

## [2026-10-12] build | B2 show-loop first slice, no game
- Clock (grace, early lock, pipelining), L0 parser, fake Jev, vote book, ChatSim.
- Tests: `python -m pytest tests/test_show.py tests/test_intent.py` — 22 passed.
- Assumptions on the show-clock page: quorum N = 3; party beat 4 s; enemy beat 3 s. No Twitch adapter, no ledger, no live Jev.

## [2026-10-12] spike-report | S-02 roof cast, three actors
- Johnny, Hanako, and Song So Ri spawned, posed, set friendly, and frozen on the roof. V stayed at -1538.17, 1197.07, 57.00.
- First person shows Johnny in a gesture. Two side cameras missed the group. Cast was despawned.
- F-027. S-02 status partial. Evidence: raw/evidence/2026-10-12-s02-roof-cast.md.

## [2026-10-12] spike-report | S-02 frozen frame is three stacked bodies
- Closer look at raw/evidence/2026-10-12-s02-frozen.png: a gold hand through a tattooed palm, a chrome forearm through a skin forearm.
- Crops: raw/evidence/2026-10-12-s02-frozen-hands.png, raw/evidence/2026-10-12-s02-frozen-arm.png.
- F-027 note corrected. Next session separates them before the workspot samples position.

## [2026-10-12] handoff | session closed
- now.md is the resume point. Three actors stack because the workspot samples position on the teleport tick.
- Pushed to https://github.com/bhoyte/cp2077-vtt.

## [2026-10-12] ingest | Cursor chat archive
- raw/chats/2026-10-11_2026-10-12-s01-s02/: parent jsonl, two subagent threads, compaction, session.md digest.
- AGENTS.md close-session now requires chat archival. Resume: read session.md after now.md.

## [2026-10-12] spike-report | S-02 teleport did not separate the cast
- `Teleport` ok, position unchanged for 2.4 s. All three stayed at the shared 1 m spawn. Cast left in place.
- Frames: raw/evidence/2026-10-12-s02-separated.png, separated-b.png. Evidence: raw/evidence/2026-10-12-s02-separate.md.
- F-008 note, F-027 note, S-02 result, now.md.

## [2026-10-12] spike-report | S-02 NPC teleport separated the cast
- `Tools:TeleportNPCTo` put Johnny, Hanako, and Song So Ri on three marks. Freeze kept the coordinates. V unmoved. Cast left in place.
- Frames: raw/evidence/2026-10-12-s02-aitp.png. Evidence: raw/evidence/2026-10-12-s02-aitp.md. F-028 verified.

## [2026-10-12] decide | operated table, session is the first tool
- ADR-013. Overview, ADR-002, contracts `table.v0`, glossary, S-04 note, index.
- ArcadeLink redials and answers status. tools/booth.py holds port 2077. CypherAgent no longer dials.
- Roof cast not touched. One CET reload still required to load the mod.

## [2026-10-13] spike-report | session redials without a CET reload
- ArcadeLink 0.1.2. Booth killed. `link down quiet=3.4` then hello 8 s later. No reload between them.
- `status` returned V at -1536.78, 1195.77, 57.00. Actors empty. Roof cast not commanded.
- F-029 verified. F-002 note updated. Evidence: raw/evidence/2026-10-13-session-redial.md.

## [2026-10-13] handoff | session closed
- now.md is the resume point. Next table command is `place` via TeleportNPCTo. Do not teleport V. Do not reload to send a command.
- Chat archive: raw/chats/2026-10-12_2026-10-13-bridge/.

## [2026-10-13] ingest | Cursor chat archive
- raw/chats/2026-10-12_2026-10-13-bridge/: parent jsonl, session.md digest. No subagent threads.
- Resume: read session.md after now.md.

## [2026-10-13] decide | place spawns the three again
- The cast is disposable. `place` removes people within 5 m, spawns Johnny, Hanako, and Song So Ri in front of V, and replies with measured positions. It does not move V.
- ArcadeLink 0.1.3. tools/booth.py place. Contract table.v0, ADR-013, overview, glossary, now.md.
- The running game still needs one mod reload before this command exists.

## [2026-10-13] decide | place takes character names
- One name places that person. Several names place that line, in order. People not named stay. A person already spawned is moved, not copied.
- ArcadeLink 0.1.4. Ambiguous names return up to five list spellings. Contract table.v0, ADR-013, overview, glossary, now.md.
- Supersedes the fixed trio in the entry above. The running game still needs one mod reload.

## [2026-10-13] spike-report | named place, three in a line
- Mods reloaded. ArcadeLink 0.1.4 hello, then place Johnny Silverhand, Hanako, Song So Ri.
- Each move returned ok. Neighbors about 1.6 m apart, same height as V. V stayed at -1536.78, 1195.77, 57.00.
- User frame shows three separate bodies. F-030 verified. Evidence: raw/evidence/2026-10-13-place-names.md.

## [2026-10-13] handoff | session closed
- now.md is the resume point. Spawning is the next exploration. The lineup on the roof is disposable.
- Chat archive: raw/chats/2026-10-13-named-place/.

## [2026-10-13] ingest | Cursor chat archive
- raw/chats/2026-10-13-named-place/: parent jsonl, session.md digest. No subagent threads.
- Resume: read session.md after now.md.

## [2026-10-13] decide | place uses single file
- ArcadeLink 0.1.5. Several names stand one behind the other, about 1.6 m apart, along the direction V is facing. The first name is closest.
- Contract table.v0, ADR-013, F-030 note. The 0.1.4 side-by-side result stays the verified observation. The running game needs one mod reload.

## [2026-10-13] spike-report | named place, single file
- Mods already on 0.1.5. Listener started, hello, then place Johnny Silverhand, Hanako, Song So Ri.
- Johnny about 2.70 m along V's facing. Neighbors about 1.60 m further on that line. V stayed at -1536.57, 1194.66, 57.08.
- Evidence: raw/evidence/2026-10-13-place-file.md. F-030 note, S-02 result. No frame yet.

## [2026-10-13] spike-report | single-file frame
- User frame raw/evidence/2026-10-13-place-file.png shows Johnny nearest, Hanako behind him, Song So Ri furthest. F-030 note, S-02.

## [2026-10-13] decide | place uses a wedge
- ArcadeLink 0.1.6. Three or more names: first name is the point, closest to V. The next two stand behind that point, one to each side, about 1.6 m apart. Two names stay in single file.
- Contract table.v0, ADR-013, F-030 note. The wedge is not yet observed. The running game needs one mod reload.

## [2026-10-13] spike-report | named place, wedge
- Mods reloaded onto 0.1.6. Hello, then place Johnny Silverhand, Hanako, Song So Ri. Log says move, not a new copy.
- Johnny is the point, about 7.51 m along V's facing. Hanako 0.80 m to V's left, Song So Ri 0.80 m to her right, both about 1.39 m further. Each pair about 1.60 m. V stayed at -1536.79, 1194.84, 57.01.
- The wedge stepped forward three times 1.6 m because the file still occupied the nearer marks. Evidence: raw/evidence/2026-10-13-place-wedge.md. F-030, S-02. No frame yet.

## [2026-10-13] spike-report | wedge frames
- User frames show the three apart, and other bodies still standing farther down the roof. raw/evidence/2026-10-13-place-wedge.png, place-wedge-b.png. F-030, S-02.

## [2026-10-13] decide | clear removes everyone near V
- ArcadeLink 0.1.7. `clear` despawns every appearance-menu spawn, then deletes any other person within 18 m. V does not move.
- Contract table.v0, ADR-013, tools/booth.py clear. The running game needs one mod reload before this command exists.

## [2026-10-13] decide | clear stays on the appearance-menu list
- The 18 m sweep would take street crowds. ArcadeLink 0.1.8 removes only people the appearance menu still lists, and the reply names them.
- Contract table.v0, ADR-013. Supersedes the sweep in the entry above. The running game needs one mod reload.

## [2026-10-13] spike-report | clear found an empty list
- Mods on 0.1.8. `clear` replied `removed` empty. Log `clear removed=0`. Saved `spawnedNPCs` length 0.
- Evidence: raw/evidence/2026-10-13-clear.md. F-031. No frame after the command.

## [2026-10-13] decide | place tags entity ids
- Reload drops the appearance menu's list (F-031, R-16). A crowded mark also slid the wedge forward.
- ArcadeLink 0.1.9 writes each placed handle to tagged.json. `clear` removes tagged people within 80 m and reports anyone still missing. Street crowds stay. People already standing have no tag.
- Contract table.v0, ADR-013, F-031 note, R-16. The running game needs one mod reload.

## [2026-10-13] spike-report | place wrote three tags
- Mods on 0.1.9. Place Johnny Silverhand, Hanako, Song So Ri. Log tagged each hash. File `tagged.json` holds the three ids.
- Neighbors about 1.60 m. Johnny about 7.5 m along V's facing. Evidence: raw/evidence/2026-10-13-place-tags.md. F-031 note. No frame. A clear after another reload is not yet observed.

## [2026-10-13] spike-report | clear after reload used the tags
- Reloaded 0.1.9 at 23:37. Hello had no actors. `clear` removed Hanako, Song So Ri, and Johnny Silverhand. `missed` empty. Tag file left empty.
- V stayed at -1540.39, 1200.91, 57.00. Evidence: raw/evidence/2026-10-13-clear-tags.md. F-031 note. No frame.

## [2026-10-13] decide | place can use one formation slot
- ArcadeLink 0.1.10. `formation` is rank, file, or wedge. `slot` and `slots` put one name on one mark of that formation.
- Contract table.v0. The running game needs one mod reload before a sequence can use it.

## [2026-10-13] spike-report | sequence stopped on the first despawn
- 0.1.10 place put Johnny Silverhand on rank slot 1, at -1537.16, 1197.12, 57.01. V stayed at -1536.84, 1194.00, 57.01.
- The following clear never logged and never replied. Status still listed Johnny. ArcadeLink 0.1.11 runs clear on the next game frame instead of inside the socket callback.

## [2026-10-13] spike-report | sequence clear failed on the game frame
- Reloaded 0.1.11 at 23:58. A clear before the drill removed the leftover Johnny Silverhand tag. Rank slot 1 then placed him at -1537.16, 1197.12, 57.01. V stayed at -1536.84, 1194.00, 57.01.
- The next clear ran on the game frame and returned `failed`. Log: `init.lua:567: bad argument #2 to 'insert' (number expected, got string)`. The appearance-menu name is returned from `gsub`, which also returns a count, so `table.insert` treated the name as a position. He was still standing.
- ArcadeLink 0.1.12 keeps only the name. Contract examples. The running game needs one mod reload. Evidence: raw/evidence/2026-10-13-sequence-clear.md.

## [2026-10-14] spike-report | Johnny still on the roof
- User frame shows Johnny Silverhand still standing in front of V after the failed clear. The running game is still 0.1.11. Tag file still holds him.
- Evidence: raw/evidence/2026-10-13-sequence-johnny.png.

## [2026-10-14] spike-report | nine slot spawns and despawns
- Reloaded 0.1.12 at 00:02. A clear removed the leftover Johnny Silverhand. Then rank, file, and wedge, one slot at a time: Johnny Silverhand, Hanako, Song So Ri. Each stood about 4 s. Each clear removed that one person. `missed` stayed empty. Tag file left `[]`.
- Marks stayed at about 2.70 m, neighbors about 1.60 m. V stayed at -1536.84, 1194.00, 57.01. Evidence: raw/evidence/2026-10-14-sequence.md. F-030, F-031, S-02. No frame.

## [2026-10-14] handoff | session closed
- now.md is the resume point. Sequential place and clear passed. Pose and freeze are next. The occupied-mark slide stays open (R-16).
- Lint: 0 errors. The existing orphan warning on src-karpathy-wiki stays.
- Chat archive: raw/chats/2026-10-13_2026-10-14-formations/.

## [2026-10-14] ingest | Cursor chat archive
- raw/chats/2026-10-13_2026-10-14-formations/: parent jsonl, one compaction segment, session.md digest. No subagent threads.
- Resume: read session.md after now.md.
