# Session redial (2026-10-13 02:21–02:24)

Game already running. One CET reload loaded ArcadeLink 0.1.2. Booth was already listening. No player teleport. The roof cast was not commanded.

02:21:04 hello, player `-1536.78, 1195.77, 57.00`, actors empty.

Booth process stopped. `IsConnected` had stayed true on the previous build (0.1.1, 00:00) and `OnDisconnection` did not fire, so that build did not redial. 0.1.2 treats three seconds without a booth ping as down.

02:23:59 `[ArcadeLink] link down quiet=3.4`
02:24:07 `[ArcadeLink] connected` then `hello sent`

No reload between those two lines. `python tools/booth.py status` returned the same player position, `id=b1`, `version=0.1.2`.
