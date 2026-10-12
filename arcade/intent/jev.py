"""Narrow Jev boundary (ADR-004, ADR-009).

The live HTTP client is not in this slice. `FakeJev` returns a fixed choice so
the show can be tested with no network and no API key. Jev only classifies;
it never generates text and it never decides a tie.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class JevChoice:
    choice: str
    confidence: float


class JevClient(Protocol):
    """One `choice` question. `request` is the ADR-004 body minus transport."""

    def choose(self, request: dict) -> JevChoice | None:
        """Return a choice, or None when the call times out or the breaker is open."""


class FakeJev:
    """Deterministic stand-in. Ignores the request and returns the configured choice."""

    def __init__(self, choice: str = "none", confidence: float = 1.0) -> None:
        self.choice = choice
        self.confidence = confidence
        self.requests: list[dict] = []

    def choose(self, request: dict) -> JevChoice:
        self.requests.append(request)
        return JevChoice(self.choice, self.confidence)
