"""L0 parser and the L0-then-L1 classify step (ADR-004)."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from .jev import JevClient
from .model import Hit, Option

# `!` is optional; the digit must end on a word boundary so "12" is not "1".
_NUMBER = re.compile(r"^!?([1-4])\b")
_LEADING_BANG = re.compile(r"^!(?=\S)")

_INSTRUCTIONS = "Which option does this chat message vote for? 'none' if it is not a vote."
_NONE = "chatter, jokes, questions, or unrelated"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def word_count(text: str) -> int:
    norm = normalize(text)
    return len(norm.split()) if norm else 0


def parse_l0(
    text: str,
    options: Sequence[Option],
    emotes: Mapping[str, str] | None = None,
) -> Hit | None:
    """Number, then a unique alias, then a single-token emote. None if it is not a vote."""

    norm = normalize(text)
    if not norm:
        return None
    ids = {opt.id for opt in options}
    numbered = _NUMBER.match(norm)
    if numbered:
        option = numbered.group(1)
        return Hit(option, "L0", 1.0) if option in ids else None

    bare = _LEADING_BANG.sub("", norm, count=1)
    hits = [opt.id for opt in options if _alias_hit(opt, bare)]
    unique = set(hits)
    if len(unique) == 1:
        return Hit(next(iter(unique)), "L0", 1.0)
    if len(unique) > 1:
        return None

    mapped = {normalize(name): option for name, option in (emotes or {}).items()}
    if bare in mapped and mapped[bare] in ids:
        return Hit(mapped[bare], "L0", 1.0)
    return None


def jev_request(situation: str, text: str, options: Sequence[Option]) -> dict:
    criteria = {opt.id: opt.label for opt in options}
    criteria["none"] = _NONE
    return {
        "state": f"{situation} | message: {text}",
        "questions": {
            "vote": {
                "type": "choice",
                "instructions": _INSTRUCTIONS,
                "criteria": criteria,
            }
        },
    }


def classify(
    text: str,
    options: Sequence[Option],
    *,
    emotes: Mapping[str, str] | None = None,
    jev: JevClient | None = None,
    situation: str = "",
    theta: float = 0.6,
) -> Hit | None:
    """L0 first. L1 only when L0 misses and the text is at least three words."""

    hit = parse_l0(text, options, emotes)
    if hit is not None:
        return hit
    if jev is None or word_count(text) < 3:
        return None
    answer = jev.choose(jev_request(situation, text, options))
    if answer is None:
        return None
    ids = {opt.id for opt in options}
    if answer.choice in ids and answer.confidence >= theta:
        return Hit(answer.choice, "L1", answer.confidence)
    return None


def _alias_hit(opt: Option, text: str) -> bool:
    names = [opt.label, *opt.aliases]
    return any(_whole_word(normalize(name), text) for name in names if normalize(name))


def _whole_word(needle: str, haystack: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", haystack) is not None
