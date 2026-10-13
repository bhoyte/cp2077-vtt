"""S-02 separation: three actors in front of V, posed only after they land.

Listens on 127.0.0.1:2077. Reload CypherAgent (and ArcadeSpike) from the CET
overlay while this process is up. Captures the game window. Does not despawn.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

HOST = "127.0.0.1"
PORT = 2077
COMMAND_SCHEMA = "bridge_command.v0.1"
ACK_SCHEMA = "bridge_ack.v0.1"
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "raw" / "evidence"
CET_LOG = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077"
    r"\bin\x64\plugins\cyber_engine_tweaks\scripting.log"
)


def command(counter: int, action: str, payload: dict) -> dict:
    return {
        "type": "command",
        "schema_version": COMMAND_SCHEMA,
        "id": f"s02-{counter}",
        "target": "spike",
        "action": action,
        "payload": payload,
        "issued_at": int(time.time() * 1000),
    }


def ack(tick_id) -> dict:
    return {
        "type": "ack",
        "schema_version": ACK_SCHEMA,
        "status": "ok",
        "tick_id": tick_id,
        "received_at_ms": int(time.time() * 1000),
    }


def in_night_city(pos: dict) -> bool:
    try:
        x = float(pos.get("x", 0))
        y = float(pos.get("y", 0))
    except (TypeError, ValueError):
        return False
    return (x * x + y * y) ** 0.5 > 50.0


def capture(name: str) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    dest = EVIDENCE / name
    script = r"""
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win {
  public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
$game = Get-Process -Name Cyberpunk2077 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $game) { Write-Output "NO_PROCESS"; exit 2 }
$script:hwnd = [IntPtr]::Zero
$script:area = 0
[Win]::EnumWindows({
  param($h, $l)
  $proc = 0
  [void][Win]::GetWindowThreadProcessId($h, [ref]$proc)
  if ($proc -eq $game.Id -and [Win]::IsWindowVisible($h)) {
    $r = New-Object Win+RECT
    [void][Win]::GetWindowRect($h, [ref]$r)
    $w = $r.Right - $r.Left
    $hgt = $r.Bottom - $r.Top
    if ($w * $hgt -gt $script:area) {
      $script:area = $w * $hgt
      $script:hwnd = $h
      $script:rect = $r
    }
  }
  return $true
}, [IntPtr]::Zero) | Out-Null
if ($script:hwnd -eq [IntPtr]::Zero) { Write-Output "NO_WINDOW"; exit 3 }
$r = $script:rect
$w = $r.Right - $r.Left
$hgt = $r.Bottom - $r.Top
$bmp = New-Object System.Drawing.Bitmap $w, $hgt
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size $w, $hgt))
$bmp.Save($env:S02_CAPTURE)
$g.Dispose()
$bmp.Dispose()
Write-Output ("OK {0} {1}x{2} @ {3},{4}" -f $script:hwnd, $w, $hgt, $r.Left, $r.Top)
"""
    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    env["S02_CAPTURE"] = str(dest)
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    print(f"[s02] capture {name}: {(proc.stdout or proc.stderr).strip()}", flush=True)


class CetLogTail:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._fh = None
        self.hits: list[str] = []

    def open(self) -> None:
        if not self.path.exists():
            return
        self._fh = self.path.open("r", encoding="utf-8", errors="replace")
        self._fh.seek(0, 2)

    def drain(self) -> list[str]:
        if self._fh is None:
            self.open()
            if self._fh is None:
                return []
        new: list[str] = []
        while True:
            line = self._fh.readline()
            if not line:
                break
            if "[ArcadeSpike]" in line or "COMMAND RECEIVED" in line or "SOCKET" in line:
                text = line.rstrip()
                new.append(text)
                self.hits.append(text)
                print(f"[cet] {text}", flush=True)
        return new

    def close(self) -> None:
        if self._fh is not None:
            self._fh.close()


async def send(writer: asyncio.StreamWriter, payload: dict) -> None:
    writer.write((json.dumps(payload, separators=(",", ":")) + "\r\n").encode("utf-8"))
    await writer.drain()


async def run() -> int:
    tail = CetLogTail(CET_LOG)
    tail.open()
    connected = asyncio.Event()
    in_world = asyncio.Event()
    state: dict = {"writer": None, "gen": 0, "snaps": 0, "real": 0}

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        state["gen"] += 1
        state["writer"] = writer
        print(f"[s02] connected gen={state['gen']}", flush=True)
        connected.set()
        buf = ""
        try:
            while True:
                chunk = await reader.read(4096)
                if not chunk:
                    break
                buf += chunk.decode("utf-8", errors="replace")
                while "\r\n" in buf:
                    raw, buf = buf.split("\r\n", 1)
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        msg = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    if msg.get("schema_version") == "scene_snapshot.v0.1":
                        state["snaps"] += 1
                        try:
                            await send(writer, ack(msg.get("tick_id")))
                        except (ConnectionResetError, ConnectionAbortedError, OSError):
                            break
                        pos = (msg.get("player") or {}).get("position") or {}
                        state["player"] = pos
                        if in_night_city(pos):
                            state["real"] += 1
                            if not in_world.is_set() and state["real"] >= 3:
                                print(f"[s02] in-world pos={pos}", flush=True)
                                in_world.set()
                        else:
                            state["real"] = 0
        finally:
            print("[s02] game disconnected", flush=True)
            if state["writer"] is writer:
                state["writer"] = None
            try:
                writer.close()
                await writer.wait_closed()
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                pass

    server = await asyncio.start_server(handle, HOST, PORT)
    print(f"[s02] listening on {HOST}:{PORT}", flush=True)
    try:
        try:
            await asyncio.wait_for(connected.wait(), timeout=180)
        except asyncio.TimeoutError:
            print("[s02] no connect in 180s. Reload all mods from the CET overlay.", flush=True)
            return 3
        if not in_world.is_set():
            try:
                await asyncio.wait_for(in_world.wait(), timeout=60)
            except asyncio.TimeoutError:
                print("[s02] connected but not in a loaded save", flush=True)
                return 4

        writer = state["writer"]
        gen = state["gen"]

        def same() -> bool:
            return state["writer"] is writer and state.get("gen") == gen

        if not same():
            print("[s02] dropped before cast", flush=True)
            return 6
        print("[s02] >>> pup_cast", flush=True)
        await send(writer, command(1, "pup_cast", {}))

        done = False
        deadline = time.monotonic() + 35
        while time.monotonic() < deadline and not done:
            if not same():
                print("[s02] dropped during cast", flush=True)
                return 6
            for line in tail.drain():
                if "RESULT pup_cast=done" in line:
                    done = True
                    break
            await asyncio.sleep(0.25)
        if not done:
            print("[s02] cast did not finish", flush=True)
            return 7

        # Leave the cast in the world. Capture the player's own view.
        await asyncio.sleep(1.5)
        tail.drain()
        capture("2026-10-12-s02-aitp.png")
        await asyncio.sleep(1.0)
        capture("2026-10-12-s02-aitp-b.png")
        print("[s02] cast left in place for inspection", flush=True)
        print(f"[s02] log lines {len(tail.hits)} player={state.get('player')}", flush=True)
        return 0
    finally:
        tail.close()
        server.close()
        await server.wait_closed()


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
