---
type: component
title: Intent — chat ingest, parsing, Jev, vote book
status: draft
updated: 2026-10-12
depends_on: [ADR-004, F-015]
---

# Intent

## Ingest
Twitch EventSub WebSocket: `channel.chat.message`, `channel.channel_points_custom_reward_redemption.add`. Each message →
`ChatMsg{user_id, login, ts_arrival, text, badges, seat}`. `seat` is the squad this account belongs to for the replay (`Solo`, `Netrunner`, `Tech`, `Face`, or empty). ChatSim produces the same objects. Bot crowds and the account-age gate are not in this slice.

## Pipeline per message (during an open window, for the active seat's squad or open seat)
1. Membership check (squad, account-age gate).
2. **L0**: normalize → regex `^!?([1-4])\b` → option keyword/alias table (built per window from option labels: "headshot", "boss", "cover"…) → emote map.
3. **L1** (only if L0 fails and the text is ≥ 3 words): Jev request
   `{"state": "<situation summary> | message: <text>", "questions": {"vote": {"type": "choice", "instructions": "Which option does this chat message vote for? 'none' if it is not a vote.", "criteria": {"opt1": "...", "opt2": "...", "none": "chatter, jokes, questions, or unrelated"}}}}`
   Accept if `choice != none` and `confidence ≥ θ` (start 0.6). Timeout 1.5 s; circuit breaker after 5 consecutive failures.
4. Vote book: `votes[user] = (option, ts, layer, conf)`; latest wins; broadcast tally.

## Messages from non-active squads
→ comms feed (rate-limited, AutoMod-cleared only), plus `!assist` counting (experiment E-1).

## S-07 corpus
Record a few hours of real Twitch chat from comparable streams (or playtests) and label 500 messages. That corpus sets θ and tests the L0 alias tables.

## Implemented slice (2026-10-12)

Code: `arcade/intent/` (parser, vote book, Jev boundary) and `arcade/ingest/chatsim.py`. No network, no API key, no wall clock.

- **L0** (`parse_l0`): lowercase, trim, collapse whitespace. Then `^!?([1-4])\b` when that id is on the window; else a unique whole-word hit on the label or an alias (a single leading `!` is stripped first, so `!headshot` counts); else the whole message as one token in the caller-supplied emote map. `12` is not `1`. Two aliases in one line are not an L0 vote.
- **L1**: `JevClient.choose(request) -> JevChoice | None`. The request body matches the shape above. `FakeJev` returns a fixed choice and records the request; it does not call a service. Classify calls it only when L0 misses and the text has at least three words. Accept when `choice` is an option id and `confidence ≥ θ` (0.6). `none`, a low score, and an unknown id are not votes. Timeout and the circuit breaker are not implemented; there is no live client. Passing no client leaves the show on L0 (R-13).
- **Vote book**: one ballot per `(window, user)`, storing `(option, ts, layer, conf)`. A later classified vote replaces the earlier one. A message that does not classify leaves the ballot in place. Tally is a count per option. A tie has no leader; the dice service breaks ties, not this book.
- **Who may vote**: the active seat's squad, or anyone when the slot is flagged `open_seat`. The clock does not compute `N_min` or the 10-minute activity window; the caller sets the flag. Comms and `!assist` are not counted here.
- **ChatSim.replay** takes a list of `ChatMsg`, advances the show clock to each `ts_arrival` (input order breaks timestamp ties), and ingests. It is not a Twitch client.
