# Set 19 assumptions ledger

Every rule the Set 19 simulator relies on, what it rests on, and how far it has been checked. Champion worksheets
(`champions/<Name>.md`) refer to these by ID; a per-champion answer that departs from a global rule is recorded in
that champion's worksheet *and* noted here under the rule.

**Status words**
- **decided**: an owner decision, not a fact about the game.
- **from data**: read from the selected client build. True of the data; whether the game behaves that way is a
  separate question.
- **Set 18 verified**: measured exactly on Set 18 replays. Same engine (UE 5.7.4), so a reasonable prior, but not
  Set 19 evidence.
- **predicted**: worked out from client scripts or timelines; never compared with the game.
- **confirmed / refuted (Set 19)**: checked against Set 19 VODs; the evidence is cited.
- **open**: no basis yet.

Change a status only with evidence: cite the worksheet evidence row, VOD or replay that moved it.

## Decisions

| ID | Decision | Date | Notes |
|---|---|---|---|
| D1 | Numbers come from the selected client build. Patch notes, cards and CommunityDragon are cross-checks only; a disagreement is logged as a question, never silently resolved. | 2026-11-17 | The in-game card text is rendered from the same curve rows, so card and build agree by construction for any value the card shows. |
| D2 | The engine starts as a verbatim copy of set18 at 859db43. It changes only where Set 19 data or evidence requires, each change recorded here. | 2026-11-17 | set18's uncommitted edits were not copied. |
| D3 | Every PBE build is snapshotted automatically (scheduled task "TFT build snapshot", every 3 h). The user picks the build the simulator uses. | 2026-11-17 | A build that is never installed on this PC (the Riot Client skipped it) cannot be snapshotted. |
| D4 | Scope: every Set 19 shop unit whose game role is not a Tank role (role name contains "Tank"). 65 units in, 29 tanks out (`roster.json`). Units may be removed later if they can't be simulated realistically, with a dated reason. | 2026-11-17 | Annie, Elise and Lillia are MagicTank in the data, so they are out, although they play partly as casters. |
| D5 | Each champion is done one at a time, with VOD evidence for its timing questions before its timing is treated as known. | 2026-11-17 | |

## Data pipeline

| ID | Assumption | Status | Basis | How it could fail |
|---|---|---|---|---|
| P1 | The snapshot of a build is complete and faithful: every number the simulator uses is read, none edited. | from data | `tftDatamine/tools/snapshot_build.py`; per-build `manifest.json` records tool hashes and read problems (`read_problems` 2 on the first build, both movement-spline modules). | A tool bug misreads a value. The 18.5 hotfix diff reproduced the patch notes exactly (Set 18), which tested the curve-table reader. |
| P2 | The usmap (class layouts) fits the build. | from data | The first build has its own usmap (`usmap_is_this_build: true`). Later builds fall back to the newest usmap. | Riot changes a native class: read problems rise. Re-dump with `tftDatamine/tools/usmap_no_replay.ps1 -Install PBE` (admin). |
| P3 | Curve values between points follow each curve's own interpolation (step or linear). | from data | Fixed in set_dump on 2026-11-17 (Hyperpop's Health was wrong before). | Cubic curves are treated as linear (tangents not read). None in Set 19 so far. |
| P4 | Composite curve tables = their stored merged rows. | from data | Stored rows equal the parent merge in all 3 Set 19 composites. | |
| P5 | Ability text values without a column, inside a trait tier's line, mean that tier's column. | predicted | Matches the in-game reading for Collab (8% at 3, 20% at 5). | |
| P6 | The game build a VOD was played on is known. | open | Needs the patch/date shown in the VOD matched to `builds/index.json`. | PBE changes daily; a VOD from the wrong day measures the wrong build. |

## Game rules (global)

| ID | Rule | Status | Basis | Set 19 checks |
|---|---|---|---|---|
| G1 | The game advances in 30 Hz ticks; events land on tick boundaries: game time = ceil(t × 30) / 30. | Set 18 verified | tftDatamine timing work, 2026-11-16: replay event times. | open |
| G2 | Attack release (ranged) or hit (melee) = the attack chrono's `LaunchAttack` time × max(1, attack period / L), L = max(chrono length, animation end). The windup stretches when the attack period is longer than the animation, never compresses. | Set 18 verified (73% of 10,228 attacks exact) | `GA_AutoAttack` sets the chrono duration to the attack period. Exceptions: some early ranged releases (Sivir), Ashe 9 vs 8.05 ticks. | open, per champion Q4/Q5 |
| G3 | First attack: combat opens with a fresh attack, the first release one windup in (stationary ranged units). Melee units first close the distance (movement not modelled). | Set 18 verified (Karma 0.93 s, Cassiopeia 1.08 s) | set18 commit 34212fe. | open, per champion Q3 |
| G4 | Projectile travel = straight-line hex distance × ~215 units / projectile speed. | Set 18 verified (6 champions fit 212-217) | | open, per champion Q6 |
| G5 | The next attack can start one tick after the cast ends. Cast end = `FinishCasting`, else `K2_EndAbility`, else mana-lock removal, from the spell script run as a timeline. | Set 18 verified (52 of 66 spells exact) | `spell_timing.py`. 10 Set 18 spells vary by design (dashes, travel, targets). | open, per champion Q7 |
| G6 | Mana lock: no mana is gained from cast start until the script removes the mana lock (`ManaLockRemoved`). | predicted | Script timelines. Set 18's engine defaulted mana-lock length to the cast time. | open, per champion Q9 |
| G7 | Cast time and mana lock do not scale with attack speed unless the spell script reads attack speed. | Set 18 verified for the scripts that read AS (Warwick, Xayah, Nidalee); predicted for the rest | `reads_attack_speed` in each spell timeline (Set 19: flagged on Ziggs and Ashe in the first build). | open, per champion Q8/Q10 |
| G8 | Mana per attack and per second come from the unit's role (Caster 7 per attack + 2 per second; Marksman, Fighter, Assassin 10 per attack; Tank 5; Specialists use their own resource). | from data | `roles` in the build (`CT_Role_Stats`). | open, per champion Q2 |
| G9 | Mana from taking damage is not modelled: the dummies never attack. | decided (inherited from set18) | | |
| G10 | Excess mana after a cast: what happens to mana above the maximum? | open | | needs one clean VOD check |
| G11 | A cast counts as zero attacks for on-attack effects, attack counters and role mana, unless the spell's script launches or simulates an attack (`GE_SimulateLaunchAttack`, `IsAttack`, `AppliesOnHit` in the script hints). | predicted | Script hints in each worksheet. | open, per champion Q11 |
| G12 | HP by star = base × 1 / 1.8 / 3.24 (`CT_UnitStatMultiplier_PerStarLevel`). AD by star = the champion's own `AutoAttackDamage` row (not a global × 1.5). | from data | | The 3-star 4/5-cost flat bonuses (`CT_ThreeStarSpecialBonuses`) are not applied yet: meaning unverified. |
| G13 | Ability damage = curve coefficient × the stat named in the formula (AP and AD are multipliers; base AD = 1.0). | from data | `CalcComponent` formulas. | open, per champion Q13 |
| G14 | The spell timeline predictions assume 2-star (`STAR=2`), base attack speed, one pass through loops, and the script's default branch where it branches on runtime state. | predicted | `spell_timing.py` settings. Units with several cast versions (Ahri basic 0.998 s vs empowered 0.944 s unlock) list every timeline in their worksheet. | per champion |
| G15 | Fighters' attack speed bonus (5-30% by stage) is computed in game code (`TFTStageMagnitude`); the stage-to-value mapping is not in data. | open | Role data. | needs the in-game role text per stage, or a measurement |
| G16 | Unlock conditions don't affect the simulation: an unlockable unit is assumed available. | decided | | |

## Engine (set18 code carried over)

Filled in as the engine is reviewed and adapted. Each entry: what the set18 engine assumes, where, and whether it
holds for Set 19.

| ID | Engine behaviour | Where | Status for Set 19 |
|---|---|---|---|
| E1 | set18 per-champion timing constants (attack windup, repeat windup, cast time) were measured on 18.5 replays. | `champion.py` class attributes, `set18champs.py` | Not carried over: Set 19 values come from the build's timelines and VOD evidence per champion. |
