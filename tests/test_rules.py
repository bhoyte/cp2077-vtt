import copy
from dataclasses import asdict
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from arcade.dice import Dice
from arcade.rules import ALIVE, DEAD, FLATLINING, Action, Encounter, Engine, IllegalAction, RulesConfig, apply, load
from arcade.rules import ai, enemy, party
from arcade.rules.events import Event
from arcade.rules.model import range_key

ROOT = Path(__file__).resolve().parents[1]
CFG = load(ROOT / "content/rules/season0.toml")


class ScriptedDice(Dice):
    """Returns queued values; falls back to 5 so tests only script the rolls they care about."""

    def __init__(self, values=()):
        super().__init__(bytes(32), "test")
        self.queue = list(values)

    def roll(self, faces, purpose):
        value = self.queue.pop(0) if self.queue else 5
        assert 1 <= value <= faces, (purpose, value, faces)
        return value


def make_encounter(cfg=CFG, tiers=("Soldier", "Mook", "Mook"), rng_range="mid"):
    crew = party(cfg)
    foes = [enemy(t, f"{t.lower()}{i}", cfg) for i, t in enumerate(tiers)]
    for f in foes:
        f.node_cover = f.cover = "half"
    ranges = {range_key(p.id, f.id): rng_range for p in crew for f in foes}
    return Encounter("t", {c.id: c for c in [*crew, *foes]}, ranges)


def play(engine, enc, party_choice=lambda opts: opts[0]):
    engine.start(enc)
    while (actor := engine.advance(enc)) is not None:
        while opts := engine.legal_actions(enc, actor):
            c = enc.combatants[actor]
            engine.resolve(enc, ai.choose(engine, enc, actor) if c.side == "enemy" else party_choice(opts))
    return enc


def snapshot(enc):
    return asdict(enc)


def test_replay_reproduces_final_state():
    initial = make_encounter(tiers=("Elite", "Soldier", "Mook"))
    pristine = copy.deepcopy(initial)
    engine = Engine(CFG, Dice(bytes(range(32)), "replay"))
    final = play(engine, initial)
    assert final.result in {"victory", "wipe", "stalemate"}
    for ev in engine.events:
        apply(pristine, ev)
    assert snapshot(pristine) == snapshot(final)


def test_same_seed_same_events():
    runs = []
    for _ in range(2):
        engine = Engine(CFG, Dice(bytes(range(32)), "det"))
        play(engine, make_encounter())
        runs.append(engine.events)
    assert runs[0] == runs[1]


def test_illegal_action_rejected():
    enc = make_encounter()
    engine = Engine(CFG, ScriptedDice())
    engine.start(enc)
    actor = engine.advance(enc)
    other = next(c.id for c in enc.combatants.values() if c.id != actor)
    with pytest.raises(IllegalAction):
        engine.resolve(enc, Action("attack", other, actor))
    with pytest.raises(IllegalAction):
        engine.resolve(enc, Action("teleport", actor))


def _armor_case(raw_dice):
    enc = make_encounter(tiers=("Elite",))
    solo, elite = enc.combatants["solo"], enc.combatants["elite0"]
    engine = Engine(CFG, ScriptedDice([*raw_dice]))
    engine._damage(enc, solo, elite, len(raw_dice), "body", "t")
    return elite


def test_damage_at_or_below_sp_does_nothing():
    elite = _armor_case([1, 2, 3])  # 6 == SP 6
    assert (elite.hp, elite.sp_body) == (elite.max_hp, 6)


def test_damage_above_sp_hurts_and_chips():
    elite = _armor_case([4, 4, 4])  # 12 - 6
    assert (elite.hp, elite.sp_body) == (elite.max_hp - 6, 5)


def test_crit_adds_bonus_after_armor():
    elite = _armor_case([6, 6, 1])  # (13 - 6) + 5
    assert elite.hp == elite.max_hp - 12


def test_zero_hp_flatlines_then_failed_save_kills():
    enc = make_encounter(tiers=("Boss",))
    face = enc.combatants["face"]
    face.hp = 1
    engine = Engine(CFG, ScriptedDice([6, 6, 1]))  # crit kills armor-free; injury d6=1
    face.sp_body = 0
    engine._damage(enc, enc.combatants["boss0"], face, 2, "body", "t")
    assert face.status == FLATLINING
    engine.dice.queue = [10]  # natural 10 always fails
    engine._death_save(enc, face, "turn")
    assert face.status == DEAD


def _start_turn(engine, enc, cid):
    engine.start(enc)
    apply(enc, Event("turn.started", {"actor": cid, "index": enc.order.index(cid)}))


def test_stabilize_returns_to_alive_at_one_hp():
    enc = make_encounter()
    tech, face = enc.combatants["tech"], enc.combatants["face"]
    engine = Engine(CFG, ScriptedDice())
    _start_turn(engine, enc, "tech")
    face.hp, face.status = 0, FLATLINING
    engine.dice.queue = [9]
    engine.resolve(enc, Action("stabilize", "tech", "face"))
    assert (face.status, face.hp, tech.medkits) == (ALIVE, 1, 1)


def test_taunt_costs_the_enemy_its_next_action():
    enc = make_encounter(tiers=("Mook",))
    engine = Engine(CFG, ScriptedDice())
    engine.start(enc)
    enc.combatants["mook0"].taunted_by = "face"
    apply(enc, Event("turn.started", {"actor": "mook0", "index": enc.order.index("mook0")}))
    assert engine.legal_actions(enc, "mook0") == []


def test_heat_degrades_cover_from_heat_round():
    cfg = CFG.merged({"heat_round": 2})
    enc = make_encounter(cfg)
    engine = Engine(cfg, Dice(bytes(range(32)), "heat"))
    engine.start(enc)
    for c in enc.combatants.values():
        c.cover = c.node_cover = "full"
    while enc.round < 2 and enc.result is None:
        actor = engine.advance(enc)
        if actor is None:
            break
        while opts := engine.legal_actions(enc, actor):
            engine.resolve(enc, opts[-1])
    assert any(ev.type == "heat.rose" for ev in engine.events)
    assert all(c.node_cover != "full" for c in enc.combatants.values())


def test_config_rejects_unknown_keys_and_deep_merges():
    with pytest.raises(KeyError):
        RulesConfig().merged({"nope": 1})
    merged = RulesConfig().merged({"seats": {"Solo": {"stats": {"IRON": 3}}}})
    assert merged.seats["Solo"]["stats"]["IRON"] == 3
    assert merged.seats["Solo"]["stats"]["MEAT"] == RulesConfig().seats["Solo"]["stats"]["MEAT"]
    assert RulesConfig().seats["Solo"]["stats"]["IRON"] == 8


@settings(max_examples=40, deadline=None)
@given(seed=st.binary(min_size=16, max_size=32),
       tiers=st.lists(st.sampled_from(["Mook", "Soldier", "Elite", "Boss"]), min_size=1, max_size=4),
       rng_range=st.sampled_from(["close", "mid", "far"]),
       pick=st.integers(min_value=0, max_value=7))
def test_any_encounter_terminates_with_sane_state(seed, tiers, rng_range, pick):
    enc = make_encounter(tiers=tuple(tiers), rng_range=rng_range)
    engine = Engine(CFG, Dice(seed, "prop"))
    play(engine, enc, party_choice=lambda opts: opts[pick % len(opts)])
    assert enc.result in {"victory", "wipe", "stalemate"}
    assert enc.round <= CFG.max_rounds
    for c in enc.combatants.values():
        assert 0 <= c.hp <= c.max_hp
        assert c.status != FLATLINING
        if c.status == DEAD:
            assert c.hp == 0
    dead_once = set()
    for ev in engine.events:
        target = ev.data.get("target")
        if ev.type == "status.changed" and ev.data["status"] == DEAD:
            dead_once.add(target)
        elif ev.type in ("healed", "stabilized") and target in dead_once:
            pytest.fail(f"{target} acted on after death")
