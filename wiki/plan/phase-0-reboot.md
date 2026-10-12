---
type: plan
title: Phase 0 — restore redscript, smoke test, freeze (game already on C:)
status: done
updated: 2026-10-11
depends_on: [ADR-012, F-014, F-017, F-020, F-021]
---

# Phase 0 — Reboot (install is done; remaining work is restore + pin)

The game is already at `C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077` (2.31, 91 GB, Phantom Liberty on disk, April mod layer still in the folder). Do **not** move it to D: — D: is a USB HDD (ADR-012).

## 1. Pin Steam — done
`appmanifest_1091500.acf` has `AutoUpdateBehavior` `1` (only update when launched). Confirm in Steam UI if you want: Properties → Updates.

## 2. Restore what the uninstall still lacks
- **redscript — done.** v0.5.31 extracted into the game root from GitHub (`D:\cp2077-stack\redscript-v0.5.31-windows.zip`). Files: `engine\tools\scc.exe`, `scc_lib.dll`, `engine\config\base\scripts.ini`, `r6\config\cybercmd\scc.toml` (F-017).
- Check AMM's Nexus requirements tab and install anything listed that's missing (the April stack ran AMM 2.12.5 with RED4ext, Codeware, ArchiveXL — those folders are still present).
- Fresh archives are on D:\ for CET 1.37.1, RED4ext 1.30.0, RedSocket 0.5.0, Codeware 1.19.0, ArchiveXL 1.26.3, AMM 2.12.5 if anything is corrupt.

## 3. Smoke test — done 2026-10-11
See [raw/evidence/2026-10-11-phase0-smoke.md](../../raw/evidence/2026-10-11-phase0-smoke.md). Johnny spawn complete after Cypher reload. Remaining: pin Steam, freeze, OBS.
```powershell
cd D:\night-city-live
python server/bridge.py --port 2077 --interactive --quiet
```
Launch the game from Steam (or the exe, if testing F-019), load a save, close the CET overlay (F-010). In the bridge: `ammchars 20` → `spawnname npc_test Johnny Silverhand`.
Expect: CET `[Cypher SOCKET] Connected…` then `[Cypher] spawn complete`. Check `red4ext\logs\` shows RED4ext 1.30.0 + 3 plugins on 2.31.

## 4. Stream-oriented game settings
Streamer Mode on (licensed music) · crowd density Low · HUD elements off where the Interface menu allows · 1080p, DLSS Quality, RT off · frame cap 60.

## 5. Freeze — done 2026-10-11
See [raw/evidence/2026-10-11-stack-freeze.md](../../raw/evidence/2026-10-11-stack-freeze.md).
- `D:\cp2077-stack\stack-2.31-20261011.zip` (245 MB) + staging folder
- `D:\cp2077-stack\game-2.31\` full copy (5141 files, 85 GB; robocopy exit 1)
- F-019: exe launch with Steam running started 2.31 + RED4ext; no pending update to skip

## 6. OBS — already installed
OBS Studio **32.2.2** at `C:\Program Files\obs-studio\bin\64bit\obs64.exe` (F-022). The 32.0.4 installer on D:\ is unused. Capture budget is S-05, not a Phase 0 blocker.
