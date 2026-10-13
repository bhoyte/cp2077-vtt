---
type: hub
title: Now — current focus and handoff
status: active
updated: 2026-10-13
---

# Now

**Focus:** The session redials. ArcadeLink 0.1.2 came back by itself after the booth was killed. `status` still returns V's position. The roof cast was not touched.
**Active gates:** G1 First Light (Track A), G2 Ghost Cabinet (Track B). See [roadmap](plan/roadmap.md).
**Orientation:** [overview](overview.md) · [glossary](glossary.md) · [ADR-013](decisions/ADR-013-operated-table.md).

## Next actions
1. Leave Johnny, Hanako, and Song So Ri on the roof until the next table command exists.
2. Add `place` on this session. The reply includes measured positions. Use `Tools:TeleportNPCTo` (F-028). Do not teleport V.
3. Booth stays up. Do not reload CET to send a command.

## Blockers
- The actor list in `status` is still empty. This session does not yet know the three bodies on the roof. C: space still tight (R-15).

## Last handoff (2026-10-13)
Session closed. Redial verified: `link down quiet=3.4` at 02:23:59, hello again at 02:24:07, no reload between them. V at -1536.78, 1195.77, 57.00. The three were left on the roof; this session does not track them. Chat archive: raw/chats/2026-10-12_2026-10-13-bridge/ (read session.md first).
