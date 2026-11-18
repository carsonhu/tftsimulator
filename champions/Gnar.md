# Gnar (1-cost HybridSpecialist_Ammo) · `DA_Gnar19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** HybridSpecialist_Ammo: "Specialists generate resources in a unique way." ()
- **Cost** 1, pool 30; traits: Pentakill, Trickshot
- **HP** 500 / 900 / 1620 · **AD** 40 / 60 / 90 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 0 / 3

### Ability: Hard Rock

> Passive: Every 3rd attack is replaced with a rock that deals 120/180/270 × AD physical damage and grants Gnar 0.09 × AP + 1 Attack Speed.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 40 | 60 | 90 |
| ADDamage | 120 | 180 | 270 |
| AttackSpeedAP | 0.09 | 0.09 | 0.09 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 120/180/270 × AD
- `AttackSpeedCalc1` = 0.09 × AP + 1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Gnar19__Attack`: launch 0.2678 s (8.03 ticks); animation length 1.9667 s (59 ticks); release at base AS 0.2678 s (8.03 ticks)
- Attack projectile: DA_Gnar19_AutoAttackProjectile, speed 1500 units/s
- No spell timeline decoded (no spell ability, or the script never reaches a cast end).

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Gnar19__Attack` | Chronos | 1.2333 | LaunchAttack 0.2678, CustomLaunchAttack1 0.38, Unlock 0.4932, Unlock 0.7864 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Trickshot19_HandleAutoAttackBounce`, `GA_PlayChronoOnTraitActivation`, `GA_AutoAttack`, `GA_LaunchProjectileAttack_Trickshot19`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Gnar19_Passive`, `GA_ShopEvents`, `GA_Gnar19_TrickshotHandler`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- `AppliesOnHit`: something in the script is flagged as applying on-hit effects: GA_Gnar19_Passive.txt
- `IsAttack`: damage flagged as an attack (or checked for it): GA_Gnar19_Passive.txt
- `LaunchAttack`: launches or listens for attacks: GA_Gnar19_Passive.txt
- `AttackSpeed`: reads or changes attack speed: GA_Gnar19_Passive.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: GA_Gnar19_TrickshotHandler.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Gnar`, D1); Ammo, attack speed and rhythm checked against VOD3
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (2★: 900 HP, 60 AD, 0.7 AS, armor/MR 25, Ammo 0/3; with his items exactly the panel) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | HybridSpecialist_Ammo | confirmed: no mana; the bar is Ammo, +1 per launch, reset after the rock | E2, D1 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2678 s (8.03 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | consistent: the rock's 0.38 s windup stretched at AS 0.77 (gaps 43.5 before, 33 after a rock) | E2 |
| Q6 | Projectile travel time (ranged only) | speed 1500 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | no spell timeline | not applicable (no spell) | D1 |
| Q8 | Does the cast time scale with attack speed? | no spell timeline | not applicable | D1 |
| Q9 | Mana lock: from cast start, when can mana be gained again? | no spell timeline | not applicable | D1 |
| Q10 | Does the mana lock scale with attack speed? | no spell timeline | not applicable | D1 |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | not applicable; the rock is itself an attack launch (LaunchAttack.Custom.1) and an on-hit hit | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | not applicable | D1 |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read: D1); no rock damage number read yet | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | the rock every 3rd attack, its attack speed stacks, its Trickshot ricochets (D1); Pentakill AD/AP (B25) | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD3 (`…PBE_11-17-2026_17-13-37-283.mp4`, 60 fps), the owner's PBE recording, build
`rls-19.1.0.5973071`; Gnar 2★, round 1-4, panel open 4:10-4:34 (f15000-16440).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 4:10-4:27 | 60 | inspection panel | planning 900/900, 0/3; in combat 1050 HP, AD 81 (+35%), AS 0.77, crit 80%, damage amp 10% (then 15, 25, 30%), armor/MR 25; Infinity Edge + Striker's Flail (owner) | 2★ as built with the items: HP 900 + 150, AS 0.7 x 1.1, crit 25 + 35 + 20, AD +35%, amp 10% + Flail's crit stacks | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 f15620-16359 (`tools/vod_text_changes.py`, mana and as) | 60 | Ammo text and AS | Ammo 1, 2, 3, 0 at f15728, 15805, 15892, 15912; 15958, 16030, 16108, 16128; 16171, 16269, 16341, 16359. AS 0.77 -> 0.83 (f15892) -> 0.90 (f16108) -> 0.96 (f16341) | launch gaps 38.5, 43.5, 33, 36, 39, 31.5 ticks; engine (`test_gnar.py`) 39, 43, 32, 36, 39, 30. AS +0.063 (0.7 x 0.09 at AP 0%) at each rock. Ammo reset 10, 10, 9 ticks after the rock (0.3 / AS: 10.8, 10.0, 9.4). One gap of 49 ticks (engine 34): a walk or retarget | Q2, Q5, Q14 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Gnar`):
  - **Ammo and the rock (GA_Gnar19_Passive):** no mana; every attack launch adds Ammo, the second sets
    ChronoTags.Dynamic.CustomAttack.1, so every 3rd attack plays the attack chrono's SpecialAttack group
    (CustomLaunchAttack1 0.38 s of 1.2333 s, rate-scaled: stretched when the period is longer, G2) and throws the rock
    (CD_Gnar19_Projectile, 1800) instead of an attack projectile. At that launch: GE_Gnar19_AttackSpeedBuff,
    AttackSpeed MultiplyAdditive (0.09 x AP + 1), infinite and stacking.
  - **Rock damage:** GE_Gnar19_PhysicalDamage = ADDamage x AD (the AttackDamage multiplier, as for Varus), physical,
    AppliesOnHit.IsAttack + AppliesOnSpell: on-hit effects apply; crits only with Precision.
  - **Trickshot:** his normal attacks ricochet as every Trickshot's (B12); the rock ricochets through
    GA_Gnar19_TrickshotHandler (CD_Gnar19_Projectile_TrickshotBounce, 1800) at RichochetDamage^k. The generic attack
    ricochet does not fire on the rock.
  - **Rhythm:** the B13 rule for units with several attack animations (starts a period apart, each releasing its own
    windup later) reproduces VOD3 within 1.5 ticks.
  - **Mana from items** (Shojin, Blue Buff...) adds no Ammo: Ammo is not meant to be filled by mana (owner,
    2026-11-18); he never casts.

