"""Events are the only way encounter state changes (ADR-007). `apply` is the fold step."""

from __future__ import annotations

from dataclasses import dataclass, field

from .model import ALIVE, COVER, DEAD, Encounter


@dataclass(frozen=True)
class Event:
    type: str
    data: dict = field(default_factory=dict)


def apply(enc: Encounter, ev: Event) -> None:
    d = ev.data
    c = enc.combatants.get(d.get("target") or d.get("actor") or "")
    match ev.type:
        case "encounter.started":
            enc.round, enc.pointer, enc.blackout, enc.result = 0, -1, 0, None
            for x in enc.combatants.values():
                x.death_saves, x.pinned, x.suppressed, x.taunted_by = 0, 0, False, None
                x.used, x.patched, x.actions_left = [], False, 0
        case "initiative.set":
            enc.order = list(d["order"])
        case "round.started":
            enc.round, enc.pointer = d["round"], -1
            if d["round"] > 1:
                enc.blackout = max(0, enc.blackout - 1)
        case "turn.started":
            enc.pointer = d["index"]
            c.suppressed = c.pinned > 0
            c.pinned = max(0, c.pinned - 1)
            c.actions_left = c.actions_per_turn - (1 if c.taunted_by else 0)
            c.taunted_by = None
        case "action.spent":
            c.actions_left -= 1
        case "ability.used":
            c.used.append(d["ability"])
        case "damage.applied":
            c.hp = max(0, c.hp - d["loss"])
            if d["chip"]:
                if d["location"] == "head":
                    c.sp_head = max(0, c.sp_head - 1)
                else:
                    c.sp_body = max(0, c.sp_body - 1)
        case "healed":
            c.hp = min(c.max_hp, c.hp + d["amount"])
            c.patched = True
            if "gut_shot" in c.injuries:
                c.injuries.remove("gut_shot")
        case "bled":
            c.hp = max(0, c.hp - d["amount"])
        case "injury.added":
            c.injuries.append(d["injury"])
        case "status.changed":
            c.status = d["status"]
            if d["status"] == DEAD:
                c.hp = 0
        case "death_save":
            c.death_saves += 1
        case "stabilized":
            c.status, c.hp = ALIVE, max(1, c.hp)
            if "gut_shot" in c.injuries:
                c.injuries.remove("gut_shot")
        case "medkit.used":
            c.medkits -= 1
        case "cover.changed":
            c.cover = d["cover"]
        case "pinned":
            c.pinned = max(c.pinned, 1)
        case "taunted":
            c.taunted_by = d["by"]
        case "blackout":
            enc.blackout = d["rounds"]
        case "heat.rose":
            for x in enc.combatants.values():
                x.cover = _degrade(x.cover)
                x.node_cover = _degrade(x.node_cover)
        case "encounter.ended":
            enc.result = d["result"]
        case "attack.rolled" | "check.rolled" | "initiative.rolled" | "held":
            pass
        case _:
            raise ValueError(f"unknown event type {ev.type}")


def _degrade(cover: str) -> str:
    return COVER[max(0, COVER.index(cover) - 1)]
