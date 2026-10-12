"""Replay a scripted chat into the show clock. Not a Twitch client."""

from __future__ import annotations

from collections.abc import Sequence

from arcade.intent import ChatMsg
from arcade.show import ShowClock, ShowEvent


class ChatSim:
    def __init__(self, messages: Sequence[ChatMsg]) -> None:
        self.messages = tuple(messages)

    def replay(self, clock: ShowClock, *, until: float | None = None) -> list[ShowEvent]:
        """Start the clock, deliver each message at its arrival time, then finish the show.

        Equal timestamps keep input order. Times before the clock's start are rejected
        by the clock.
        """

        events = list(clock.start())
        for msg in sorted(self.messages, key=lambda item: item.ts_arrival):
            events.extend(clock.advance_to(msg.ts_arrival))
            events.extend(clock.ingest(msg))
        end = clock.bound_s() if until is None else until
        if _ms(end) > clock.now_ms:
            events.extend(clock.advance_to(end))
        return events


def _ms(seconds: float) -> int:
    return round(float(seconds) * 1000)
