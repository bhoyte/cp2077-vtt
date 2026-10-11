from pathlib import Path

from arcade.rules import load
from arcade.sim import TARGETS, run, verdict
from arcade.sim.__main__ import main

ROOT = Path(__file__).resolve().parents[1]
CFG = load(ROOT / "content/rules/season0.toml")


def test_sim_is_deterministic_and_reports_targets():
    a, b = run(CFG, 40, seed=11), run(CFG, 40, seed=11)
    assert a == b
    assert set(TARGETS) <= set(a)
    assert len(verdict(a)) == len(TARGETS)


def test_ablation_reports_every_seat():
    s = run(CFG, 20, seed=2, ablate=True)
    for key in ("seat_idle_share", "seat_random_share"):
        assert set(s[key]) == {"Solo", "Netrunner", "Tech", "Face"}


def test_cli_runs(capsys):
    assert main(["--gigs", "10", "--rules", str(ROOT / "content/rules/season0.toml")]) == 0
    assert "rounds_per_encounter" in capsys.readouterr().out
