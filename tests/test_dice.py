from collections import Counter

import pytest

from arcade.dice import Dice, verify_log

SEED = bytes(range(32))


def test_same_seed_same_rolls():
    a, b = Dice(SEED, "s1"), Dice(SEED, "s1")
    assert [a.d10("x") for _ in range(50)] == [b.d10("x") for _ in range(50)]


def test_session_and_purpose_change_the_stream():
    def stream(session, purpose):
        d = Dice(SEED, session)
        return [d.d10(purpose) for _ in range(20)]

    assert stream("s1", "x") != stream("s2", "x")
    assert stream("s1", "x") != stream("s1", "y")


def test_verify_accepts_honest_log():
    d = Dice(SEED, "show-1")
    for i in range(200):
        d.roll(6 if i % 2 else 10, f"p{i}")
    assert verify_log(SEED.hex(), d.export()) == []


def test_verify_catches_tampering_and_wrong_seed():
    d = Dice(SEED, "show-1")
    for i in range(20):
        d.d10(f"p{i}")
    log = d.export()
    log["rolls"][5]["value"] = log["rolls"][5]["value"] % 10 + 1
    assert any("#5" in p for p in verify_log(SEED.hex(), log))
    assert any("commitment" in p for p in verify_log(bytes(32).hex(), d.export()))


def test_faces_are_uniform():
    d = Dice(SEED, "uniform")
    n = 20_000
    counts = Counter(d.d10("u") for _ in range(n))
    expected = n / 10
    chi2 = sum((counts[f] - expected) ** 2 / expected for f in range(1, 11))
    assert set(counts) == set(range(1, 11))
    assert chi2 < 27.9  # p = 0.001 for 9 degrees of freedom


def test_rejects_bad_inputs():
    with pytest.raises(ValueError):
        Dice(b"short")
    with pytest.raises(ValueError):
        Dice(SEED).roll(1, "x")
    with pytest.raises(ValueError):
        Dice(SEED).roll(6, "a\x1fb")
