"""Show clock (ADR-010). Pure: time is injected, no I/O, no randomness, no wall clock.

Party slot: window (viewer time, then grace L) → resolve → dice → beat.
The next party window opens when this beat starts. Enemy slots take dice + beat
and never open a window. Consecutive enemies that share a target are one volley.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from arcade.intent import Ballot, ChatMsg, JevClient, Option, VoteBook, classify

SEATS = ("Solo", "Netrunner", "Tech", "Face")
_PHASES = ("resolve", "dice", "beat")


def _ms(seconds: float) -> int:
    return round(float(seconds) * 1000)


def _sec(ms: int) -> float:
    return ms / 1000


@dataclass(frozen=True)
class ClockConfig:
    """Defaults are the ADR-010 / show-clock numbers. `quorum` is N, which the ADR leaves unnamed."""

    window_s: float = 12.0
    grace_s: float = 3.0
    extend_after_s: float = 6.0
    extend_by_s: float = 3.0
    min_window_s: float = 6.0
    quorum: int = 3
    lock_share: float = 0.60
    lock_stable_s: float = 3.0
    resolve_s: float = 0.3
    party_dice_s: float = 2.0
    party_beat_s: float = 4.0
    enemy_dice_s: float = 1.5
    enemy_beat_s: float = 3.0
    theta: float = 0.6

    def __post_init__(self) -> None:
        if self.window_s < self.min_window_s:
            raise ValueError("viewer window is shorter than the 6 s minimum")
        if self.grace_s < 0 or self.quorum < 1:
            raise ValueError("grace must be >= 0 and quorum at least 1")
        if not 0 < self.lock_share <= 1:
            raise ValueError("lock share must be in (0, 1]")
        if not 0 <= self.theta <= 1:
            raise ValueError("theta must be in [0, 1]")
        for name in (
            "extend_after_s",
            "extend_by_s",
            "lock_stable_s",
            "resolve_s",
            "party_dice_s",
            "party_beat_s",
            "enemy_dice_s",
            "enemy_beat_s",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")
        seconds = {
            "window_ms": self.window_s,
            "grace_ms": self.grace_s,
            "extend_after_ms": self.extend_after_s,
            "extend_by_ms": self.extend_by_s,
            "lock_stable_ms": self.lock_stable_s,
            "resolve_ms": self.resolve_s,
            "party_dice_ms": self.party_dice_s,
            "party_beat_ms": self.party_beat_s,
            "enemy_dice_ms": self.enemy_dice_s,
            "enemy_beat_ms": self.enemy_beat_s,
        }
        for key, value in seconds.items():
            object.__setattr__(self, key, _ms(value))
        object.__setattr__(self, "lock_percent", round(self.lock_share * 100))


@dataclass(frozen=True)
class Slot:
    """One initiative entry. `kind` is ``party`` or ``enemy``; volleys are built by the clock."""

    id: str
    kind: str
    seat: str | None = None
    options: tuple[Option, ...] = ()
    target: str | None = None
    open_seat: bool = False
    members: tuple[str, ...] = ()


@dataclass(frozen=True)
class ShowEvent:
    t: float
    type: str
    data: dict = field(default_factory=dict)


@dataclass
class _Run:
    slot: Slot
    phase: str = "pending"
    open_ms: int | None = None
    viewer_close_ms: int | None = None
    server_close_ms: int | None = None
    extended: bool = False
    extend_checked: bool = False
    lock_since_ms: int | None = None
    lock_leader: str | None = None
    phase_until_ms: int | None = None


class ShowClock:
    """Simulated-time phase machine. Call `start`, then `advance_to` / `ingest`."""

    def __init__(
        self,
        slots: Sequence[Slot],
        *,
        config: ClockConfig | None = None,
        jev: JevClient | None = None,
        emotes: Mapping[str, str] | None = None,
        situation: str = "",
        t0: float = 0.0,
    ) -> None:
        self.config = config or ClockConfig()
        self.runs = [_Run(slot) for slot in _plan(slots)]
        self.book = VoteBook()
        self.jev = jev
        self.emotes = dict(emotes or {})
        self.situation = situation
        self.t0_ms = _ms(t0)
        self.now_ms = self.t0_ms
        self.log: list[ShowEvent] = []
        self.started = False

    @property
    def t(self) -> float:
        return _sec(self.now_ms)

    def start(self) -> list[ShowEvent]:
        if self.started:
            raise RuntimeError("clock already started")
        self.started = True
        first = self.runs[0]
        if first.slot.kind == "party":
            return self._open(first)
        return self._begin_enemy(first)

    def advance_to(self, t: float) -> list[ShowEvent]:
        """Move simulated time forward, applying every deadline up to and including `t`.

        The +3 s quorum check is the exception: it waits until time moves *past*
        ``open + 6 s``, so a ballot timestamped on that instant still counts.
        """

        if not self.started:
            raise RuntimeError("start the clock before advancing")
        target = _ms(t)
        if target < self.now_ms:
            raise ValueError("simulated time only moves forward")
        events: list[ShowEvent] = []
        for _ in range(100_000):
            if self.now_ms >= target:
                return events
            step = self._next(target)
            if step is None:
                self.now_ms = target
                return events
            at, kinds = step
            self.now_ms = at
            events.extend(self._apply(kinds))
        raise RuntimeError("show clock did not reach the requested time")

    def ingest(self, msg: ChatMsg) -> list[ShowEvent]:
        """Classify one message at the clock's current time. Advance here first."""

        if not self.started:
            raise RuntimeError("start the clock before ingest")
        if not msg.user_id:
            raise ValueError("user_id is required")
        if _ms(msg.ts_arrival) != self.now_ms:
            raise ValueError("advance the clock to ts_arrival before ingest")
        run = self._window()
        if run is None or run.slot.kind != "party":
            return []
        if not run.slot.open_seat and msg.seat != run.slot.seat:
            return []
        hit = classify(
            msg.text,
            run.slot.options,
            emotes=self.emotes,
            jev=self.jev,
            situation=self.situation,
            theta=self.config.theta,
        )
        if hit is None:
            return []
        self.book.cast(
            run.slot.id,
            Ballot(msg.user_id, hit.option, msg.ts_arrival, hit.layer, hit.conf),
        )
        event = self._emit(
            "vote.cast",
            {
                "user": msg.user_id,
                "option": hit.option,
                "layer": hit.layer,
                "conf": hit.conf,
                "slot": run.slot.id,
            },
        )
        self._refresh_lock(run)
        return [event]

    def bound_s(self) -> float:
        """A time by which every slot has finished, even with the +3 s extension."""

        cfg = self.config
        party = (
            cfg.window_s
            + cfg.grace_s
            + cfg.extend_by_s
            + cfg.resolve_s
            + cfg.party_dice_s
            + cfg.party_beat_s
        )
        enemy = cfg.enemy_dice_s + cfg.enemy_beat_s
        return _sec(self.t0_ms) + max(party, enemy) * len(self.runs) + 1

    def _next(self, target: int) -> tuple[int, frozenset[str]] | None:
        hits: dict[int, set[str]] = {}

        def add(at: int | None, kind: str) -> None:
            if at is None:
                return
            if kind == "extend":
                # Parking exactly on the checkpoint lets `ingest` record a ballot
                # timestamped there. If the window is also closing, decide first.
                if at == target and not self._deadline_at(target, "close", "lock"):
                    return
                leaving = at == self.now_ms and self.now_ms < target
                passing = self.now_ms < at < target or (at == target and self._deadline_at(target, "close", "lock"))
                if not (leaving or passing):
                    return
            elif not (self.now_ms < at <= target):
                return
            hits.setdefault(at, set()).add(kind)

        for run in self.runs:
            if run.phase == "window" and run.open_ms is not None:
                if not run.extend_checked:
                    add(run.open_ms + self.config.extend_after_ms, "extend")
                if run.lock_since_ms is not None:
                    add(run.lock_since_ms + self.config.lock_stable_ms, "lock")
                add(run.server_close_ms, "close")
            elif run.phase in _PHASES:
                add(run.phase_until_ms, "phase")
        if not hits:
            return None
        at = min(hits)
        return at, frozenset(hits[at])

    def _deadline_at(self, at: int, *kinds: str) -> bool:
        for run in self.runs:
            if run.phase != "window":
                continue
            if "close" in kinds and run.server_close_ms == at:
                return True
            if (
                "lock" in kinds
                and run.lock_since_ms is not None
                and run.lock_since_ms + self.config.lock_stable_ms == at
            ):
                return True
        return False

    def _apply(self, kinds: frozenset[str]) -> list[ShowEvent]:
        events: list[ShowEvent] = []
        if "extend" in kinds:
            for run in self._windows():
                if not run.extend_checked and run.open_ms is not None:
                    if run.open_ms + self.config.extend_after_ms == self.now_ms:
                        events.extend(self._check_extend(run))
        if "lock" in kinds:
            for run in self._windows():
                due = run.lock_since_ms is not None and (
                    run.lock_since_ms + self.config.lock_stable_ms == self.now_ms
                )
                if due:
                    events.extend(self._close(run, "locked_in"))
        if "close" in kinds:
            for run in self._windows():
                if run.server_close_ms == self.now_ms:
                    events.extend(self._close(run, "timer"))
        if "phase" in kinds:
            for run in list(self.runs):
                if run.phase in _PHASES and run.phase_until_ms == self.now_ms:
                    events.extend(self._advance_phase(run))
        return events

    def _check_extend(self, run: _Run) -> list[ShowEvent]:
        run.extend_checked = True
        if self.book.total(run.slot.id) >= self.config.quorum:
            return []
        assert run.viewer_close_ms is not None and run.server_close_ms is not None
        run.viewer_close_ms += self.config.extend_by_ms
        run.server_close_ms += self.config.extend_by_ms
        run.extended = True
        return [
            self._emit(
                "window.extended",
                {
                    "slot": run.slot.id,
                    "viewer_close_at": _sec(run.viewer_close_ms),
                    "server_close_at": _sec(run.server_close_ms),
                },
            )
        ]

    def _refresh_lock(self, run: _Run) -> None:
        leader, votes, total = self.book.leader(run.slot.id)
        holds = (
            leader is not None
            and total >= self.config.quorum
            and votes * 100 >= total * self.config.lock_percent
        )
        if not holds:
            run.lock_since_ms = None
            run.lock_leader = None
            return
        if run.lock_leader != leader:
            run.lock_since_ms = self.now_ms
            run.lock_leader = leader

    def _open(self, run: _Run) -> list[ShowEvent]:
        if any(other.phase == "window" for other in self.runs):
            raise RuntimeError("two vote windows overlapped")
        run.phase = "window"
        run.open_ms = self.now_ms
        run.viewer_close_ms = self.now_ms + self.config.window_ms
        run.server_close_ms = run.viewer_close_ms + self.config.grace_ms
        return [
            self._emit(
                "window.opened",
                {
                    "slot": run.slot.id,
                    "seat": run.slot.seat,
                    "options": [{"id": opt.id, "label": opt.label} for opt in run.slot.options],
                    "viewer_close_at": _sec(run.viewer_close_ms),
                    "server_close_at": _sec(run.server_close_ms),
                    "open_seat": run.slot.open_seat,
                },
            )
        ]

    def _close(self, run: _Run, reason: str) -> list[ShowEvent]:
        tally = {opt.id: 0 for opt in run.slot.options}
        tally.update(self.book.tally(run.slot.id))
        winner, _votes, total = self.book.leader(run.slot.id)
        run.phase = "resolve"
        run.phase_until_ms = self.now_ms + self.config.resolve_ms
        run.lock_since_ms = None
        run.lock_leader = None
        return [
            self._emit(
                "window.closed",
                {
                    "slot": run.slot.id,
                    "tally": tally,
                    "winner": winner,
                    "tied": total > 0 and winner is None,
                    "reason": reason,
                },
            ),
            self._emit("phase.started", self._phase_data(run)),
        ]

    def _advance_phase(self, run: _Run) -> list[ShowEvent]:
        if run.phase == "resolve":
            run.phase = "dice"
            run.phase_until_ms = self.now_ms + self._dice_ms(run)
            return [self._emit("phase.started", self._phase_data(run))]
        if run.phase == "dice":
            run.phase = "beat"
            run.phase_until_ms = self.now_ms + self._beat_ms(run)
            events = [self._emit("phase.started", self._phase_data(run))]
            events.extend(self._pipeline(run))
            return events
        run.phase = "done"
        run.phase_until_ms = None
        events = [self._emit("slot.done", {"slot": run.slot.id})]
        events.extend(self._start_following_enemy(run))
        return events

    def _pipeline(self, run: _Run) -> list[ShowEvent]:
        nxt = self._after(run)
        if nxt is not None and nxt.phase == "pending" and nxt.slot.kind == "party":
            return self._open(nxt)
        return []

    def _start_following_enemy(self, run: _Run) -> list[ShowEvent]:
        nxt = self._after(run)
        if nxt is not None and nxt.phase == "pending" and nxt.slot.kind != "party":
            return self._begin_enemy(nxt)
        return []

    def _begin_enemy(self, run: _Run) -> list[ShowEvent]:
        run.phase = "dice"
        run.phase_until_ms = self.now_ms + self.config.enemy_dice_ms
        return [self._emit("phase.started", self._phase_data(run))]

    def _after(self, run: _Run) -> _Run | None:
        index = self.runs.index(run)
        if index + 1 < len(self.runs):
            return self.runs[index + 1]
        return None

    def _window(self) -> _Run | None:
        open_runs = [run for run in self.runs if run.phase == "window"]
        return open_runs[0] if open_runs else None

    def _windows(self) -> list[_Run]:
        return [run for run in self.runs if run.phase == "window"]

    def _dice_ms(self, run: _Run) -> int:
        if run.slot.kind == "party":
            return self.config.party_dice_ms
        return self.config.enemy_dice_ms

    def _beat_ms(self, run: _Run) -> int:
        if run.slot.kind == "party":
            return self.config.party_beat_ms
        return self.config.enemy_beat_ms

    def _phase_data(self, run: _Run) -> dict:
        data: dict = {"slot": run.slot.id, "phase": run.phase, "kind": run.slot.kind}
        if run.slot.members:
            data["members"] = list(run.slot.members)
        if run.slot.target:
            data["target"] = run.slot.target
        return data

    def _emit(self, type_: str, data: dict) -> ShowEvent:
        event = ShowEvent(_sec(self.now_ms), type_, dict(data))
        self.log.append(event)
        return event


def _plan(slots: Sequence[Slot]) -> list[Slot]:
    if not slots:
        raise ValueError("show needs at least one slot")
    seen: set[str] = set()
    for slot in slots:
        if not slot.id or slot.id in seen:
            raise ValueError(f"duplicate or empty slot id {slot.id!r}")
        seen.add(slot.id)
        _validate(slot)
    merged: list[Slot] = []
    index = 0
    pending = list(slots)
    while index < len(pending):
        slot = pending[index]
        if slot.kind == "enemy" and slot.target:
            group = [slot]
            nxt = index + 1
            while (
                nxt < len(pending)
                and pending[nxt].kind == "enemy"
                and pending[nxt].target == slot.target
            ):
                group.append(pending[nxt])
                nxt += 1
            if len(group) > 1:
                merged.append(
                    Slot(
                        id="+".join(member.id for member in group),
                        kind="volley",
                        target=slot.target,
                        members=tuple(member.id for member in group),
                    )
                )
                index = nxt
                continue
        merged.append(slot)
        index += 1
    return merged


def _validate(slot: Slot) -> None:
    if slot.kind not in {"party", "enemy"}:
        raise ValueError(f"unknown slot kind {slot.kind}")
    if slot.kind != "party":
        return
    if slot.seat not in SEATS:
        raise ValueError(f"party slot {slot.id} needs a seat")
    if not 1 <= len(slot.options) <= 4:
        raise ValueError(f"party slot {slot.id} needs 1–4 options")
    ids = [opt.id for opt in slot.options]
    if len(ids) != len(set(ids)) or any(opt_id not in {"1", "2", "3", "4"} for opt_id in ids):
        raise ValueError(f"party slot {slot.id} options must be unique ids 1–4")
