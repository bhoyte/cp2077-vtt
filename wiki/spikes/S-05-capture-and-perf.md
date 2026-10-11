---
type: spike
id: S-05
title: Capture and performance budget on this PC
status: planned
gate: G1
updated: 2026-10-11
depends_on: [F-018]
---

# S-05 — Capture & performance

**Setup.** OBS 32 (installer on D:), Game Capture, NVENC H.264, 1080p60, 6000 kbps CBR, one 1080p overlay browser source.
Game: 1080p, DLSS Quality, ray tracing off, crowd density low, 60 fps cap. Orchestrator + FakeStage overlay running.

**Measure over 30 min with beats running.** Game FPS (p1 low), GPU util, VRAM, system RAM committed, OBS "skipped frames due to encoding lag" and "rendering lag", CPU.

**Pass.** Game ≥ 55 fps p1 (or a locked 30 fps if it looks fine on stream), OBS skipped frames < 0.5 %, RAM headroom ≥ 1.5 GB.

**Decision output.** Is the 32 GB RAM upgrade mandatory (Q-07)? Which preset is the stream default?

## Result
_(not run)_
