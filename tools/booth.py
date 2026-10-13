"""Booth: hold 127.0.0.1:2077 for the ArcadeLink session.

Stays up. Prints each hello. Does not cast, pose, or decide a show.

    python tools/booth.py
    python tools/booth.py status
"""

from __future__ import annotations

import asyncio
import json
import sys

HOST = "127.0.0.1"
GAME_PORT = 2077
CTL_PORT = 2078


class Booth:
    def __init__(self) -> None:
        self.game_writer: asyncio.StreamWriter | None = None
        self.pending: dict[str, asyncio.Future] = {}
        self.counter = 0

    def fail_waiters(self, reason: str) -> None:
        waiters = list(self.pending.items())
        self.pending.clear()
        for _, fut in waiters:
            if not fut.done():
                fut.set_result({"error": reason})

    async def request_status(self) -> dict:
        writer = self.game_writer
        if writer is None:
            return {"error": "no-game"}
        self.counter += 1
        req_id = f"b{self.counter}"
        loop = asyncio.get_running_loop()
        fut: asyncio.Future = loop.create_future()
        self.pending[req_id] = fut
        payload = json.dumps({"type": "status", "id": req_id}, separators=(",", ":")) + "\r\n"
        writer.write(payload.encode("utf-8"))
        try:
            await writer.drain()
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            self.pending.pop(req_id, None)
            self.game_writer = None
            return {"error": "no-game"}
        try:
            return await asyncio.wait_for(fut, timeout=3)
        except asyncio.TimeoutError:
            self.pending.pop(req_id, None)
            return {"error": "timeout"}

    def on_game_message(self, message: dict) -> None:
        kind = message.get("type")
        if kind == "ping":
            return
        if kind == "hello":
            print("[booth] hello " + json.dumps(message, separators=(",", ":")), flush=True)
            return
        if kind == "status":
            fut = self.pending.pop(str(message.get("id")), None)
            if fut is not None and not fut.done():
                fut.set_result(message)
            return
        print("[booth] ignored " + json.dumps(message, separators=(",", ":")), flush=True)


async def read_game(booth: Booth, reader: asyncio.StreamReader) -> None:
    buf = ""
    while True:
        chunk = await reader.read(4096)
        if not chunk:
            break
        buf += chunk.decode("utf-8", errors="replace")
        while "\n" in buf:
            raw, buf = buf.split("\n", 1)
            raw = raw.strip()
            if not raw:
                continue
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                print(f"[booth] bad line {raw!r}", flush=True)
                continue
            if isinstance(message, dict):
                booth.on_game_message(message)


async def serve() -> None:
    booth = Booth()

    async def handle_game(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        if booth.game_writer is not None and booth.game_writer is not writer:
            try:
                booth.game_writer.close()
            except OSError:
                pass
        booth.game_writer = writer
        peer = writer.get_extra_info("peername")
        print(f"[booth] game attached {peer}", flush=True)
        try:
            await read_game(booth, reader)
        finally:
            if booth.game_writer is writer:
                booth.game_writer = None
            booth.fail_waiters("disconnected")
            print("[booth] game detached", flush=True)
            try:
                writer.close()
                await writer.wait_closed()
            except OSError:
                pass

    async def handle_ctl(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            line = await asyncio.wait_for(reader.readline(), timeout=5)
        except asyncio.TimeoutError:
            line = b""
        reply: dict
        if line.strip() == b"status":
            reply = await booth.request_status()
        else:
            reply = {"error": "unknown"}
        writer.write((json.dumps(reply, separators=(",", ":")) + "\n").encode("utf-8"))
        try:
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except OSError:
            pass

    game_server = await asyncio.start_server(handle_game, HOST, GAME_PORT)
    ctl_server = await asyncio.start_server(handle_ctl, HOST, CTL_PORT)
    print(f"[booth] listening on {HOST}:{GAME_PORT} ctl {HOST}:{CTL_PORT}", flush=True)

    async def heartbeat() -> None:
        while True:
            await asyncio.sleep(1.0)
            writer = booth.game_writer
            if writer is None:
                continue
            try:
                writer.write(b'{"type":"ping"}\r\n')
                await writer.drain()
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                if booth.game_writer is writer:
                    booth.game_writer = None

    asyncio.create_task(heartbeat())
    async with game_server, ctl_server:
        await asyncio.Future()


async def ask_status() -> int:
    try:
        reader, writer = await asyncio.open_connection(HOST, CTL_PORT)
    except OSError as exc:
        print(f"[booth] status failed: {exc}", flush=True)
        return 1
    writer.write(b"status\n")
    await writer.drain()
    line = await reader.readline()
    writer.close()
    await writer.wait_closed()
    text = line.decode("utf-8", errors="replace").strip()
    print(text, flush=True)
    return 0 if text and '"error"' not in text else 2


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        sys.exit(asyncio.run(ask_status()))
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("[booth] stopped", flush=True)
