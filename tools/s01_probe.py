"""S-01 camera-rig probe.

Listens on 127.0.0.1:2077 (RedSocket / CypherAgent), waits until the game is
in-world (first SceneSnapshot), then sends cam_* commands through CypherAgent.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

HOST = "127.0.0.1"
PORT = 2077
COMMAND_SCHEMA = "bridge_command.v0.1"
ACK_SCHEMA = "bridge_ack.v0.1"

DEFAULT_CET_LOG = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077"
    r"\bin\x64\plugins\cyber_engine_tweaks\scripting.log"
)

STEPS: list[tuple[str, dict, float]] = [
    ("cam_probe", {}, 2.0),
    ("cam_spawn", {}, 12.0),
    ("cam_hide", {}, 2.0),
    ("cam_cut", {"cam": "cam_a", "blend": 0}, 3.0),
    ("cam_cut", {"cam": "cam_b", "blend": 0}, 3.0),
    ("cam_cut", {"cam": "cam_c", "blend": 1.5}, 5.0),
    ("cam_status", {}, 1.0),
    ("cam_despawn", {}, 2.0),
]


def command(counter: int, action: str, payload: dict) -> dict:
    return {
        "type": "command",
        "schema_version": COMMAND_SCHEMA,
        "id": f"s01-{counter}",
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


def _xy(pos: dict) -> tuple[float, float]:
    try:
        return float(pos.get("x", 0)), float(pos.get("y", 0))
    except (TypeError, ValueError):
        return 0.0, 0.0


def in_night_city(pos: dict) -> bool:
    """Menu / load puppets sit near the origin. Soundstage coords do not."""
    x, y = _xy(pos)
    return (x * x + y * y) ** 0.5 > 50.0


class CetLogTail:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._fh = None
        self.hits: list[str] = []

    def open(self) -> None:
        if not self.path.exists():
            print(f"[s01] CET log not found yet: {self.path}", flush=True)
            return
        self._fh = self.path.open("r", encoding="utf-8", errors="replace")
        self._fh.seek(0, 2)

    def drain(self) -> list[str]:
        if self._fh is None:
            if self.path.exists():
                self.open()
            if self._fh is None:
                return []
        new: list[str] = []
        while True:
            line = self._fh.readline()
            if not line:
                break
            if "[ArcadeSpike]" in line or "[Cypher CMD" in line or "ArcadeSpike" in line:
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


async def run(host: str, port: int, wait: float, cet_log: Path, hold: float) -> int:
    tail = CetLogTail(cet_log)
    tail.open()
    connected = asyncio.Event()
    in_world = asyncio.Event()
    state: dict = {"writer": None, "addr": None, "snaps": 0}

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        state["gen"] = state.get("gen", 0) + 1
        state["writer"] = writer
        state["addr"] = writer.get_extra_info("peername")
        print(f"[s01] connected: {state['addr']} gen={state['gen']}", flush=True)
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
                        print(f"[s01] bad json: {raw[:120]}", flush=True)
                        continue
                    if msg.get("schema_version") == "scene_snapshot.v0.1":
                        state["snaps"] += 1
                        tick = msg.get("tick_id")
                        try:
                            await send(writer, ack(tick))
                        except (ConnectionResetError, ConnectionAbortedError, OSError):
                            break
                        pos = (msg.get("player") or {}).get("position") or {}
                        if in_night_city(pos):
                            state["real"] = state.get("real", 0) + 1
                            if not in_world.is_set() and state["real"] >= 3:
                                print(
                                    f"[s01] in-world tick={tick} pos={pos}",
                                    flush=True,
                                )
                                in_world.set()
                        else:
                            state["real"] = 0
                            if state["snaps"] == 1 or state["snaps"] % 25 == 0:
                                print(
                                    f"[s01] waiting for a loaded save (menu/load pos={pos})",
                                    flush=True,
                                )
        finally:
            print("[s01] game disconnected", flush=True)
            if state["writer"] is writer:
                state["writer"] = None
            try:
                writer.close()
                await writer.wait_closed()
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                pass

    server = await asyncio.start_server(handle, host, port)
    print(f"[s01] listening on {host}:{port}", flush=True)
    print(
        "[s01] Start or reload CypherAgent while this stays up. "
        "Load a save, then close the CET overlay.",
        flush=True,
    )
    try:
        try:
            await asyncio.wait_for(connected.wait(), timeout=wait)
        except asyncio.TimeoutError:
            print(
                f"[s01] no connect in {wait:.0f}s. "
                "Reload CypherAgent from the CET overlay (Ctrl+`) while this server stays up.",
                flush=True,
            )
            return 3

        if not in_world.is_set():
            print("[s01] connected; waiting for an in-world snapshot…", flush=True)
            try:
                await asyncio.wait_for(in_world.wait(), timeout=wait)
            except asyncio.TimeoutError:
                print("[s01] connected but never saw a player snapshot. Load a save.", flush=True)
                return 4

        writer = state["writer"]
        run_gen = state.get("gen")
        if writer is None:
            print("[s01] writer lost after connect", flush=True)
            return 5

        def still_same() -> bool:
            return state["writer"] is writer and state.get("gen") == run_gen

        for i, (action, payload, pause) in enumerate(STEPS, start=1):
            if not still_same():
                print("[s01] game dropped mid-probe; sequence stopped", flush=True)
                return 6
            msg = command(i, action, payload)
            print(f"[s01] >>> {action} {payload}", flush=True)
            await send(state["writer"], msg)
            deadline = time.monotonic() + pause
            while time.monotonic() < deadline:
                if not still_same():
                    print("[s01] game dropped mid-probe; sequence stopped", flush=True)
                    return 6
                tail.drain()
                await asyncio.sleep(0.2)

        print(
            f"[s01] sequence sent. Holding {hold:.0f}s so you can look / grab OBS frames. "
            "Cameras stay live until cam_despawn or a CET reload.",
            flush=True,
        )
        end = time.monotonic() + hold
        while time.monotonic() < end:
            tail.drain()
            await asyncio.sleep(0.4)
        tail.drain()
        print(f"[s01] captured {len(tail.hits)} ArcadeSpike/Cypher lines", flush=True)
        return 0
    finally:
        tail.close()
        server.close()
        await server.wait_closed()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=HOST)
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--wait", type=float, default=180.0)
    ap.add_argument("--hold", type=float, default=20.0)
    ap.add_argument("--cet-log", type=Path, default=DEFAULT_CET_LOG)
    args = ap.parse_args(argv)
    return asyncio.run(run(args.host, args.port, args.wait, args.cet_log, args.hold))


if __name__ == "__main__":
    sys.exit(main())
