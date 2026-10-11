"""Dice CLI.

python -m arcade.dice new                         print a fresh seed and its commitment
python -m arcade.dice verify LOG.json SEED_HEX    check a published roll log against a revealed seed
"""

import json
import secrets
import sys

from .service import commit_of, verify_log


def main(argv: list[str]) -> int:
    if len(argv) >= 1 and argv[0] == "new":
        seed = secrets.token_bytes(32)
        print(f"seed   {seed.hex()}\ncommit {commit_of(seed)}")
        return 0
    if len(argv) == 3 and argv[0] == "verify":
        with open(argv[1], encoding="utf-8") as fh:
            exported = json.load(fh)
        problems = verify_log(argv[2], exported)
        for p in problems:
            print(f"FAIL  {p}")
        if not problems:
            print(f"OK  {len(exported['rolls'])} rolls verified against commit {exported['commit'][:16]}…")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
