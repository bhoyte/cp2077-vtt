import pytest

from arcade.intent import ChatMsg, Option
from arcade.show import ClockConfig, ShowClock, Slot


def opt(number, label, *aliases):
    return Option(str(number), label, aliases)


def party(slot_id="solo", seat="Solo", options=None, **kwargs):
    options = options or (opt(1, "shoot"), opt(2, "cover"))
    return Slot(slot_id, "party", seat=seat, options=tuple(options), **kwargs)


def enemy(slot_id, target):
    return Slot(slot_id, "enemy", target=target)


def say(user, text, ts, seat="Solo"):
    return ChatMsg(user, user, ts, text, seat=seat)


def of(events, type_, slot=None):
    return [e for e in events if e.type == type_ and (slot is None or e.data.get("slot") == slot)]


def balanced(slots=None):
    """2–2 split: enough votes to skip the +3 s extension, not enough agreement to lock."""

    slots = slots or [party()]
    clock = ShowClock(slots)
    clock.start()
    clock.advance_to(1)
    for i, choice in enumerate(("1", "1", "2", "2")):
        clock.ingest(say(f"u{i}", choice, 1, seat=slots[0].seat))
    return clock


def test_grace_keeps_accepting_after_the_onscreen_timer_hits_zero():
    clock = balanced()
    opened = of(clock.log, "window.opened")[0]
    assert opened.data["viewer_close_at"] == pytest.approx(12)
    assert opened.data["server_close_at"] == pytest.approx(15)

    clock.advance_to(12)
    assert clock.ingest(say("on_zero", "1", 12))
    clock.advance_to(14.5)
    assert clock.ingest(say("during", "1", 14.5))
    assert of(clock.log, "window.closed") == []

    clock.advance_to(15)
    assert clock.ingest(say("after", "1", 15)) == []
    assert of(clock.log, "window.closed")[0].t == pytest.approx(15)
    assert clock.book.tally("solo") == {"1": 4, "2": 2}


def test_vote_during_grace_counts_and_the_timer_still_closes_at_viewer_plus_L():
    clock = balanced()
    clock.advance_to(13)
    assert clock.ingest(say("during", "1", 13))
    closed = of(clock.advance_to(15), "window.closed")
    assert closed[0].t == pytest.approx(15)
    assert closed[0].data["reason"] == "timer"
    assert closed[0].data["winner"] == "1"
    assert clock.t == pytest.approx(15)
    assert clock.ingest(say("after", "2", 15)) == []


def test_under_quorum_after_six_seconds_extends_the_window_and_its_grace():
    clock = ShowClock([party()])
    clock.start()
    clock.advance_to(6)
    assert of(clock.log, "window.extended") == []
    clock.ingest(say("early", "1", 6))  # still one vote, and it counts toward the check

    extended = of(clock.advance_to(7), "window.extended")
    assert len(extended) == 1
    assert extended[0].t == pytest.approx(6)
    assert extended[0].data["viewer_close_at"] == pytest.approx(15)
    assert extended[0].data["server_close_at"] == pytest.approx(18)

    clock.advance_to(17)
    assert clock.ingest(say("late", "2", 17))
    clock.advance_to(18)
    assert clock.ingest(say("too_late", "2", 18)) == []
    assert clock.book.tally("solo") == {"1": 1, "2": 1}


def test_quorum_reached_on_the_six_second_mark_does_not_extend():
    clock = ShowClock([party()])
    clock.start()
    clock.advance_to(6)
    for i, choice in enumerate(("1", "1", "2", "2")):
        clock.ingest(say(f"u{i}", choice, 6))
    clock.advance_to(15)
    assert of(clock.log, "window.extended") == []
    assert of(clock.log, "window.closed")[0].t == pytest.approx(15)


def test_early_lock_after_three_stable_seconds():
    clock = ShowClock([party(), party("net", "Netrunner")])
    clock.start()
    clock.advance_to(2)
    for i in range(3):
        clock.ingest(say(f"u{i}", "!1", 2))
    assert of(clock.log, "window.closed") == []

    assert of(clock.advance_to(4.9), "window.closed") == []
    closed = of(clock.advance_to(5), "window.closed")
    assert closed[0].data["reason"] == "locked_in"
    assert closed[0].data["winner"] == "1"
    assert closed[0].data["tally"] == {"1": 3, "2": 0}
    assert closed[0].t == pytest.approx(5)
    assert clock.ingest(say("late", "2", 5)) == []

    clock.advance_to(7.3)
    opened = of(clock.log, "window.opened", "net")
    assert len(opened) == 1
    assert opened[0].t == pytest.approx(7.3)


def test_another_vote_for_the_leader_does_not_restart_the_hold():
    clock = ShowClock([party()])
    clock.start()
    clock.advance_to(2)
    for i in range(3):
        clock.ingest(say(f"u{i}", "1", 2))
    clock.advance_to(4)
    clock.ingest(say("u3", "1", 4))
    closed = of(clock.advance_to(5), "window.closed")
    assert closed[0].data["reason"] == "locked_in"
    assert closed[0].data["tally"]["1"] == 4


def test_early_lock_restarts_when_the_lead_breaks():
    clock = ShowClock([party()])
    clock.start()
    clock.advance_to(1)
    for i in range(3):
        clock.ingest(say(f"a{i}", "1", 1))
    clock.advance_to(3)
    # a0 switching still leaves option 1 ahead; b0 ties it, which drops the hold.
    clock.ingest(say("a0", "2", 3))
    clock.ingest(say("b0", "2", 3))
    assert of(clock.advance_to(4), "window.closed") == []

    clock.advance_to(4.5)
    clock.ingest(say("c0", "2", 4.5))  # 3–2, a new 60% hold
    assert of(clock.advance_to(7.4), "window.closed") == []
    closed = of(clock.advance_to(7.5), "window.closed")
    assert closed[0].data["reason"] == "locked_in"
    assert closed[0].data["winner"] == "2"


def test_two_voters_do_not_lock():
    clock = ShowClock([party()])
    clock.start()
    clock.advance_to(1)
    clock.ingest(say("a", "1", 1))
    clock.ingest(say("b", "1", 1))
    clock.advance_to(10)
    assert of(clock.log, "window.closed") == []


def test_next_party_window_opens_when_the_beat_starts():
    clock = balanced([party("solo", "Solo"), party("net", "Netrunner")])
    assert of(clock.advance_to(17.2), "window.opened") == []
    opened = of(clock.advance_to(17.3), "window.opened")
    assert len(opened) == 1
    assert opened[0].data["slot"] == "net"
    assert opened[0].data["seat"] == "Netrunner"
    assert opened[0].t == pytest.approx(17.3)

    assert clock.ingest(say("fan", "1", 17.3, seat="Solo")) == []
    assert clock.ingest(say("runner", "!2", 17.3, seat="Netrunner"))
    assert clock.book.tally("net") == {"2": 1}
    assert clock.book.tally("solo") == {"1": 2, "2": 2}


def test_enemy_slot_has_no_window_and_same_target_batches_into_one_volley():
    clock = balanced(
        [
            party("solo", "Solo"),
            enemy("e1", "boss"),
            enemy("e2", "boss"),
            party("net", "Netrunner"),
        ]
    )
    clock.advance_to(clock.bound_s())
    assert [e.data["slot"] for e in of(clock.log, "window.opened")] == ["solo", "net"]
    volleys = [
        e
        for e in clock.log
        if e.type == "phase.started" and e.data["phase"] == "dice" and e.data["kind"] == "volley"
    ]
    assert len(volleys) == 1
    assert volleys[0].data["members"] == ["e1", "e2"]
    assert of(clock.log, "window.opened", "net")[0].t == pytest.approx(22.8)


def test_enemies_with_different_targets_are_not_one_volley():
    clock = balanced(
        [
            party("solo", "Solo"),
            enemy("e1", "boss"),
            enemy("e2", "mook"),
            party("net", "Netrunner"),
        ]
    )
    clock.advance_to(clock.bound_s())
    dice = [
        e
        for e in clock.log
        if e.type == "phase.started" and e.data["phase"] == "dice" and e.data["kind"] == "enemy"
    ]
    assert len(dice) == 2
    assert of(clock.log, "window.opened", "net")[0].t == pytest.approx(27.3)


def test_viewer_window_cannot_be_scheduled_under_six_seconds():
    with pytest.raises(ValueError):
        ClockConfig(window_s=5)
