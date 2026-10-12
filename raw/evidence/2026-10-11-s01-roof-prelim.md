# S-01 roof prelim — 2026-10-11 22:46–22:50

Manual hotkeys, player stayed on the roof. Log: `scripting.log`.

- 22:46:46 spawn, hard cut to cam_a.
- 22:47:38 blend 1.5 s from cam_a to cam_b.
- 22:48:29–22:50:00 further hard cuts A/B/C and two more 1.5 s blends (B from A, A from C). Every `cut` returned `ok=true`.

Frames, in the order sent:

- `2026-10-11-s01-roof-a.jpg` — high angle, V's full body in frame, HUD on (minimap, quest, weapon prompts).
- `2026-10-11-s01-roof-b.jpg` — along the railing, V out of frame, cyan crosshair and HUD still on.
- `2026-10-11-s01-roof-c.jpg` — toward the billboard and the chairs. Different angle from the railing shot. HUD on.
- `2026-10-11-s01-roof-d.jpg` — low along the blue rail. Different angle again. HUD on.

The four views are different held cameras of the same roof. Detail stays full because V is on that roof. Hiding V was not part of this pass, so a body in frame is expected. No crash, no teleport.
