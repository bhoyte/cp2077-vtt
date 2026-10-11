---
type: decision
id: ADR-008
title: Python orchestrator, TypeScript overlay, Lua stage mod, schemas as single source of truth; fake stage first-class
status: accepted
updated: 2026-10-11
revisit_if: Overlay and orchestrator types drift more than once
depends_on: [F-001]
---

# ADR-008 — Stack

| Part | Choice | Why |
|---|---|---|
| Orchestrator | Python 3.11+, asyncio, `uv`-managed | Existing bridge code and catalog tools; good asyncio TCP/WS; Python 3.11 is installed |
| Schemas | Pydantic v2 models → exported JSON Schema → generated TS types | One definition for wire, ledger, and overlay |
| Overlay | Vite + TypeScript (one page, several layers), WebSocket from the orchestrator | One OBS browser source keeps RAM low (R-09) |
| OBS control | obs-websocket v5 (built into OBS 28+) | Scene switches, media stingers, screenshots for portraits |
| Chat | Twitch EventSub over WebSocket (`channel.chat.message`, channel-point redemptions) | Current Twitch API; IRC is legacy |
| Stage mod | CET Lua (`ArcadeStage`), RedSocket, AMM as a library | Verified path (F-001, F-004) |
| Tests | pytest + hypothesis (rules properties), golden replays, recorded chat fixtures | Determinism makes golden tests trivial |

**Fake stage (first-class).** A Python `FakeStage` speaks `stage.v1` exactly like the CET mod and renders a 2D tactical
view (nodes, pawns, HP, cut markers) in the overlay. Uses:
1. Build and play the whole show while CP2077 isn't installed.
2. CI end-to-end tests.
3. **On-air failover.** If the game drops, OBS cuts to the "tactical feed" and the show goes on.

**Overturns from night-city-live.** Its bans on WebSockets and HTTP were about the *game* transport. The overlay and
OBS legitimately need WebSocket.
