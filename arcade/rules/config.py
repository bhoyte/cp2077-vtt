"""Every tunable number in the ruleset (wiki/design/ruleset.md). Seasons override via TOML."""

from __future__ import annotations

import copy
import tomllib
from dataclasses import dataclass, field, fields, replace
from pathlib import Path


def _stats(**kw: int) -> dict[str, int]:
    base = dict(IRON=2, BLADE=2, GHOST=4, JACK=2, WRENCH=2, TALK=2, MEAT=5)
    base.update(kw)
    return base


def _seats() -> dict[str, dict]:
    return {
        "Solo": dict(stats=_stats(IRON=8, BLADE=6, GHOST=6, JACK=2, WRENCH=3, TALK=3, MEAT=7), signature="IRON",
                     weapon="rifle", sp_body=11, sp_head=11, medkits=0),
        "Netrunner": dict(stats=_stats(IRON=5, GHOST=6, JACK=8, WRENCH=4, TALK=4, MEAT=4), signature="JACK",
                          weapon="light_pistol", sp_body=7, sp_head=7, medkits=0),
        "Tech": dict(stats=_stats(IRON=5, GHOST=5, JACK=4, WRENCH=8, TALK=3, MEAT=6), signature="WRENCH",
                     weapon="heavy_pistol", sp_body=11, sp_head=7, medkits=2),
        "Face": dict(stats=_stats(IRON=6, GHOST=6, JACK=3, WRENCH=3, TALK=8, MEAT=5), signature="TALK",
                     weapon="heavy_pistol", sp_body=7, sp_head=7, medkits=0),
    }


def _enemies() -> dict[str, dict]:
    return {
        "Mook": dict(stats=_stats(IRON=6, GHOST=4), specialty=2, hp=15, sp=4, weapon="light_pistol", actions=1),
        "Soldier": dict(stats=_stats(IRON=8, GHOST=5), specialty=3, hp=25, sp=7, weapon="heavy_pistol", actions=1),
        "Elite": dict(stats=_stats(IRON=9, GHOST=6), specialty=4, hp=35, sp=11, weapon="rifle", actions=1),
        "Boss": dict(stats=_stats(IRON=10, GHOST=7), specialty=4, hp=60, sp=13, weapon="rifle", actions=2),
    }


@dataclass(frozen=True)
class RulesConfig:
    range_dv: dict[str, int] = field(default_factory=lambda: {"close": 12, "mid": 15, "far": 18})
    cover_bonus: dict[str, int] = field(default_factory=lambda: {"none": 0, "half": 2, "full": 4})
    weapon_skill: int = 0
    wounded_penalty: int = 2
    aimed_head_penalty: int = 6
    head_multiplier: int = 2
    crit_six_count: int = 2
    crit_bonus: int = 5
    hp_base: int = 15
    hp_per_meat: int = 5
    specialty: int = 2
    death_save_offset: int = 1
    stabilize_dv: int = 13
    medkit_bonus: int = 2
    patch_dv: int = 12
    patch_dice: int = 2
    suppress_dv: int = 15
    pinned_penalty: int = 2
    blackout_dv: int = 13
    blackout_penalty: int = 2
    blackout_rounds: int = 2
    short_dv: int = 15
    short_dice: int = 2
    overclock_penalty: int = 2
    lock_on_bonus: int = 4
    rampage_penalty: int = 2
    taunt_resolve: dict[str, int] = field(default_factory=lambda: {"Mook": 10, "Soldier": 12, "Elite": 14, "Boss": 16})
    solo_initiative_bonus: int = 2
    mook_flee_hp: int = 5
    max_rounds: int = 12
    heat_round: int = 7
    breather_heal_dice: int = 2
    downed_target_penalty: int = 100
    seats: dict[str, dict] = field(default_factory=_seats)
    enemies: dict[str, dict] = field(default_factory=_enemies)

    def merged(self, overrides: dict) -> RulesConfig:
        known = {f.name for f in fields(self)}
        unknown = set(overrides) - known
        if unknown:
            raise KeyError(f"unknown rules keys: {sorted(unknown)}")
        return replace(self, **{k: _deep_merge(getattr(self, k), v) for k, v in overrides.items()})


def _deep_merge(current, value):
    if isinstance(current, dict) and isinstance(value, dict):
        out = copy.deepcopy(current)
        for k, v in value.items():
            out[k] = _deep_merge(out[k], v) if k in out else v
        return out
    return value


def load(path: str | Path | None = None) -> RulesConfig:
    base = RulesConfig()
    if path is None:
        return base
    with open(path, "rb") as fh:
        return base.merged(tomllib.load(fh).get("rules", {}))
