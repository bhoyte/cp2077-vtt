# Host audit — 2026-10-11 (post C: install)

Observed by agent after the user reported installing CP2077 on the C: SSD.

## Disks
- C: KINGSTON SNV2S1000G (SSD), NTFS, 51.2 GB free / 930 GB (was 101 GB free earlier the same day).
- D: TOSHIBA EXTERNAL_USB (HDD, USB), NTFS, 3414.9 GB free / 3725.9 GB.

## Steam libraries
- `C:\Program Files (x86)\Steam` — library 0; contains app 1091500 (Cyberpunk 2077), SizeOnDisk 91,328,398,342.
- `D:\SteamLibrary` — library 1; no apps.

## Game
- Path: `C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077`
- `bin\x64\Cyberpunk2077.exe` ProductVersion 2.31, FileVersion 3.0.5294808.
- Steam `appmanifest_1091500.acf`: StateFlags 4 (fully installed), buildid 20383525, AutoUpdateBehavior 0 (Steam will auto-update).
- Depots: 1091501 (base, 66.4 GB), 2060310 (optional DLC, 97 MB), 2138330 (Phantom Liberty, 24.9 GB).
- `archive\pc\ep1` present.

## Mod layer (survived the reinstall, still in the same folder)
- CET: `bin\x64\version.dll`, `plugins\cyber_engine_tweaks.asi`
- CET mods: AppearanceMenuMod, CypherAgent, RedSocket
- RED4ext + plugins: ArchiveXL, Codeware, RedSocket
- `r6\scripts`, `r6\config`
- `archive\pc\mod`: AMM props/requirement/fixes, PinkyDude facial expressions, johnny companion, etc.

## redscript
- Vanilla `engine\` is back (config + shader caches). This is the game's own folder, not the redscript compiler.
- Community redscript (`engine\tools\scc.exe` or equivalent) is still absent.
- `tools\redmod\bin\scc.exe` is CDPR REDmod, not redscript.
