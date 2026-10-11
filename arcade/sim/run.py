"""Monte Carlo gigs against the Season 0 balance targets (wiki/design/ruleset.md)."""

from __future__ import annotations

import random
import statistics
from collections import Counter
from dataclasses import dataclass, field

from ..dice import FastDice
from ..rules import ai
from ..rules.config import RulesConfig
from ..rules.engine import Engine
from ..rules.model import ALIVE, DEAD, SEATS, Combatant, Encounter, range_key
from ..rules.roster import enemy, party
from .policy import CrowdPolicy

TARGETS = {
    "rounds_per_encounter": (4.0, 6.0),
    "p_death_per_gig": (0.25, 0.35),
    "p_wipe_per_gig": (0.0, 0.03),
    "p_stalemate_per_encounter": (0.0, 0.01),
}

OPENERS = {"street": ["Mook", "Mook", "Mook", "Soldier"], "squad": ["Soldier", "Soldier", "Mook", "Mook"]}
CLOSERS = {"elite": ["Elite", "Soldier", "Soldier"], "boss": ["Boss", "Mook", "Mook"]}
RANGES = (("close", 0.25), ("mid", 0.55), ("far", 0.20))
COVERS = (("none", 0.2), ("half", 0.5), ("full", 0.3))


@dataclass
class GigResult:
    shape: str
    deaths: int
    wiped: bool
    rounds: list[int]
    results: list[str]
    damage_by: Counter = field(default_factory=Counter)
    actions: Counter = field(default_factory=Counter)


def _pick(rng: random.Random, table) -> str:
    names, weights = zip(*table)
    return rng.choices(names, weights)[0]


def build_encounter(eid: str, crew: list[Combatant], tiers: list[str], rng: random.Random, cfg: RulesConfig) -> Encounter:
    foes = []
    for i, tier in enumerate(tiers):
        foe = enemy(tier, f"{tier.lower()}{i}", cfg)
        foe.node_cover = _pick(rng, COVERS)
        foe.cover = foe.node_cover
        foes.append(foe)
    for p in crew:
        p.node_cover, p.cover = _pick(rng, COVERS), "none"
    ranges = {range_key(p.id, f.id): _pick(rng, RANGES) for p in crew for f in foes}
    return Encounter(eid, {c.id: c for c in [*crew, *foes]}, ranges)


def play_gig(cfg: RulesConfig, seed: int, crowd_chaos: float = 0.15, idle_seat: str | None = None,
             idle_mode: str = "hold") -> GigResult:
    rng = random.Random(seed ^ 0x5EED)
    dice = FastDice(seed)
    crew = party(cfg)
    opener, closer = rng.choice(list(OPENERS)), rng.choice(list(CLOSERS))
    crowd = CrowdPolicy(rng, chaos=crowd_chaos)
    out = GigResult(f"{opener}+{closer}", 0, False, [], [])
    for n, tiers in enumerate((OPENERS[opener], CLOSERS[closer])):
        if not any(p.status == ALIVE for p in crew):
            break
        enc = build_encounter(f"gig{seed}:e{n}", crew, tiers, rng, cfg)
        engine = Engine(cfg, dice)
        if n > 0:
            engine.breather(enc)
        engine.start(enc)
        while (actor := engine.advance(enc)) is not None:
            c = enc.combatants[actor]
            while options := engine.legal_actions(enc, actor):
                if c.side == "enemy":
                    action = ai.choose(engine, enc, actor)
                elif c.role == idle_seat:
                    action = options[-1] if idle_mode == "hold" else rng.choice(options)
                else:
                    action = crowd(enc, options)
                    out.actions[f"{c.role}:{action.kind}"] += 1
                engine.resolve(enc, action)
        for ev in engine.events:
            if ev.type == "damage.applied" and enc.combatants[ev.data["target"]].side == "enemy":
                out.damage_by[enc.combatants[ev.data["source"]].role] += ev.data["loss"]
        out.rounds.append(enc.round)
        out.results.append(enc.result)
        if enc.result == "wipe":
            out.wiped = True
            break
    out.deaths = sum(1 for p in crew if p.status == DEAD)
    return out


def summarize(results: list[GigResult]) -> dict:
    rounds = [r for g in results for r in g.rounds]
    party_damage = Counter()
    actions = Counter()
    for g in results:
        party_damage.update({k: v for k, v in g.damage_by.items() if k in ("Solo", "Netrunner", "Tech", "Face")})
        actions.update(g.actions)
    total_dmg = sum(party_damage.values()) or 1
    by_shape: dict[str, list[GigResult]] = {}
    for g in results:
        by_shape.setdefault(g.shape, []).append(g)
    return {
        "gigs": len(results),
        "rounds_per_encounter": statistics.mean(rounds),
        "rounds_p90": sorted(rounds)[int(0.9 * (len(rounds) - 1))],
        "p_death_per_gig": sum(g.deaths > 0 for g in results) / len(results),
        "p_wipe_per_gig": sum(g.wiped for g in results) / len(results),
        "mean_deaths": statistics.mean(g.deaths for g in results),
        "p_stalemate_per_encounter": sum(r == "stalemate" for g in results for r in g.results) / len(rounds),
        "loss": loss(results),
        "damage_share": {k: party_damage[k] / total_dmg for k in ("Solo", "Netrunner", "Tech", "Face")},
        "by_shape": {s: {"n": len(gs), "p_death": sum(g.deaths > 0 for g in gs) / len(gs),
                         "p_wipe": sum(g.wiped for g in gs) / len(gs),
                         "rounds": statistics.mean(r for g in gs for r in g.rounds)} for s, gs in sorted(by_shape.items())},
        "top_actions": actions.most_common(16),
    }


def loss(results: list[GigResult]) -> float:
    """Mean party cost per gig: deaths, plus a wipe counted as two extra deaths."""
    return statistics.mean(g.deaths + 2 * g.wiped for g in results)


def run(cfg: RulesConfig, gigs: int, seed: int, crowd_chaos: float = 0.15, ablate: bool = False) -> dict:
    seeds = [seed * 1_000_003 + i for i in range(gigs)]
    summary = summarize([play_gig(cfg, s, crowd_chaos) for s in seeds])
    if ablate:
        for mode, key in (("hold", "idle"), ("random", "random")):
            deltas = {}
            for role in SEATS:
                ablated = loss([play_gig(cfg, s, crowd_chaos, idle_seat=role, idle_mode=mode) for s in seeds])
                deltas[role] = max(0.0, ablated - summary["loss"])
            total = sum(deltas.values()) or 1.0
            summary[f"seat_loss_if_{key}"] = deltas
            summary[f"seat_{key}_share"] = {k: v / total for k, v in deltas.items()}
    return summary


def verdict(summary: dict) -> list[str]:
    lines = []
    for key, (lo, hi) in TARGETS.items():
        value = summary[key]
        lines.append(f"{'PASS' if lo <= value <= hi else 'MISS'} {key} = {value:.3f} (target {lo}-{hi})")
    return lines
