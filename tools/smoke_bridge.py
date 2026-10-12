"""Drive the night-city-live bridge for the Phase 0 smoke test.

Starts `server/bridge.py --interactive --quiet`, waits for Cypher to connect,
then sends `ammchars` and `spawnname npc_test Johnny Silverhand`.
"""

from __future__ import annotations

import argparse
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

DEFAULT_BRIDGE = Path(r"D:\night-city-live\server\bridge.py")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bridge", type=Path, default=DEFAULT_BRIDGE)
    ap.add_argument("--port", type=int, default=2077)
    ap.add_argument("--wait", type=float, default=90.0, help="seconds to wait for the game to connect")
    ap.add_argument("--after", type=float, default=8.0, help="seconds to keep reading after spawn")
    args = ap.parse_args(argv)

    cmd = [sys.executable, "-u", str(args.bridge), "--port", str(args.port), "--interactive", "--quiet"]
    print(f"[smoke] starting {' '.join(cmd)}", flush=True)
    env = {**__import__("os").environ, "PYTHONUNBUFFERED": "1"}
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )
    assert proc.stdin is not None and proc.stdout is not None

    lines: queue.Queue[str | None] = queue.Queue()

    def _pump() -> None:
        assert proc.stdout is not None
        for raw in proc.stdout:
            lines.put(raw)
        lines.put(None)

    threading.Thread(target=_pump, daemon=True).start()

    def drain(until: float) -> str | None:
        while True:
            remaining = until - time.monotonic()
            if remaining <= 0:
                return None
            try:
                item = lines.get(timeout=min(remaining, 0.5))
            except queue.Empty:
                continue
            if item is None:
                return None
            print(item, end="", flush=True)
            return item

    connected = False
    deadline = time.monotonic() + args.wait
    try:
        while time.monotonic() < deadline:
            if proc.poll() is not None and lines.empty():
                print("[smoke] bridge exited before connect", flush=True)
                return 2
            line = drain(min(deadline, time.monotonic() + 1.0))
            if line and "[bridge] connected:" in line:
                connected = True
                break
        if not connected:
            print(
                f"[smoke] no Cypher connect in {args.wait:.0f}s. "
                "Reload CypherAgent from the CET overlay (Ctrl+`) while this server stays up.",
                flush=True,
            )
            return 3

        for command in ("ammchars 20", "spawnname npc_test Johnny Silverhand"):
            print(f"[smoke] >>> {command}", flush=True)
            proc.stdin.write(command + "\n")
            proc.stdin.flush()
            time.sleep(0.4)

        end = time.monotonic() + args.after
        while time.monotonic() < end:
            drain(end)
        return 0
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
