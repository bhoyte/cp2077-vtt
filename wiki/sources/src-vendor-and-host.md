---
type: source
title: Vendor docs (Jev, patch compatibility) and the 2026-10-11 host audit
status: current
updated: 2026-10-11
raw: [raw/web/typesafe-jev-2026-10-11.md, raw/web/cp2077-compat-2026-10-11.md, raw/env/host-audit-2026-10-11.md, raw/amm/camera.lua]
---

# Source: vendors and host

- **Jev** exists and fits ADR-004: `choice` over ≤ 255 options, calibrated probabilities, negligible cost (F-015). Latency is unproven (S-07).
- **Patch 2.31** is still current (2026-10-08 matrix) and CET 1.37.1 matches. The April stack should work unchanged (F-014).
- **Host**: 3060 Ti 8 GB / R5 5600 / 16 GB. RAM is the tightest resource (R-09, S-05). C: has too little space for the install (ADR-011). OBS isn't installed. The mod layer survived the uninstall; redscript didn't (F-017).
- **AMM camera.lua** is the key evidence that scripted cameras exist (F-007). It's the foundation of S-01.
