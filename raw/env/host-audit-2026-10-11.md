# Host audit — 2026-10-11

Observed by agent via shell on the user's machine. Immutable observation record.

## Hardware
- GPU: NVIDIA GeForce RTX 3060 Ti (8 GB), driver 32.0.15.9186
- CPU: AMD Ryzen 5 5600, 6 cores
- RAM: 16 GB
- Disks: C: 101 GB free / 829 GB used; D: 3423 GB free / 303 GB used

## Tooling
- git (C:\Program Files\Git), Python 3.11 (C:\Users\bento\AppData\Local\Programs\Python\Python311), uv, Node.js (v22.14 installer present)
- OBS Studio NOT installed (installer present: D:\OBS-Studio-32.0.4-Windows-x64-Installer.exe)
- Also present on D:: ComfyUI installer, LM-Studio installer, DaVinci Resolve zips, stable-diffusion-webui folder

## Cyberpunk 2077 install state
- Steam library folders: `C:\Program Files (x86)\Steam`, `D:\SteamLibrary`
- `C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077` exists but holds ONLY the mod layer (179 files, 0.25 GB); game files are uninstalled.
  - `bin\x64\version.dll`, `global.ini`, `winmm.dll`, `plugins\cyber_engine_tweaks.asi` (CET), `plugins\address_library\`
  - CET mods: `AppearanceMenuMod`, `CypherAgent`, `RedSocket`
  - `red4ext\RED4ext.dll`, plugins: `ArchiveXL`, `Codeware`, `RedSocket`
  - `r6\scripts\RedSocket\RedSocket.reds`, `r6\config\redsUserHints\ArchiveXL.toml`
  - `archive\pc\mod\`: basegame_AMM_Props, basegame_AMM_requirement, AMM fixes, PinkyDude facial expressions (M/F V), etc.
  - NO `engine\` folder → redscript compiler (scc) is gone with the uninstall.
- Saves: `%USERPROFILE%\Saved Games\CD Projekt Red\Cyberpunk 2077` → AutoSave-0/11/12, ManualSave-0, QuickSave-0 (Steam cloud)
- Last RED4ext log (2026-04-05): product version 2.31; RED4ext v1.30.0; ArchiveXL 1.26.3, Codeware 1.19.0, RedSocket 0.5.0 loaded (3 plugins).
- Last CET scripting log line of interest: `[Cypher SOCKET ERROR] RedSocket connection failed.` (bridge not running at game start).

## Mod archives on D:\ (re-install sources)
- `cet_1.37.1.zip`, `RED4ext-2380-1-30-0-*.zip` / `red4ext-1.30.0.zip`, `RedSocket-0.5.0.zip`,
  `Codeware-7780-1-19-0-*.zip`, `ArchiveXL-4198-1-26-3-*.zip`, `Appearance Menu Mod-790-2-12-5-*.zip`
- No redscript archive found.

## Prior project folders
- `D:\night-city-live` — canonical prior repo (git; 6 commits; last: AMM spawn export). Bridge + CypherAgent CET mod + AMM catalog SQLite (4,363 entities, 43,765 workspots).
- `D:\cypher-vision` — shelved duplicate (per HANDOFF-2026-06).
- `D:\cppc` — Cyberpunk audio-drama pipeline ("Night City Holocaust"): lore integration framework, linguistics guide, Hailuo/ElevenLabs tutorials, voiced character audio.
- Cyberpunk OST / SFX mp3s in D:\ root.
