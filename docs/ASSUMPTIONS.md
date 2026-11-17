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
| G17 | Mana regen (Caster 2 mana/s): paid continuously, per tick, or in steps (set18 used 0.25 s steps), and from t = 0? | open | | VOD: mana bar of an itemless Caster before its first attack |
| G18 | A unit must attack at least once between casts (set18 engine rule). | open | | VOD: any unit whose mana refills from regen alone |

## Timing core (2026-11-17)

The engine's tick rules (`timing.py`, `champion.py` `update`). They port tftFightSim's engine
(`tftFightSim/crates/engine/src/sim.rs`, `cast.rs`), which was fitted to and checked against the 18.5 replays, and
set18's replay findings (set18 commits a2a5fd3, 34212fe, 859db43). Tests: `test_timing.py` (local), one exact-tick
test per rule.

| ID | Rule as implemented | Status | Source | Set 19 check |
|---|---|---|---|---|
| T1 | The engine runs on whole 30 Hz ticks; items still receive `time` = tick / 30. `simulate`'s `frameRate` is ignored. | Set 18 verified (G1) | tftFightSim tick loop | G1 |
| T2 | Repeat attacks keep exact time: next release = this release + 30 / AS ticks, the fraction carried (AS 0.8: gaps alternate 38/37), rounded half up. The next attack starts one windup (G2) before its release. A fresh attack (combat start, after a cast, after a reset) releases one windup after it starts. | Set 18 verified | tftFightSim `attacks` (cadence between hits 91.7% exact on 18.5/18.6 replays) | Q4, Q5 |
| T3 | Attack mana: ranged units at the attack start, melee on the hit (default; `Timing.mana_at` overrides per champion). A ranged unit whose mana comes later pays at the start an attack whose mana fills the bar. | Set 18 verified | 18.5 replays via set18 34212fe (Hold = attack start) and 859db43 (Karma, LeBlanc, Veigar, Cinderling, Cassiopeia) | Q2 (add: when the mana is paid) |
| T4 | A full bar casts on the tick after it filled, from any source. A ranged attack under way when the cast starts still releases (unless `cast_cancels_attack`); any other attack in progress is lost. | Set 18 verified for the attack that fills the bar (melee: 1 tick after the hit; ranged: the tick after the filling attack's start). Predicted for bars filled by regen or items. | set18 a2a5fd3; tftFightSim cast rules | Q7, Q12 |
| T5 | After a cast: no attack starts until the cast lock ends, then a fresh attack starts. Mana is gained only when neither the cast lock nor the mana lock is running. Overflow mana is kept (G10). | Set 18 verified (locks); G10 open | tftFightSim `try_cast` / `gain_mana` | Q7, Q9 |
| T6 | Attack damage and the attack's item effects (`preAttack`, `onAttack`, `postAttack`) happen when it lands: melee at the hit, ranged at release + flight (G4). Delayed spell effects use `Champion.schedule(seconds, fn)` and land on `ticks_up(seconds)` after the current tick. | predicted (design) | | per champion: on-attack items at release or on landing? |
| T7 | Mana regen: 0.25 s steps from t = 0, each paid on the first tick at or after its time (set18's behaviour, now on the tick grid). | inherited (G17 open) | set18 | G17 |
| T8 | G18 is counted on attack starts: a cast needs an attack started since the last cast. | inherited (G18 open) | set18 | G18 |
| T9 | Locks that scale with attack speed scale by base AS / current AS. | predicted | Generic form of set18's AS-scaled casts; a champion whose script uses its own curve (Set 18: Xayah, Nidalee) overrides `Timing.scaled_locks`. | Q8, Q10 |
| C1 | set18 content still runs: its `castTime`, `manalockDuration`, `attackWindup` become a Timing at combat start, and its writes to `nextAttackTime`, `manalockTime`, `attack_progress` map onto the tick state. Its numbers and timings are Set 18's, not Set 19 evidence. | compatibility only | | remove with E16 |

## Engine (set18 code carried over)

Filled in as the engine is reviewed and adapted. Each entry: what the set18 engine assumes, where, and whether it
holds for Set 19.

| ID | Engine behaviour | Where | Status for Set 19 |
|---|---|---|---|
| E1 | set18 per-champion timing constants (attack windup, repeat windup, cast time) were measured on 18.5 replays. | `champion.py` class attributes, `set18champs.py` | Not carried over: Set 19 values come from the build's timelines and VOD evidence per champion. |

Engine review of 2026-11-17 (independent read of the imported engine; items marked *checked* were re-read by a
second pass). The status column says which are fixed (by the timing core, T-entries above).

| ID | Engine behaviour | Where | Conflict / question |
|---|---|---|---|
| E2 | Time is a float advanced by 1/30 each frame; events compare floats, so an event scheduled exactly on a tick can fire a tick late (2864 of 5600 sampled). Attack gaps at AS 1.0 come out 29/30/31 frames. | `simulator.py` frame loop (*checked*), `champion.py` `canAttack`, attack progress | **Fixed** (T1, T2). The remainder question is answered by the replays: it carries (T2). Statuses still compare float times (E10). |
| E3 | The fresh-attack windup is capped by the attack period (`min(attackWindup, attackTime())`), so it shrinks at high AS. | `champion.py` `freshAttackDelay` (*checked*) | **Fixed** (G2 in `Timing.release_ticks`). |
| E4 | One event per attack: damage, on-hit and mana all at once, no projectile travel. | `champion.py` `performAttack` | **Fixed** (T3, T6): start, release and landing are separate ticks. |
| E5 | Spell damage lands on the cast frame; a later hit needs a hand-written status. | `champion.py` `update` / `performAbility` | **Fixed** (T6): `schedule()`; champions must use it for delayed effects. |
| E6 | `manalockDuration = 0` means "use castTime", so a zero mana lock can't be expressed; mana-lock comparisons mix `>` and `<=`. | `champion.py` `update` (*checked*), `addMana`, `canCast` | **Fixed** for Set 19 (`Timing.mana_lock`, tick comparisons); kept in set18 compat only. |
| E7 | Mana regen ticks every 0.25 s from t = -0.001, off the 30 Hz grid, including a tick at t = 0. | `champion.py` | **On the tick grid** (T7); the step size and t = 0 tick stay open (G17). |
| E8 | `multiTargetSpell` builds `Attack(...)` with positional arguments that land in the wrong parameters (`canCrit="physical"`, `canOnHit=1`). | `champion.py` `multiTargetSpell` (*checked*) | Bug: use keyword arguments. |
| E9 | The crit counter fires on `> 1`, so at 100% crit the first crit effect comes on the second hit. | `champion.py` (*checked*) | Bug: `>= 1`. |
| E10 | Status bugs: `CritModifier` wear-off subtracts AS; Armor/MR reduction reapply the old value; several status classes raise TypeError (dead); wear-off on `>` (a tick late); DoT ticks snap to whole seconds. | `status.py` | Fix when the statuses are needed. |
| E11 | Star scaling AD × 1.5, HP × 1.8 hard-coded. | `champion.py` constructor | G12: take HP and AD per star from the build. |
| E12 | Crit defaults 25% / 140%, excess crit → crit damage, AS cap 5, precision +10%. | `champion.py`, `stats.py` | Not in the build's champion stats: needs a source per value (global data asset, VOD, or owner decision). |
| E13 | Roles: 13 hard-coded roles with mana 7/5/10, regen 2, Fighter AS table {2:5, 3:10, 4:20, 5:30}; Specialists get 0 mana. | `role.py`, `set18roles.py` | G8/G15: the build has 29 roles; read them from the build. The Fighter table has no data source. |
| E14 | AS-scaled cast time is per-champion content (`aspd_scaled_cast_time`). | `set18champs.py` | **Engine support added** (`Timing.lock_scales_with_as`, T9, set from the build); set18 content unchanged. |
| E15 | 60 fps is offered; some code hard-codes 1/30. | `sim_entry.py`, `simulator.py`, `status.py` | **Engine fixed at 30** (T1); the UI still offers 60 (ignored) until the UI is adapted. |
| E16 | Set 18 content inside the engine (Emblem/Blackthorn/N.O.V.A./Arbiter sweeps, meep/seraphim fields, `set18roles` import, Set 18 dummy tank). | `sim_core.py`, `champion.py`, `sim_entry.py` | Remove when the engine is adapted. |
| E17 | Overflow mana carries over, and mana gained inside the cast counts before the bar is spent. | `champion.py` `update` | G10, open. |
| E18 | A unit can cast only after at least one attack since its last cast. | `champion.py` `canCast` | New question G18. |
| E19 | Timing is spread over eight attributes (`castTime`, `manalockDuration`, `attackWindup`, `attackWindupRepeat`, `fillingAttackLead`, `attackWindupRatio`, `attackWindupLockout`, `freshAttackDelay`). | `champion.py` | **Fixed**: one `timing.Timing` per champion (`Timing.from_build`, every field's source in `Timing.source`). |
