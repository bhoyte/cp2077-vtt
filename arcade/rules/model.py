from __future__ import annotations

from dataclasses import dataclass, field

STATS = ("IRON", "BLADE", "GHOST", "JACK", "WRENCH", "TALK", "MEAT")
SEATS = ("Solo", "Netrunner", "Tech", "Face")
TIERS = ("Mook", "Soldier", "Elite", "Boss")

ALIVE, FLATLINING, DEAD, FLED = "ALIVE", "FLATLINING", "DEAD", "FLED"
COVER = ("none", "half", "full")


@dataclass(frozen=True)
class Weapon:
    name: str
    dice: int
    close_only: bool = False


WEAPONS = {
    "light_pistol": Weapon("light_pistol", 2),
    "heavy_pistol": Weapon("heavy_pistol", 3),
    "rifle": Weapon("rifle", 4),
    "shotgun": Weapon("shotgun", 5, close_only=True),
}

# d6 → (injury, stat penalties ("*" = all checks), HP bleed at the start of each own turn until patched)
INJURIES: dict[int, tuple[str, dict[str, int], int]] = {
    1: ("glass_eye", {"IRON": -2}, 0),
    2: ("cracked_ribs", {"*": -1}, 0),
    3: ("burned_hand", {"IRON": -1, "BLADE": -2}, 0),
    4: ("concussion", {"JACK": -2, "TALK": -2}, 0),
    5: ("shrapnel_leg", {"GHOST": -2}, 0),
    6: ("gut_shot", {}, 2),
}
INJURY_BY_NAME = {name: (penalties, bleed) for name, penalties, bleed in INJURIES.values()}


@dataclass
class Combatant:
    id: str
    name: str
    side: str
    role: str
    stats: dict[str, int]
    signature: str
    specialty: int
    max_hp: int
    hp: int
    sp_body: int
    sp_head: int
    weapon: str
    node_cover: str = "half"
    cover: str = "none"
    status: str = ALIVE
    death_saves: int = 0
    pinned: int = 0
    suppressed: bool = False
    taunted_by: str | None = None
    injuries: list[str] = field(default_factory=list)
    used: list[str] = field(default_factory=list)
    patched: bool = False
    medkits: int = 0
    actions_per_turn: int = 1
    actions_left: int = 0
    temperament: str = "steady"

    @property
    def wounded(self) -> bool:
        return self.hp <= self.max_hp // 2

    def stat(self, name: str) -> int:
        value = self.stats.get(name, 0)
        for injury in self.injuries:
            penalties, _ = INJURY_BY_NAME[injury]
            value += penalties.get(name, 0) + penalties.get("*", 0)
        return value

    @property
    def bleed(self) -> int:
        return sum(INJURY_BY_NAME[i][1] for i in self.injuries)


@dataclass(frozen=True)
class Action:
    kind: str
    actor: str
    target: str | None = None

    def __str__(self) -> str:
        return f"{self.kind}->{self.target}" if self.target else self.kind


@dataclass
class Encounter:
    id: str
    combatants: dict[str, Combatant]
    ranges: dict[str, str] = field(default_factory=dict)
    default_range: str = "mid"
    order: list[str] = field(default_factory=list)
    round: int = 0
    pointer: int = -1
    blackout: int = 0
    result: str | None = None

    def range_between(self, a: str, b: str) -> str:
        return self.ranges.get(range_key(a, b), self.default_range)

    def side(self, side: str) -> list[Combatant]:
        return [c for c in self.combatants.values() if c.side == side]

    def current(self) -> Combatant | None:
        if 0 <= self.pointer < len(self.order):
            return self.combatants[self.order[self.pointer]]
        return None


def range_key(a: str, b: str) -> str:
    return "|".join(sorted((a, b)))
