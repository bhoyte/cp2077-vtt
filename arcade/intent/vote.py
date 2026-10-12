"""Per-window vote book (ADR-004). One ballot per account; the latest cast wins."""

from __future__ import annotations

from .model import Ballot


class VoteBook:
    def __init__(self) -> None:
        self._ballots: dict[str, dict[str, Ballot]] = {}

    def cast(self, window_id: str, ballot: Ballot) -> Ballot:
        self._ballots.setdefault(window_id, {})[ballot.user_id] = ballot
        return ballot

    def ballots(self, window_id: str) -> tuple[Ballot, ...]:
        return tuple(self._ballots.get(window_id, {}).values())

    def tally(self, window_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for ballot in self.ballots(window_id):
            counts[ballot.option] = counts.get(ballot.option, 0) + 1
        return counts

    def total(self, window_id: str) -> int:
        return len(self._ballots.get(window_id, {}))

    def leader(self, window_id: str) -> tuple[str | None, int, int]:
        """`(option, votes_for_option, total)`. `option` is None on an empty book or a tie."""

        tally = self.tally(window_id)
        total = sum(tally.values())
        if total == 0:
            return None, 0, 0
        best = max(tally.values())
        leaders = [opt for opt, count in tally.items() if count == best]
        if len(leaders) != 1:
            return None, best, total
        return leaders[0], best, total
