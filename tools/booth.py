"""Keep a connection open for the game on 127.0.0.1:2077.

Stays up. Prints each hello. Asks the game where V is, to place named people in front of her, or to clear them.

    python tools/booth.py
    python tools/booth.py status
    python tools/booth.py place "Johnny Silverhand"
    python tools/booth.py place "Johnny Silverhand" "Hanako" "Song So Ri"
    python tools/booth.py clear
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

    async def request(self, kind: str, timeout: float, extra: dict | None = None) -> dict:
        writer = self.game_writer
        if writer is None:
            return {"error": "no-game"}
        self.counter += 1
        req_id = f"b{self.counter}"
        loop = asyncio.get_running_loop()
        fut: asyncio.Future = loop.create_future()
        self.pending[req_id] = fut
        body = {"type": kind, "id": req_id}
        if extra:
            body.update(extra)
        payload = json.dumps(body, separators=(",", ":")) + "\r\n"
        writer.write(payload.encode("utf-8"))
        try:
            await writer.drain()
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            self.pending.pop(req_id, None)
            self.game_writer = None
            return {"error": "no-game"}
        try:
            return await asyncio.wait_for(fut, timeout=timeout)
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
        if kind in ("status", "place", "clear"):
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


def names_from_args(args: list[str]) -> list[str]:
    names: list[str] = []
    for arg in args:
        for part in arg.split(","):
            part = part.strip()
            if part:
                names.append(part)
    return names


def parse_control(line: bytes) -> tuple[str, dict | None, float]:
    text = line.strip().decode("utf-8", errors="replace")
    if text == "status":
        return "status", None, 3
    if text == "clear":
        return "clear", None, 20
    if text.startswith("{"):
        try:
            msg = json.loads(text)
        except json.JSONDecodeError:
            return "", None, 3
        if isinstance(msg, dict) and msg.get("cmd") == "status":
            return "status", None, 3
        if isinstance(msg, dict) and msg.get("cmd") == "clear":
            return "clear", None, 20
        if isinstance(msg, dict) and msg.get("cmd") == "place":
            raw = msg.get("names") or []
            if isinstance(raw, str):
                names = names_from_args([raw])
            elif isinstance(raw, list):
                names = names_from_args([str(item) for item in raw])
            else:
                names = []
            extra = {"names": names}
            for key in ("formation", "slot", "slots"):
                if key in msg:
                    extra[key] = msg[key]
            return "place", extra, min(90, 8 + 6 * max(len(names), 1))
    return "", None, 3


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
        cmd, extra, timeout = parse_control(line)
        if cmd == "":
            reply = {"error": "unknown"}
        else:
            reply = await booth.request(cmd, timeout, extra or None)
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


async def ask(kind: str, names: list[str] | None = None) -> int:
    try:
        reader, writer = await asyncio.open_connection(HOST, CTL_PORT)
    except OSError as exc:
        print(f"[booth] {kind} failed: {exc}", flush=True)
        return 1
    if kind == "place":
        payload = json.dumps({"cmd": "place", "names": names or []}, separators=(",", ":")) + "\n"
    elif kind == "clear":
        payload = "clear\n"
    else:
        payload = "status\n"
    writer.write(payload.encode("utf-8"))
    await writer.drain()
    line = await reader.readline()
    writer.close()
    await writer.wait_closed()
    text = line.decode("utf-8", errors="replace").strip()
    print(text, flush=True)
    try:
        message = json.loads(text) if text else {}
    except json.JSONDecodeError:
        return 2
    return 0 if message.get("type") in ("status", "place", "clear") else 2


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        sys.exit(asyncio.run(ask("status")))
    if len(sys.argv) > 1 and sys.argv[1] == "place":
        sys.exit(asyncio.run(ask("place", names_from_args(sys.argv[2:]))))
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        sys.exit(asyncio.run(ask("clear")))
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("[booth] stopped", flush=True)
