# Guinsoo's Rageblade · `DA_GuinsoosRageblade`

Implemented as `set19items.GuinsoosRageblade` (docstring cites the script). Stats `GE_GuinsoosRageblade_Base`
(10% AP, AttackSpeed MultiplyAdditive 1.1); the script starts a looping 1-second timer at activation and each expiry
adds `ASCounter` (7) to the item's Stack; `GE_GuinsoosRageblade_StackingAS` gives AttackSpeed MultiplyAdditive
0.01 x Stack.

## Questions

| # | Question | Prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | When is the first stack? | timer starts at activation; activation at combat start (Blue Buff's script tests phase 9 at elapsed < 0.01) → 1.000 s | **confirmed** | E1 |
| Q2 | Interval | 1 s (script literal) | **confirmed** | E1, E2, E3 |
| Q3 | AS per stack, and how it adds | +7% of base AS, additive with other AS (MultiplyAdditive) | **confirmed** (to the panel's 2 decimals, 15 steps) | E1 |
| Q4 | Does a stack land before or after an attack on the same tick? | engine: onUpdate before the attack phase (O5) | open | |

## Evidence log

Source: `Outplayed/…PBE_11-17-2026_16-35-16-966.mp4` (owner's PBE recording, 2026-11-17 16:22-16:35; build `rls-19.1.0.5973071`: game files dated 13:21-13:28, no newer build snapshotted), 1280x720 at **60 fps** (2 frames per game tick). Values read from the inspection panel's printed numbers (`tools/vod_text_changes.py`); frames are the video's own.

| # | Date | Build | Frames | fps | Measured | Values | Result | Q |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | f15365-16387 | 60 | Varus (1★, Blue Buff + Guinsoo's): combat start, AS steps | combat start f15365 (mana text 30 → 40 = Blue Buff's combat-start mana); AS text 0.77 until f15425, then changes at f15425, 15485, 15545, 15606, 15666, 15726, 15786, 15846, 15907, 15967, 16027, 16087, 16147, 16207, 16267, 16327, 16387 (60-61 frames apart) reading 0.82 0.87 0.92 0.97 1.01 1.06 1.11 1.16 1.21 1.26 1.31 1.36 1.41 1.46 1.50 1.55 1.60 | first stack +60 frames = 1.000 s after combat start; then every 1 s; AS = 0.70 x (1.10 + 0.07n) for n = 1..17 at every step | Q1, Q2, Q3 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | f20410-21089 | 60 | Neeko (Guinsoo's + Blue Buff), inspected mid-fight | AS 0.92 → 0.97 at f20470, then every 60-61 frames to 1.36; reset to 0.77 after combat | interval 1 s; values = 0.70 x (1.10 + 0.07n) | Q2 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | f26146-27984 | 60 | Senna (Blue Buff + Guinsoo's + 1) | AS text changes every 60-61 frames (values not read) | interval 1 s | Q2 |

## Notes

- 2026-11-17: set18 stacked at `time > 1` (the tick after 1.0 s); the VOD shows exactly 1.000 s, so set19 stacks on
  tick 30, 60, ... (ledger I4, O5).
