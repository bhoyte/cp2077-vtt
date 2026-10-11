---
type: spike
id: S-03
title: Staged violence — gunfire FX, hit reactions, death on command
status: planned
gate: G1
updated: 2026-10-11
depends_on: [F-012, F-013]
---

# S-03 — Staged violence

**Hypothesis.** A 4-second "shot → hit → drop" beat can be built from held poses, FX entities, and a death state, and it
reads clearly with no game combat AI involved.

**Candidates to test (research each in NativeDB/AMM source before calling):**
- Muzzle flash / impact / blood: AMM "FX & Effects" entities (103, F-012) spawned at weapon/target positions and despawned after ~200 ms.
- Death: (a) a lying-dead workspot; (b) killing the puppet and letting it ragdoll; (c) AMM's fake-death approach (named in the brief, unverified). Compare how it looks and whether the body stays put.
- Hit reaction: a stagger pose between shot and death; camera micro-shake via a 0.1 s blend jitter.
- Gun audio comes from the overlay/OBS (cue op), so it's deterministic.

**Procedure.** Build three beats by hand (miss, hit, kill), play each 10× on the same set, record clips. Blind test: show the
clips to 3 people and ask "what happened?"

**Pass.** ≥ 90 % correct reads; the corpse is stable for the rest of the scene (and restageable as `state: dead`).

**Fallback.** Cut away on impact (reaction shot of the shooter + SFX + overlay KILL banner) and reveal the body already in the death pose.

## Result
_(not run)_
