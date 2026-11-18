# Blue Buff · `DA_BlueBuff`

Implemented as `set19items.BlueBuff`. Stats `GE_BlueBuff_Stats` (6 mana regen, 15% AP, 15% AD). The script, on
activation at combat start (phase 9, round time < 0.01 s), applies `GE_BlueBuff_StartingMana`: mana +
`StartingMana` (10), item source, AlwaysBank. Applied in preCombat, as set18's Blue Buff.

## Questions

| # | Question | Prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Combat-start mana | +10 at combat start | **confirmed** | E1 |
| Q2 | Mana regen | +6 / s (8 / s on a 2 / s caster) | **consistent** (panel shows 8/s) | E1 |
| Q3 | Does the +10 go through mana multipliers (Adaptive Helm)? | yes (engine: `addMana`) | open | |

## Evidence log

Source: `Outplayed/…PBE_11-17-2026_16-35-16-966.mp4` (owner's PBE recording, 2026-11-17 16:22-16:35; build `rls-19.1.0.5973071`: game files dated 13:21-13:28, no newer build snapshotted), 1280x720 at **60 fps** (2 frames per game tick). Values read from the inspection panel's printed numbers (`tools/vod_text_changes.py`); frames are the video's own.

| # | Date | Build | Frames | fps | Measured | Values | Result | Q |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | f15340-15390 | 60 | Varus (1★, Blue Buff + Guinsoo's) mana text | 30/70 until f15364 (his ManaStarting 30), 40/70 on f15365, then 42 (f15373, regen), 49 (f15381, attack +7), 51 (f15387); regen shown as 8/s | +10 exactly at combat start; regen 2 + 6 | Q1, Q2 |

## Notes

- Neeko with Blue Buff + Guinsoo's (f20438) showed max mana 36, not 40. Not Blue Buff (it has no ManaMax
  modifier): the K/DA trait's first tier, (3) POP/STARS, "0.1 reduced max Mana" (`ManaReduction` 0.1):
  40 x 0.9 = 36 (owner, 2026-11-17; see champions/Neeko.md).
