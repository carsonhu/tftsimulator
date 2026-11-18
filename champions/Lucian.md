# Lucian (2-cost AttackCaster) · `DA_Lucian19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Jazz, Hitmaker, Encore
- **HP** 550 / 990 / 1782 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 20

### Ability: Relentless Pursuit

> Dash to a nearby hex, then fire 2 shots at target that each deal 80/120/180 × AD + 8/12/18 × AP physical damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| ADDamage | 80 | 120 | 180 |
| APDamage | 8 | 12 | 18 |
| MinDashDistance | 1 | 1 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 80/120/180 × AD + 8/12/18 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Lucian19__Attack`: launch 0.2283 s (6.85 ticks), variants 0.2283, 0.262; animation length 1.5 s (45 ticks); release at base AS 0.2283 s (6.85 ticks)
- Attack projectile: DA_Lucian19_AutoAttackProjectile, speed 2800 units/s
- Spell `GA_Lucian19_Spell` (chrono `CD_Lucian19_Dash`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_Encore19.RecastEffectiveness input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast), used star 2 ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Lucian19_CastAnim` | Chronos | 0.9507 | Unlock 0.9298 |
| `CD_Lucian19_CastAnim_Encore` | Chronos | 0.8263 | Unlock 0.8029 |
| `CD_Lucian19_Dash` | Chronos | 1.3652 | Default 0, Arrive 0.0124, LoopAnim 0.0124 |
| `CD_Lucian19__Attack` | Chronos | 1.5 | LaunchAttackVariant1 0.2283, LaunchAttackVariant2 0.2283, LaunchAttackVariant1 0.262, LaunchAttackVariant2 0.262, Unlock 0.6 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Lucian19_Spell`, `GA_ShopEvents`, `GA_ForceSequentialAttack`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Lucian19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Lucian19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Lucian19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Lucian19_Spell.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Lucian`, D1); panel and the cast's rhythm checked against
  VOD1 (the dash ~4 ticks longer in the clip: open)
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed with his items (1★) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster | confirmed: 7 per attack (+2 Nashor's), 2/s | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2283 s (6.85 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2800 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | – | open | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | open | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | open | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | open | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | predicted: one GE_SimulateLaunchAttack per shot (2, or 4 with Encore) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read: D1); the panel's tooltip showed 90 = 80 x AD + 8 x 1.25 AP | D1, E1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | the Encore cast (2 more shots); Jazz (B31), Hitmaker, Encore implemented | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD1 (`…PBE_11-17-2026_15-16-17-933.mp4`, 30 fps: one frame per tick), the owner's PBE
recording (Tocker's Trials, a stationary target), build `rls-19.1.0.5973071`; Lucian 1★, round 1-7.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5973071 | VOD1 5:40 (f10200) | 30 | inspection panel, ability tooltip | 700/700, 0/20, 2/s; AD 30, AP 25%, AS 0.90, crit 45%, range 4; Nashor's Tooth, Guinsoo's Rageblade; Bodyguard (3), Heartsteel (1); Jazz, Hitmaker, Encore inactive. Tooltip: 90 = 80 x AD + 8 x AP | 550 + 150 HP, 0.75 x 1.2 AS, 25 + 20 crit, 10 + 15 AP: as built | Q1, Q13 |
| E2 | 2026-11-18 | rls-19.1.0.5973071 | VOD1 f10347-10760 (`tools/vod_text_changes.py`, mana) | 30 | mana text | +9 per attack (7 + Nashor's 2), +0.5 regen steps; casts on fills at f10380, 10454, 10525, (f10608 by regen), 10689; the overflow (2, 5, 7, 3) shown 37, 37, 38, 39 ticks after the filling attack; the next attack 46 after it (twice) | engine (Nashor's, Guinsoo's): lock 32 from the cast (a 1-hex dash, 4 ticks, + Unlock 28), next attack 41 after the fill. The clip's casts last ~4 ticks longer: a longer dash than MinDashDistance (the real board's safest hex) is likely (open) | Q2, Q7, Q9 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Lucian`):
  - **Spell (GA_Lucian19_Spell):** mana lock; a dash (CD_Lucian19_Dash, 2000 units/s, client asset: the build has no
    movement modules) to the safest hex at least MinDashDistance (1) away that keeps his target in range. On the
    default dummy layout every such hex is as safe, so the nearest (1 hex, 4 ticks). Its 'Arrive' fires the shots:
    CD_Lucian19_CastAnim (SpellMis at 0.1494 and 0.3282 s, 1800 units/s) or, with Encore active,
    CD_Lucian19_CastAnim_Encore (SpellMis at 0.1009 and 0.2018 s, EncoreMis at 0.2923 and 0.3834 s at
    RecastEffectiveness). Each shot fired is a GE_SimulateLaunchAttack. 80/120/180 x AD + 8/12/18 x AP physical,
    on-spell, crit only with Precision. The cast chrono's Unlock (0.9298 / 0.8029 s) ends the cast and the mana lock.

