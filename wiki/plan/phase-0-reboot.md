---
type: plan
title: Phase 0 — reinstall, restore the mod stack, smoke test, freeze
status: active
updated: 2026-10-11
depends_on: [ADR-011, F-014, F-017, F-018]
---

# Phase 0 — Reboot (≈ 1 day, mostly download time)

## 1. Install to D:
1. Steam → Library → Cyberpunk 2077 → Install → **choose `D:\SteamLibrary`** (not C:, ADR-011). Include Phantom Liberty if owned (Q-04).
2. Steam → game Properties → Updates → "Only update this game when I launch it".
3. Don't launch yet.

## 2. Move the surviving mod layer (C: → D:)
From `C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077\` copy into `D:\SteamLibrary\steamapps\common\Cyberpunk 2077\`, merging folders:
- `bin\x64\version.dll`, `bin\x64\global.ini`, `bin\x64\winmm.dll`, `bin\x64\LICENSE`, `bin\x64\plugins\` (CET + mods AMM/CypherAgent/RedSocket + address_library)
- `red4ext\` (RED4ext + ArchiveXL, Codeware, RedSocket plugins; skip `logs\`)
- `r6\scripts\`, `r6\config\`
- `archive\pc\mod\` (AMM props, fixes, expression packs)

Then zip the C: folder to `D:\cp2077-stack\remnant-2026-04.zip` and delete it, so Steam never sees two installs.

## 3. Restore what the uninstall removed
- **redscript** (≥ 0.5.27 for 2.31) from its GitHub releases or Nexus; extract to the game root (creates `engine\` + `r6\`). Codeware and RedSocket need it (F-017).
- Check AMM's Nexus requirements tab and install anything listed that's missing (the stack verified in April ran AMM 2.12.5 with RED4ext, Codeware, ArchiveXL).
- Fresh archives are already on D:\ for CET 1.37.1, RED4ext 1.30.0, RedSocket 0.5.0, Codeware 1.19.0, ArchiveXL 1.26.3, AMM 2.12.5 if anything is corrupt.

## 4. Smoke test (the old bridge proves the stack)
```powershell
cd D:\night-city-live
python server/bridge.py --port 2077 --interactive --quiet
```
Launch the game, load a save, close the CET overlay (F-010). In the bridge: `ammchars 20` → `spawnname npc_test Johnny Silverhand`.
Expect: CET `[Cypher SOCKET] Connected…` then `[Cypher] spawn complete`. Check `red4ext\logs\` shows RED4ext 1.30.0 + 3 plugins on 2.31.

## 5. Stream-oriented game settings
Streamer Mode on (licensed music) · crowd density Low · HUD elements off where the Interface menu allows · 1080p, DLSS Quality, RT off · frame cap 60.

## 6. Freeze
Zip `bin\x64\plugins`, `red4ext` (no logs), `r6`, `engine`, `archive\pc\mod` + `bin\x64\Cyberpunk2077.exe` hash → `D:\cp2077-stack\stack-2.31-YYYYMMDD.zip`.
**spike-report** the result: re-verify F-001/F-004 with today's date, update F-017, log it.

## 7. Also install
OBS Studio 32.0.4 (installer on D:\) — needed for S-05.
