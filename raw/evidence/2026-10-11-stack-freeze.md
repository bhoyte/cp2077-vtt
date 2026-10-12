# Stack freeze — 2026-10-11

Game was not running. Steam was.

## Mod-layer zip
- `D:\cp2077-stack\stack-2.31-20261011.zip` (244,663,422 bytes)
- Staging also left at `D:\cp2077-stack\staging-stack-2.31-20261011\` (187 files, ~393 MB uncompressed)
- Contents: CET loaders (`version.dll`, `winmm.dll`, `global.ini`), `bin\x64\plugins` (CET + AMM + CypherAgent + RedSocket), `red4ext` (no `logs\`), `r6` (no `logs\`), `engine\tools` (redscript 0.5.31), `engine\config\base\scripts.ini`, `archive\pc\mod`
- `Cyberpunk2077.exe` ProductVersion 2.31 SHA256 `A7DE82945C03E041FC7339FCF9066224D98DB2F5D80FEA50F7947BB350A60991`

## Full game folder
- `D:\cp2077-stack\game-2.31\` — robocopy 2026-10-11 21:04–21:25, exit 1 (success: files copied)
- 5141 files, 85.322 GB (Steam SizeOnDisk was 91 GB; `logs\` dirs excluded)
- Backup exe SHA256 matches live: `A7DE82945C03E041FC7339FCF9066224D98DB2F5D80FEA50F7947BB350A60991`

## F-019 exe launch (Steam already running)
- `Start-Process` live `bin\x64\Cyberpunk2077.exe` at 21:25:34 → pid 12320 immediately
- New `red4ext-2026-10-11-21-25-35.log`: RED4ext 1.30.0, product 2.31, 3 plugins, scc invoked
- Steam `LastUpdated` unchanged (`1791761049`); `buildid` == `TargetBuildID` (20383525) so there was no pending update to skip. "Starts" is verified; "skips a pending Steam update" is still untested.
