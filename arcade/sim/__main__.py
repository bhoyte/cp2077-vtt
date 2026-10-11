"""python -m arcade.sim [--gigs N] [--seed S] [--rules content/rules/season0.toml] [--chaos 0.15] [--ablate] [--json]"""

from __future__ import annotations

import argparse
import json
import sys

from ..rules.config import load
from .run import run, verdict


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="arcade.sim")
    ap.add_argument("--gigs", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--rules", default=None)
    ap.add_argument("--chaos", type=float, default=0.15, help="share of crowd decisions that are uniformly random")
    ap.add_argument("--ablate", action="store_true", help="rerun with each seat idle to measure seat impact")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    summary = run(load(args.rules), args.gigs, args.seed, args.chaos, args.ablate)
    if args.json:
        print(json.dumps(summary, indent=2))
        return 0
    for line in verdict(summary):
        print(line)
    print(f"rounds p90 = {summary['rounds_p90']}, mean deaths/gig = {summary['mean_deaths']:.2f}, "
          f"loss/gig = {summary['loss']:.3f}")
    print("damage share: " + ", ".join(f"{k} {v:.0%}" for k, v in summary["damage_share"].items()))
    for key, label in (("idle", "seat power (extra loss/gig if the seat holds)"),
                       ("random", "vote leverage (extra loss/gig if the seat votes randomly)")):
        if f"seat_{key}_share" in summary:
            print(f"{label}: " + ", ".join(f"{k} +{summary[f'seat_loss_if_{key}'][k]:.2f} ({v:.0%})"
                                          for k, v in summary[f"seat_{key}_share"].items()))
    for shape, s in summary["by_shape"].items():
        print(f"  {shape:14s} n={s['n']:5d} rounds={s['rounds']:.1f} p_death={s['p_death']:.2f} p_wipe={s['p_wipe']:.3f}")
    print("top party actions: " + ", ".join(f"{k}={v}" for k, v in summary["top_actions"][:10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
