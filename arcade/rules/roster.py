"""Build combatants from the seat and enemy templates in RulesConfig."""

from __future__ import annotations

from .config import RulesConfig
from .model import SEATS, Combatant


def seat(role: str, cfg: RulesConfig, cid: str | None = None, name: str | None = None) -> Combatant:
    t = cfg.seats[role]
    hp = cfg.hp_base + cfg.hp_per_meat * t["stats"]["MEAT"]
    return Combatant(
        id=cid or role.lower(), name=name or role, side="party", role=role, stats=dict(t["stats"]),
        signature=t["signature"], specialty=cfg.specialty, max_hp=hp, hp=hp, sp_body=t["sp_body"],
        sp_head=t["sp_head"], weapon=t["weapon"], medkits=t["medkits"],
    )


def enemy(tier: str, cid: str, cfg: RulesConfig, name: str | None = None) -> Combatant:
    t = cfg.enemies[tier]
    return Combatant(
        id=cid, name=name or cid, side="enemy", role=tier, stats=dict(t["stats"]), signature="IRON",
        specialty=t["specialty"], max_hp=t["hp"], hp=t["hp"], sp_body=t["sp"], sp_head=t["sp"],
        weapon=t["weapon"], actions_per_turn=t["actions"],
    )


def party(cfg: RulesConfig) -> list[Combatant]:
    return [seat(role, cfg) for role in SEATS]
