---
type: component
title: Intent — chat ingest, parsing, Jev, vote book
status: draft
updated: 2026-10-11
depends_on: [ADR-004, F-015]
---

# Intent

## Ingest
Twitch EventSub WebSocket: `channel.chat.message`, `channel.channel_points_custom_reward_redemption.add`. Each message →
`ChatMsg{user_id, login, ts_arrival, text, badges}`. ChatSim produces the same objects (bot crowds with skill/noise profiles; replays).

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
