---
type: decision
id: ADR-012
title: Keep CP2077 on the C: SSD; pin 2.31; freeze backups on D:
status: accepted
updated: 2026-10-11
supersedes: ADR-011
revisit_if: C: free space drops below ~20 GB, or a Steam update forces a move
depends_on: [F-014, F-017, F-020, F-021]
---

# ADR-012 — Install path (SSD) and pin

**Context.** ADR-011 put the game on `D:\SteamLibrary` because C: had 101 GB free and filling the system drive
starves the pagefile. The user installed on C: instead, and C: is the Kingston NVMe SSD; D: is a Toshiba USB HDD.
A 91 GB open-world game on USB HDD would punish load times, texture streaming, and S-05 capture work. After the
install, C: has 51 GB free (F-021). The April mod layer was already in the C: Steam folder and survived (F-020).

**Decision.** Keep the game at `C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077`. Pin patch 2.31.
Put bulky artifacts on D: (mod-layer zip, full game-folder backup, OBS recordings). Do not move the live install
to the HDD. Remaining restore/smoke/freeze steps: [phase-0-reboot](../plan/phase-0-reboot.md).
