"""Enemy decision policy: utility scoring, provable d6 tie-break among near-best options."""

from __future__ import annotations

from .config import RulesConfig
from .engine import Engine
from .model import ALIVE, FLATLINING, Action, Encounter

NEAR_BEST = 2


def score(enc: Encounter, action: Action, cfg: RulesConfig) -> int:
    c = enc.combatants[action.actor]
    if action.kind == "hold":
        return -50
    if action.kind == "take_cover":
        return 11 if c.cover == "none" else 4
    if action.kind == "rampage":
        return 6 + 4 * sum(1 for p in enc.side("party") if p.status == ALIVE)
    t = enc.combatants[action.target]
    s = 10
    if t.status == FLATLINING:
        s -= cfg.downed_target_penalty
    if t.wounded:
        s += 3
    s += {"none": 2, "half": 0, "full": -3}[t.cover]
    if action.kind == "lock_on":
        s += 3
    return s


def choose(engine: Engine, enc: Encounter, actor: str) -> Action:
    options = engine.legal_actions(enc, actor)
    scored = sorted(((score(enc, a, engine.cfg), str(a), a) for a in options), key=lambda x: (-x[0], x[1]))
    top = [a for s, _, a in scored if s >= scored[0][0] - NEAR_BEST]
    if len(top) == 1:
        return top[0]
    pick = engine.dice.d6(f"r{enc.round}:{actor}:ai")
    return top[(pick - 1) % len(top)]
