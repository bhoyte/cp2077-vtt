"""Deterministic rules core: pure state + events, randomness only from arcade.dice."""

from .config import RulesConfig, load
from .engine import Engine, IllegalAction
from .events import Event, apply
from .model import ALIVE, DEAD, FLATLINING, FLED, Action, Combatant, Encounter
from .roster import enemy, party, seat

__all__ = [
    "ALIVE", "DEAD", "FLATLINING", "FLED", "Action", "Combatant", "Encounter", "Engine", "Event",
    "IllegalAction", "RulesConfig", "apply", "enemy", "load", "party", "seat",
]
