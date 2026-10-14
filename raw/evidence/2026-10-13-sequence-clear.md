# Sequence clear failed on the game frame

2026-10-13 23:59 local. ArcadeLink 0.1.11. Listener on 127.0.0.1:2078.

Preclear reply: removed Johnny Silverhand, missed empty, actors empty.
Place rank slot 1 Johnny Silverhand: actors at -1537.16, 1197.12, 57.01.
Player stayed at -1536.84, 1194.00, 57.01, facing_x -0.59, facing_y 0.80.
Clear reply: type clear, error failed, Johnny still in actors at the same point.

scripting.log:

- 23:59:07 clear begin / clear removed=1 missed=0 (the preclear)
- 23:59:13 clear begin
- 23:59:13 clear err init.lua:567: bad argument #2 to 'insert' (number expected, got string)

No frame.
