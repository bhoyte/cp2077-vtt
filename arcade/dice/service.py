"""Provably fair dice (ADR-006).

Draw i = HMAC-SHA256(seed, session_id ␟ i ␟ purpose ␟ attempt), mapped to a die face by rejection
sampling over 32-bit words, so every face is exactly equally likely. Publishing SHA-256(seed) before the
show and the seed after it lets anyone recompute every roll with `verify_log`.
"""

from __future__ import annotations

import hashlib
import hmac
import random
import secrets
from dataclasses import asdict, dataclass

SEP = "\x1f"
WORD = 1 << 32


@dataclass(frozen=True)
class Roll:
    index: int
    purpose: str
    faces: int
    value: int


def commit_of(seed: bytes) -> str:
    return hashlib.sha256(seed).hexdigest()


def derive(seed: bytes, session_id: str, index: int, purpose: str, faces: int) -> int:
    limit = WORD - (WORD % faces)
    attempt = 0
    while True:
        message = SEP.join((session_id, str(index), purpose, str(attempt))).encode()
        digest = hmac.digest(seed, message, "sha256")
        for offset in range(0, len(digest), 4):
            word = int.from_bytes(digest[offset : offset + 4], "big")
            if word < limit:
                return word % faces + 1
        attempt += 1


class Dice:
    """Authoritative dice. The only source of randomness the rules core may use."""

    def __init__(self, seed: bytes | None = None, session_id: str = "dev") -> None:
        self.seed = secrets.token_bytes(32) if seed is None else seed
        if len(self.seed) < 16:
            raise ValueError("seed must be at least 16 bytes")
        self.session_id = session_id
        self.log: list[Roll] = []

    @property
    def commit(self) -> str:
        return commit_of(self.seed)

    def roll(self, faces: int, purpose: str) -> int:
        if faces < 2:
            raise ValueError("a die needs at least 2 faces")
        if SEP in purpose:
            raise ValueError("purpose may not contain the separator character")
        index = len(self.log)
        value = derive(self.seed, self.session_id, index, purpose, faces)
        self.log.append(Roll(index, purpose, faces, value))
        return value

    def d10(self, purpose: str) -> int:
        return self.roll(10, purpose)

    def d6(self, purpose: str) -> int:
        return self.roll(6, purpose)

    def export(self) -> dict:
        return {"session_id": self.session_id, "commit": self.commit, "rolls": [asdict(r) for r in self.log]}


class FastDice(Dice):
    """Same interface, Mersenne Twister underneath. Simulation only; never on air."""

    def __init__(self, seed: int = 0, session_id: str = "sim", keep_log: bool = False) -> None:
        self.seed = seed.to_bytes(16, "big")
        self.session_id = session_id
        self.log = []
        self._rng = random.Random(seed)
        self._keep_log = keep_log

    def roll(self, faces: int, purpose: str) -> int:
        value = self._rng.randint(1, faces)
        if self._keep_log:
            self.log.append(Roll(len(self.log), purpose, faces, value))
        return value


def verify_log(seed_hex: str, exported: dict) -> list[str]:
    """Return a list of problems; empty means every roll and the commitment check out."""
    problems: list[str] = []
    seed = bytes.fromhex(seed_hex)
    if commit_of(seed) != exported["commit"]:
        problems.append("commitment does not match the revealed seed")
    for expected_index, roll in enumerate(exported["rolls"]):
        if roll["index"] != expected_index:
            problems.append(f"roll index gap at position {expected_index}")
            continue
        value = derive(seed, exported["session_id"], roll["index"], roll["purpose"], roll["faces"])
        if value != roll["value"]:
            problems.append(f"roll #{roll['index']} ({roll['purpose']}): logged {roll['value']}, derived {value}")
    return problems
