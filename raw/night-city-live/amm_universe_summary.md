# AMM Universe Summary

- Generated from: `d:\night-city-live\catalog\amm_universe.sqlite`

## Table Counts

- `anim_refs`: 23
- `appearance_triggers`: 0
- `appearances`: 30069
- `blacklist_appearances`: 0
- `camera_ops`: 14
- `categories`: 61
- `components`: 1192
- `custom_appearances`: 3238
- `director_ops`: 61
- `entities`: 4363
- `entities_fts`: 4363
- `extraction_stats`: 30
- `favorites`: 0
- `favorites_apps`: 0
- `favorites_props`: 0
- `favorites_swap`: 0
- `locations`: 121
- `metadata`: 1
- `module_capabilities`: 2287
- `module_literals`: 1
- `overlay_items`: 9
- `paths`: 7407
- `photomode_poses`: 142
- `pose_refs`: 7
- `provenance`: 8
- `saved_appearances`: 0
- `saved_despawns`: 0
- `saved_lights`: 0
- `saved_props`: 0
- `settings`: 37
- `workspots`: 43765
- _(FTS5 internal tables `entities_fts_*` omitted from row counts above)_

## Category Distribution (entities)

- `Decor`: 558
- `Furniture`: 342
- `Build`: 306
- `Vegetation`: 306
- `Walls`: 226
- `Small Props`: 213
- `Fake NPCs`: 176
- `Misc. NPCs`: 171
- `Side Characters`: 161
- `Misc`: 154
- `Electronics`: 153
- `Flooring`: 137
- `Clothes`: 136
- `Ceilings`: 111
- `Food & Drink`: 107
- `FX & Effects`: 103
- `Vehicles`: 93
- `Neons & Holograms`: 91
- `Lights`: 75
- `Recreation`: 61
- `Big Props`: 59
- `Musical Instruments`: 53
- `Arasaka`: 50
- `Weapons`: 37
- `Valentinos`: 34
- `Cyberpsycho`: 32
- `NCPD`: 31
- `Media`: 25
- `Non Companions`: 25
- `Joytoys`: 23
- `Main Characters`: 23
- `Scavenger`: 21
- `Voodoo Boys`: 21
- `Animals`: 20
- `Maelstrom`: 20
- `Tyger Claws`: 19
- `Nomad`: 17
- `Barghest`: 15
- `NSFW`: 15
- `Mox`: 14
- `Militech`: 13
- `Ripperdoc`: 13
- `Samurai`: 12
- `Wraiths`: 12
- `Sound Effects`: 11
- `Cameos`: 10
- `6th Street`: 9
- `Fixer`: 9
- `NUSA`: 9
- `Ambient Lights`: 6
- `At Your Own Risk`: 6
- `Kang Tao`: 6
- `Trauma Team`: 6
- `Interactions`: 3
- `Netwatch`: 2
- `Custom Characters`: 1
- `Props`: 1

## Integrity Checks

- `appearances` with blank `entity_id` (collab/global style rows): 14
- `appearances` with no `entities` row on direct `entity_id` join: 21342
- `appearances` resolved via `v_appearances_resolved` (direct id or `paths` bridge): 9812
- Duplicate `entities.entity_name` groups: 0
- `workspots` with a matching extracted rig label (`v_workspots_linked_rig_ref`, distinct `anim_id`): 39236
- `workspots` with exact `anim_name` match to `anim_refs` (`v_workspots_linked_anim_ref`): 0
- `module_literals` rows (structured Lua lists): 1

## Query Examples

```sql
-- entity counts by category (join when cat label lives on categories)
SELECT COALESCE(c.cat_name, '(null)') AS cat_name, COUNT(1) AS n
FROM entities e
LEFT JOIN categories c ON c.cat_id = e.cat_id
GROUP BY e.cat_id
ORDER BY n DESC;

-- appearances for a record (prefer resolved view; includes paths bridge)
SELECT app_name, entity_path, resolution
FROM v_appearances_resolved
WHERE entity_path = 'AMM_Character.Silverhand' AND resolution != 'unresolved'
ORDER BY app_name ASC;

-- fuzzy entity lookup (requires FTS build; MATCH must use base table name)
SELECT e.entity_name, e.entity_path, e.entity_id
FROM entities_fts JOIN entities e ON e.rowid = entities_fts.rowid
WHERE entities_fts MATCH ?
LIMIT 25;

-- module-derived camera operations
SELECT op_name, source_file FROM camera_ops ORDER BY op_name;

-- director movement enum (parsed from director.lua)
SELECT name, values_json FROM module_literals WHERE name = 'movementTypes';

-- workspots ↔ extracted rig labels (ref_label matches workspots.anim_rig)
SELECT anim_id, anim_name, anim_rig, anim_key FROM v_workspots_linked_rig_ref LIMIT 25;

-- per extracted anim_ref: how many workspot rows share anim_name or anim_rig label
SELECT anim_key, workspot_rows_by_name, workspot_rows_by_rig_label
FROM v_anim_ref_workspot_usage WHERE workspot_rows_by_rig_label > 0 ORDER BY workspot_rows_by_rig_label DESC LIMIT 15;
```

## Notes

- `module_capabilities` contains parser-derived candidates from AMM Lua modules.
- `anim_refs`/`pose_refs`: string matches are heuristic; `rig:*` rows include `ref_label` (AMM display rig name) for joining `workspots.anim_rig`.
- Many `appearances` rows use scan ids that match `paths` but not `entities.entity_id`; use `v_appearances_resolved`.
- `entities_fts` has INSERT/UPDATE/DELETE triggers on `entities` so ad-hoc edits stay indexed.
