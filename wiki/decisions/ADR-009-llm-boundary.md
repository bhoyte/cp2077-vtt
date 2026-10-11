---
type: decision
id: ADR-009
title: Generative LLMs stay out of the authoritative loop; allowed offline and for selection
status: accepted
updated: 2026-10-11
supersedes: night-city-live "Ollama director on phase transitions"
revisit_if: A non-authoritative live narration feature is wanted and proven safe with a canned fallback
depends_on: []
---

# ADR-009 — Where AI is allowed

| Zone | Allowed | Examples |
|---|---|---|
| Authoritative (rules, dice, votes, outcomes, state) | **No generative models.** Deterministic code + Jev classification only. | — |
| Selection at runtime | Jev picks among pre-written options | Which handler line, which beat variant, which bark fits |
| Offline authoring | Any LLM / agent | Gig scripts, beat templates, bark pools, lifepath tables, lint of content, scene-manifest drafting |
| Offline media | Video/image/TTS models | Memorial videos, travel stingers, portraits |

**Why.** The spec's instinct is right. Determinism is what makes permadeath fair and replays exact (ADR-006/007). The
prior project's live Ollama director adds latency, cost, and narrative drift for little gain over large pre-written
pools selected in context. Content pools are also reviewable before air (moderation).
