"""Crowd policy: what a plurality vote of a distracted audience plausibly picks. Not authoritative."""

from __future__ import annotations

import random

from ..rules.model import ALIVE, Action, Encounter


def heuristic(enc: Encounter, a: Action) -> float:
    c = enc.combatants[a.actor]
    t = enc.combatants.get(a.target) if a.target else None
    allies_wounded = sum(1 for p in enc.side("party") if p.status == ALIVE and p.wounded)
    threat = {"Mook": 0, "Soldier": 1, "Elite": 2, "Boss": 3}.get(t.role, 0) if t is not None else 0
    match a.kind:
        case "attack":
            return 5 + (2 if t.wounded else 0) + (1 if t.cover == "none" else 0) - 0.3 * threat
        case "aimed_shot":
            return 2 + threat * 0.5
        case "suppress":
            return 2.5 + threat * 0.5
        case "take_cover":
            return 6.5 if c.cover == "none" else 3
        case "overclock":
            return 7 + threat
        case "blackout":
            return 8 if enc.round <= 2 else 5
        case "short_circuit":
            return 6 + threat
        case "stabilize":
            return 12
        case "patch":
            missing = (t.max_hp - t.hp) / t.max_hp
            return 2 + 8 * missing
        case "deploy_cover":
            return 4 + (3 if t.wounded else 0) + (1 if t.cover == "none" else 0)
        case "taunt":
            return 3 + 1.5 * threat + allies_wounded
        case "hold":
            return -5
    return 1


class CrowdPolicy:
    def __init__(self, rng: random.Random, chaos: float = 0.15, noise: float = 1.5) -> None:
        self.rng, self.chaos, self.noise = rng, chaos, noise

    def __call__(self, enc: Encounter, options: list[Action]) -> Action:
        if self.rng.random() < self.chaos:
            return self.rng.choice(options)
        return max(options, key=lambda a: heuristic(enc, a) + self.rng.gauss(0, self.noise))
