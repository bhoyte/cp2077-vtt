# redscript restore — 2026-10-11

Installed community redscript into the live C: game folder.

- Source: https://github.com/jac3km4/redscript/releases/download/v0.5.31/redscript-v0.5.31-windows.zip
- Kept zip: `D:\cp2077-stack\redscript-v0.5.31-windows.zip` SHA256 `799BBD88863F6728616F8D723C941EA15DFF71ED5BBFD50C525F0D39EA0BF46B`
- Extracted into `C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077` (no pre-existing `engine\tools` or `scripts.ini`).

| Rel path | Size | SHA256 |
|---|---|---|
| engine\config\base\scripts.ini | 39 | EA8281682D4130F872E1703B25AA989A823F136FA1D886077AF24AEDB08B0D4C |
| engine\tools\scc.exe | 449024 | DA2C0DE580173010C907A05FDD2F3CD2430D6E62BF748339D65060118AE32EDD |
| engine\tools\scc_lib.dll | 1988608 | 49EB60A3613C990CD13B6136E827A74F9F64AD68E2F911D8C93E4E3D3F53C100 |
| r6\config\cybercmd\scc.toml | 228 | 05802A334D72E87194D49765B7B852C2A983F8849851ABCF3FD1366F64D4A934 |

`scripts.ini` contents: `[Scripts] EnableCompilation = "true"`.

In-game compile is not yet observed (no launch). Confirm on first smoke test via `r6\logs\redscript_rCURRENT.log`.
