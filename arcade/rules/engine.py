"""Rules engine. Changes state only by emitting events through `apply` (ADR-007); all randomness via Dice (ADR-006).

Turn loop for any driver (orchestrator, simulator):
    engine.start(enc)
    while (actor := engine.advance(enc)) is not None:
        while engine.legal_actions(enc, actor):
            engine.resolve(enc, choose(engine.legal_actions(enc, actor)))
"""

from __future__ import annotations

from dataclasses import dataclass

from ..dice import Dice
from .config import RulesConfig
from .events import Event, apply
from .model import ALIVE, COVER, DEAD, FLATLINING, FLED, INJURIES, WEAPONS, Action, Combatant, Encounter


class IllegalAction(ValueError):
    pass


@dataclass(frozen=True)
class Check:
    natural: int
    extra: int
    modifier: int
    total: int
    dv: int

    @property
    def success(self) -> bool:
        return self.total >= self.dv


SEAT_ABILITIES = {
    "Solo": ("overclock",),
    "Netrunner": ("blackout", "short_circuit"),
    "Tech": ("patch", "stabilize", "deploy_cover"),
    "Face": ("taunt",),
}
ONCE_PER_ENCOUNTER = {"overclock", "blackout", "deploy_cover", "lock_on", "rampage"}


class Engine:
    def __init__(self, cfg: RulesConfig, dice: Dice) -> None:
        self.cfg = cfg
        self.dice = dice
        self.events: list[Event] = []

    # ---------------------------------------------------------------- plumbing

    def _emit(self, enc: Encounter, type_: str, **data) -> Event:
        ev = Event(type_, data)
        apply(enc, ev)
        self.events.append(ev)
        return ev

    def check(self, c: Combatant, stat: str, dv: int, modifier: int, purpose: str) -> Check:
        natural = self.dice.d10(f"{purpose}:d10")
        extra = 0
        if natural == 10:
            extra = self.dice.d10(f"{purpose}:spike")
        elif natural == 1:
            extra = -self.dice.d10(f"{purpose}:glitch")
        mod = c.stat(stat) + (c.specialty if stat == c.signature else 0) + modifier
        if c.wounded and c.status == ALIVE:
            mod -= self.cfg.wounded_penalty
        return Check(natural, extra, mod, natural + extra + mod, dv)

    # ---------------------------------------------------------------- flow

    def start(self, enc: Encounter) -> None:
        self._emit(enc, "encounter.started", id=enc.id)
        scores: dict[str, tuple[int, int, int]] = {}
        for cid in sorted(enc.combatants):
            c = enc.combatants[cid]
            if c.status in (DEAD, FLED):
                continue
            bonus = self.cfg.solo_initiative_bonus if c.role == "Solo" else 0
            roll = self.dice.d10(f"init:{cid}")
            scores[cid] = (roll + c.stat("GHOST") + bonus, c.stat("GHOST"), self.dice.d10(f"init-tiebreak:{cid}"))
            self._emit(enc, "initiative.rolled", actor=cid, roll=roll, total=scores[cid][0])
        order = sorted(scores, key=lambda k: scores[k], reverse=True)
        self._emit(enc, "initiative.set", order=order)
        self._check_end(enc)

    def breather(self, enc: Encounter) -> None:
        """Between encounters of one gig: surviving party recover breather_heal_dice d6."""
        for p in enc.side("party"):
            if p.status == ALIVE and p.hp < p.max_hp and self.cfg.breather_heal_dice:
                amount = sum(self.dice.d6(f"{enc.id}:breather:{p.id}#{i}") for i in range(self.cfg.breather_heal_dice))
                self._emit(enc, "healed", target=p.id, by="breather", amount=amount)

    def advance(self, enc: Encounter) -> str | None:
        """Process start-of-turn effects until someone can act. Returns their id, or None when the encounter ends."""
        idx = enc.pointer + 1
        while enc.result is None:
            if enc.round == 0 or idx >= len(enc.order):
                if enc.round >= self.cfg.max_rounds:
                    self._end(enc, "stalemate")
                    break
                self._emit(enc, "round.started", round=enc.round + 1)
                if enc.round >= self.cfg.heat_round:
                    self._emit(enc, "heat.rose", round=enc.round)
                idx = 0
                continue
            cid = enc.order[idx]
            c = enc.combatants[cid]
            idx += 1
            if c.status in (DEAD, FLED):
                continue
            self._emit(enc, "turn.started", actor=cid, index=idx - 1)
            if c.status == FLATLINING:
                self._death_save(enc, c, "turn")
                self._check_end(enc)
                continue
            if c.role == "Mook" and c.hp <= self.cfg.mook_flee_hp and not self._leaders_standing(enc):
                self._emit(enc, "status.changed", target=cid, status=FLED)
                self._check_end(enc)
                continue
            if c.bleed:
                self._emit(enc, "bled", target=cid, amount=c.bleed)
                self._after_hp_change(enc, c, took_damage=False)
                if c.status != ALIVE:
                    self._check_end(enc)
                    continue
            return cid
        return None

    # ---------------------------------------------------------------- legality

    def legal_actions(self, enc: Encounter, cid: str) -> list[Action]:
        c = enc.combatants[cid]
        if enc.result is not None or c.status != ALIVE or c.actions_left <= 0:
            return []
        foes = [f for f in enc.side("enemy" if c.side == "party" else "party") if f.status in (ALIVE, FLATLINING)]
        allies = [a for a in enc.side(c.side) if a.id != cid]
        weapon = WEAPONS[c.weapon]
        shootable = [f for f in foes if not weapon.close_only or enc.range_between(cid, f.id) == "close"]
        acts: list[Action] = []
        for f in shootable:
            acts.append(Action("attack", cid, f.id))
            if c.side == "party" and f.status == ALIVE:
                acts.append(Action("aimed_shot", cid, f.id))
                acts.append(Action("suppress", cid, f.id))
        if COVER.index(c.cover) < COVER.index(c.node_cover):
            acts.append(Action("take_cover", cid))
        unused = lambda ability: ability not in c.used  # noqa: E731
        living_foes = [f for f in foes if f.status == ALIVE]
        match c.role:
            case "Solo" if unused("overclock"):
                acts += [Action("overclock", cid, f.id) for f in shootable if f.status == ALIVE]
            case "Netrunner":
                if unused("blackout") and enc.blackout == 0:
                    acts.append(Action("blackout", cid))
                acts += [Action("short_circuit", cid, f.id) for f in living_foes]
            case "Tech":
                acts += [Action("stabilize", cid, a.id) for a in allies if a.status == FLATLINING]
                acts += [Action("patch", cid, a.id) for a in [c, *allies] if a.status == ALIVE and not a.patched and a.hp < a.max_hp]
                if unused("deploy_cover"):
                    acts += [Action("deploy_cover", cid, a.id) for a in [c, *allies] if a.status == ALIVE and a.cover != "full"]
            case "Face":
                acts += [Action("taunt", cid, f.id) for f in living_foes if not f.taunted_by]
            case "Elite" if unused("lock_on"):
                acts += [Action("lock_on", cid, f.id) for f in shootable if f.status == ALIVE]
            case "Boss" if unused("rampage") and any(f.status == ALIVE for f in shootable):
                acts.append(Action("rampage", cid))
        acts.append(Action("hold", cid))
        return acts

    # ---------------------------------------------------------------- resolution

    def resolve(self, enc: Encounter, action: Action) -> None:
        if action not in self.legal_actions(enc, action.actor):
            raise IllegalAction(f"{action} is not legal for {action.actor}")
        c = enc.combatants[action.actor]
        t = enc.combatants.get(action.target) if action.target else None
        tag = f"r{enc.round}:{c.id}:{action.kind}"
        if action.kind in ONCE_PER_ENCOUNTER:
            self._emit(enc, "ability.used", actor=c.id, ability=action.kind)
        match action.kind:
            case "attack":
                self._attack(enc, c, t, tag)
            case "aimed_shot":
                self._attack(enc, c, t, tag, aimed=True)
            case "lock_on":
                self._attack(enc, c, t, tag, modifier=self.cfg.lock_on_bonus)
            case "overclock":
                for n in (1, 2):
                    if t.status == ALIVE:
                        self._attack(enc, c, t, f"{tag}#{n}", modifier=-self.cfg.overclock_penalty)
            case "rampage":
                for f in [f for f in enc.side("party") if f.status == ALIVE]:
                    self._attack(enc, c, f, f"{tag}:{f.id}", modifier=-self.cfg.rampage_penalty)
            case "suppress":
                save = self.check(t, "GHOST", self.cfg.suppress_dv, 0, f"{tag}:save")
                self._emit(enc, "check.rolled", actor=t.id, kind="suppress_save", **_check_data(save))
                if not save.success:
                    self._emit(enc, "pinned", target=t.id, by=c.id)
            case "hold":
                self._emit(enc, "held", actor=c.id)
            case "take_cover":
                self._emit(enc, "cover.changed", target=c.id, cover=c.node_cover)
            case "deploy_cover":
                self._emit(enc, "cover.changed", target=t.id, cover="full", by=c.id)
            case "blackout":
                chk = self.check(c, "JACK", self.cfg.blackout_dv, 0, tag)
                self._emit(enc, "check.rolled", actor=c.id, kind="blackout", **_check_data(chk))
                if chk.success:
                    self._emit(enc, "blackout", rounds=self.cfg.blackout_rounds, by=c.id)
            case "short_circuit":
                chk = self.check(c, "JACK", self.cfg.short_dv, 0, tag)
                self._emit(enc, "check.rolled", actor=c.id, kind="short_circuit", target_id=t.id, **_check_data(chk))
                if chk.success:
                    self._damage(enc, c, t, self.cfg.short_dice, "body", tag, direct=True)
            case "taunt":
                dv = self.cfg.taunt_resolve.get(t.role, 12)
                chk = self.check(c, "TALK", dv, 0, tag)
                self._emit(enc, "check.rolled", actor=c.id, kind="taunt", target_id=t.id, **_check_data(chk))
                if chk.success:
                    self._emit(enc, "taunted", target=t.id, by=c.id)
            case "patch":
                chk = self.check(c, "WRENCH", self.cfg.patch_dv, 0, tag)
                self._emit(enc, "check.rolled", actor=c.id, kind="patch", target_id=t.id, **_check_data(chk))
                if chk.success:
                    amount = sum(self.dice.d6(f"{tag}:heal#{i}") for i in range(self.cfg.patch_dice))
                    self._emit(enc, "healed", target=t.id, by=c.id, amount=amount)
            case "stabilize":
                bonus = 0
                if c.medkits > 0:
                    bonus = self.cfg.medkit_bonus
                    self._emit(enc, "medkit.used", actor=c.id)
                chk = self.check(c, "WRENCH", self.cfg.stabilize_dv, bonus, tag)
                self._emit(enc, "check.rolled", actor=c.id, kind="stabilize", target_id=t.id, **_check_data(chk))
                if chk.success:
                    self._emit(enc, "stabilized", target=t.id, by=c.id)
            case _:
                raise IllegalAction(action.kind)
        if c.status == ALIVE:
            self._emit(enc, "action.spent", actor=c.id)
        self._check_end(enc)

    def _attack(self, enc: Encounter, c: Combatant, t: Combatant, tag: str, *, aimed: bool = False, modifier: int = 0) -> None:
        dv = self.cfg.range_dv[enc.range_between(c.id, t.id)] + self.cfg.cover_bonus[t.cover]
        mod = modifier - (self.cfg.aimed_head_penalty if aimed else 0)
        if c.side == "party":
            mod += self.cfg.weapon_skill
        if c.suppressed:
            mod -= self.cfg.pinned_penalty
        if c.side == "enemy" and enc.blackout > 0:
            mod -= self.cfg.blackout_penalty
        chk = self.check(c, "IRON", dv, mod, tag)
        self._emit(enc, "attack.rolled", actor=c.id, target_id=t.id, aimed=aimed, **_check_data(chk))
        if chk.success:
            self._damage(enc, c, t, WEAPONS[c.weapon].dice, "head" if aimed else "body", tag)

    def _damage(self, enc: Encounter, src: Combatant, t: Combatant, ndice: int, location: str, tag: str, *, direct: bool = False) -> None:
        dice = [self.dice.d6(f"{tag}:dmg#{i}") for i in range(ndice)]
        raw = sum(dice)
        crit = dice.count(6) >= self.cfg.crit_six_count
        sp = t.sp_head if location == "head" else t.sp_body
        if direct:
            loss, chip = raw, False
        elif raw > sp:
            loss, chip = raw - sp, True
        else:
            loss, chip = 0, False
        if location == "head":
            loss *= self.cfg.head_multiplier
        if crit:
            loss += self.cfg.crit_bonus
        was_down = t.status == FLATLINING
        self._emit(enc, "damage.applied", source=src.id, target=t.id, dice=dice, raw=raw, location=location,
                   sp=sp, loss=loss, chip=chip, crit=crit)
        if crit and t.side == "party" and t.status != DEAD:
            name = INJURIES[self.dice.d6(f"{tag}:injury")][0]
            self._emit(enc, "injury.added", target=t.id, injury=name)
        self._after_hp_change(enc, t, took_damage=loss > 0 and was_down)

    def _after_hp_change(self, enc: Encounter, c: Combatant, *, took_damage: bool) -> None:
        if c.hp > 0 or c.status in (DEAD, FLED):
            return
        if c.side == "enemy":
            self._emit(enc, "status.changed", target=c.id, status=DEAD)
        elif c.status == ALIVE:
            self._emit(enc, "status.changed", target=c.id, status=FLATLINING)
        elif took_damage:
            self._death_save(enc, c, "damage")

    def _death_save(self, enc: Encounter, c: Combatant, reason: str) -> None:
        threshold = c.stats["MEAT"] + self.cfg.death_save_offset - c.death_saves
        roll = self.dice.d10(f"r{enc.round}:{c.id}:death_save#{c.death_saves}")
        success = roll != 10 and roll <= threshold
        self._emit(enc, "death_save", target=c.id, roll=roll, threshold=threshold, success=success, reason=reason)
        if not success:
            self._emit(enc, "status.changed", target=c.id, status=DEAD)

    # ---------------------------------------------------------------- endings

    def _leaders_standing(self, enc: Encounter) -> bool:
        return any(e.status == ALIVE and e.role != "Mook" for e in enc.side("enemy"))

    def _check_end(self, enc: Encounter) -> None:
        if enc.result is not None:
            return
        if not any(e.status == ALIVE for e in enc.side("enemy")):
            self._end(enc, "victory")
        elif not any(p.status == ALIVE for p in enc.side("party")):
            self._end(enc, "wipe")

    def _end(self, enc: Encounter, result: str) -> None:
        carried = any(p.status == ALIVE for p in enc.side("party"))
        for p in enc.side("party"):
            if p.status == FLATLINING:
                if carried:
                    self._emit(enc, "stabilized", target=p.id, by="extraction")
                else:
                    self._emit(enc, "status.changed", target=p.id, status=DEAD)
        self._emit(enc, "encounter.ended", result=result)


def _check_data(chk: Check) -> dict:
    return {"natural": chk.natural, "extra": chk.extra, "modifier": chk.modifier, "total": chk.total,
            "dv": chk.dv, "success": chk.success}
