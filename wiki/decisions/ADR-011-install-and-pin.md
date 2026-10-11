---
type: decision
id: ADR-011
title: Reinstall CP2077 to D:, pin patch 2.31, treat the mod layer as a versioned artifact
status: accepted
updated: 2026-10-11
revisit_if: CDPR ships a patch the ecosystem supports and that we need
depends_on: [F-014, F-017, F-018]
---

# ADR-011 — Install & pin

**Context.** C: has 101 GB free; CP2077 needs roughly 70–100+ GB depending on DLC. Filling the system drive also
starves the pagefile on a 16 GB-RAM machine. D: has 3.4 TB free. The surviving mod layer sits in the C: Steam folder (F-017).

**Decision.** Install to `D:\SteamLibrary`, move the mod layer over, reinstall redscript, and freeze the verified mod
layer as a zip (`D:\cp2077-stack\stack-2.31-YYYYMMDD.zip`) after every successful smoke test. Exact steps: [plan/phase-0-reboot](../plan/phase-0-reboot.md).
