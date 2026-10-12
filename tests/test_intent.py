import pytest

from arcade.ingest import ChatSim
from arcade.intent import Ballot, ChatMsg, FakeJev, Option, VoteBook, classify, parse_l0
from arcade.show import ShowClock, Slot


OPTIONS = (Option("1", "shoot", ("headshot",)), Option("2", "cover"))


def party(slot_id="solo", seat="Solo", options=None, **kwargs):
    options = options or (Option("1", "shoot"), Option("2", "cover"))
    return Slot(slot_id, "party", seat=seat, options=tuple(options), **kwargs)


def say(user, text, ts, seat="Solo"):
    return ChatMsg(user, user, ts, text, seat=seat)


def of(events, type_, slot=None):
    return [e for e in events if e.type == type_ and (slot is None or e.data.get("slot") == slot)]


def test_l0_parses_numbers_bangs_aliases_and_emotes():
    assert parse_l0("1", OPTIONS).option == "1"
    assert parse_l0("!2 now", OPTIONS).option == "2"
    assert parse_l0("!Headshot", OPTIONS).option == "1"
    assert parse_l0("please take COVER", OPTIONS).option == "2"
    assert parse_l0("VoteYea", OPTIONS, {"VoteYea": "1"}).option == "1"
    assert parse_l0("12", OPTIONS) is None
    assert parse_l0("3", OPTIONS) is None
    assert parse_l0("coverage plan", OPTIONS) is None
    assert parse_l0("shoot the cover", OPTIONS) is None
    assert parse_l0("lol", OPTIONS) is None


def test_l1_fake_runs_only_after_l0_misses_a_three_word_line():
    jev = FakeJev("2", 0.91)
    hit = classify("1", OPTIONS, jev=jev)
    assert hit is not None and hit.layer == "L0" and hit.conf == 1.0
    assert jev.requests == []

    assert classify("go left", OPTIONS, jev=jev) is None
    assert jev.requests == []

    hit = classify("please do the second one", OPTIONS, jev=jev, situation="solo pinned")
    assert hit is not None
    assert (hit.option, hit.layer, hit.conf) == ("2", "L1", 0.91)
    request = jev.requests[0]
    assert request["state"] == "solo pinned | message: please do the second one"
    vote = request["questions"]["vote"]
    assert vote["type"] == "choice"
    assert vote["criteria"]["2"] == "cover"
    assert "none" in vote["criteria"]

    # Ambiguous aliases are not an L0 vote, so free text may fall through.
    ambiguous = FakeJev("1", 0.95)
    assert classify("shoot the cover", OPTIONS, jev=ambiguous).option == "1"
    assert len(ambiguous.requests) == 1


def test_l1_rejects_none_low_confidence_and_a_missing_client():
    options = OPTIONS
    assert classify("please do the second one", options, jev=FakeJev("none", 0.99)) is None
    assert classify("please do the second one", options, jev=FakeJev("1", 0.6)).option == "1"
    assert classify("please do the second one", options, jev=FakeJev("1", 0.59)) is None
    assert classify("please do the second one", options, jev=FakeJev("9", 1.0)) is None
    assert classify("please do the second one", options, jev=None) is None


def test_latest_ballot_wins_and_a_tie_has_no_leader():
    book = VoteBook()
    book.cast("w", Ballot("a", "1", 1.0, "L0", 1.0))
    book.cast("w", Ballot("a", "2", 2.0, "L0", 1.0))
    book.cast("w", Ballot("b", "2", 1.5, "L1", 0.8))
    assert book.tally("w") == {"2": 2}
    assert book.leader("w") == ("2", 2, 2)

    book.cast("w", Ballot("b", "1", 3.0, "L0", 1.0))
    assert book.leader("w")[0] is None
    assert book.total("w") == 2


def test_clock_tally_keeps_one_vote_per_user_and_reports_ties():
    clock = ShowClock([party(options=OPTIONS)], emotes={"VoteYea": "1"})
    clock.start()
    clock.advance_to(1)
    clock.ingest(say("a", "!headshot", 1))
    clock.ingest(say("a", "2", 1))
    clock.ingest(say("a", "lol", 1))
    clock.ingest(say("b", "VoteYea", 1))
    assert clock.book.tally("solo") == {"2": 1, "1": 1}
    layers = {b.user_id: b.layer for b in clock.book.ballots("solo")}
    assert layers == {"a": "L0", "b": "L0"}
    clock.ingest(say("c", "1", 1))
    clock.ingest(say("d", "2", 1))

    closed = of(clock.advance_to(15), "window.closed")
    assert closed[0].data["tied"] is True
    assert closed[0].data["winner"] is None
    assert closed[0].data["tally"] == {"1": 2, "2": 2}


def test_only_the_active_squad_votes_unless_the_seat_is_open():
    clock = ShowClock([party()])
    clock.start()
    clock.advance_to(1)
    assert clock.ingest(say("facefan", "1", 1, seat="Face")) == []
    assert clock.ingest(say("solo1", "1", 1))

    open_seat = ShowClock([party(open_seat=True)])
    open_seat.start()
    open_seat.advance_to(1)
    assert open_seat.ingest(say("facefan", "!2", 1, seat="Face"))
    assert open_seat.book.tally("solo") == {"2": 1}


def test_clock_records_an_l1_ballot_from_the_fake():
    jev = FakeJev("2", 0.8)
    clock = ShowClock([party(options=OPTIONS)], jev=jev, situation="rooftop")
    clock.start()
    clock.advance_to(1)
    cast = clock.ingest(say("poet", "please do the second one", 1))
    assert cast[0].data["layer"] == "L1"
    assert cast[0].data["conf"] == 0.8
    assert cast[0].data["option"] == "2"
    ballot = clock.book.ballots("solo")[0]
    assert ballot.layer == "L1" and ballot.conf == 0.8


def test_chatsim_replay_locks_a_scripted_crowd():
    messages = [say(f"u{i}", "!1", 2.0) for i in range(3)]
    clock = ShowClock([party(), party("net", "Netrunner")])
    events = ChatSim(messages).replay(clock)
    closed = of(events, "window.closed", "solo")
    assert closed[0].data["reason"] == "locked_in"
    assert closed[0].data["winner"] == "1"
    assert closed[0].t == pytest.approx(5)
    assert of(events, "window.opened", "net")[0].t == pytest.approx(7.3)


def test_replay_is_deterministic():
    def run():
        messages = [say("b", "2", 4.0), say("a", "1", 1.0), say("a", "2", 4.0)]
        clock = ShowClock([party()])
        return [(e.t, e.type, e.data) for e in ChatSim(messages).replay(clock)]

    assert run() == run()


def test_non_vote_does_not_clear_a_ballot():
    clock = ShowClock([party()])
    clock.start()
    clock.advance_to(1)
    clock.ingest(say("a", "1", 1))
    clock.advance_to(2)
    assert clock.ingest(say("a", "haha nice", 2)) == []
    assert clock.book.tally("solo") == {"1": 1}
