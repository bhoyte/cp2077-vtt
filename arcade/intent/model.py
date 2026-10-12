"""Chat messages and the ballots the vote book stores."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Option:
    """One numbered choice on a vote window. `id` is ``1``–``4``."""

    id: str
    label: str
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class ChatMsg:
    """One chat line. ChatSim and (later) Twitch EventSub both build these.

    `seat` is the squad this account belongs to. This slice does not check
    account age or follow time; the caller has already decided membership.
    """

    user_id: str
    login: str
    ts_arrival: float
    text: str
    badges: tuple[str, ...] = ()
    seat: str | None = None


@dataclass(frozen=True)
class Ballot:
    """One account's current vote in a window. A later ballot replaces it."""

    user_id: str
    option: str
    ts: float
    layer: str
    conf: float


@dataclass(frozen=True)
class Hit:
    """A message that classified as a vote."""

    option: str
    layer: str
    conf: float
