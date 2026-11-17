# Miss Fortune (5-cost AttackCaster) · `DA_MissFortune19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 5, pool 9; traits: 8-Bit, Hitmaker
- **HP** 900 / 1620 / 2916 · **AD** 80 / 120 / 180 · **AS** 0.8 · **Range** 4 · **Armor** 45 · **MR** 45 · **Mana** 0 / 50

### Ability: Pinball Wizard

> Fire a pinball towards the target, dealing 130/200/1337 × AD + 15/25/908 × AP physical damage. After hitting an enemy, it continues bouncing until damaging enemies 12 times, reducing its damage by 30% each hit. (Minimum damage: 20%)

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 80 | 120 | 180 |
| DamageReductionPerHit | 0.3 | 0.3 | 0.3 |
| 8BitMissFortuneBonusScoreMultiplier | 3 | 3 | 3 |
| DamageAmountPhysical | 130 | 200 | 1337 |
| DamageAmountMagic | 15 | 25 | 908 |
| PinballAimbotMaxAngleCheck | 30 | 30 | 30 |
| PinballBounceRandomAngleAmount | 25 | 25 | 25 |
| ProjectileSpeedIncrease | 0 | 0 | 0 |
| ProjectileSpeedMax | 0 | 0 | 0 |
| ProjectileSpeedBase | 0 | 0 | 0 |
| ProjectileHitNumBeforeExpire | 12 | 12 | 12 |
| MinimumDamagePercent | 0.2 | 0.2 | 0.2 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 130/200/1337 × AD + 15/25/908 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_MissFortune19_Attack`: launch 0.2664 s (7.99 ticks); animation length 2.6667 s (80 ticks); release at base AS 0.2664 s (7.99 ticks)
- Attack projectile: DA_MissFortune19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_MissFortune19_Spell` (chrono `CD_MissFortune19_CastAnim`): cast ends 1.0667 s (32 ticks), next attack can start 1.1 s (33 ticks), mana lock removed 1.0667 s (32 ticks); ended by `FinishCasting via OnEventBegin:CD_MissFortune19_CastAnim:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_MissFortune19_3StarCastanim` | Chronos/3Star | 15.3279 | LaunchProjectile 0.2033, LaunchProjectile 0.4707, LaunchProjectile 0.7301, LaunchProjectile 1.0053, LaunchProjectile 1.2696, LaunchProjectile 1.5369, LaunchProjectile 1.7964, LaunchProjectile 2.0716, LaunchProjectile 2.3326, LaunchProjectile 2.6, LaunchProjectile 2.8595, LaunchProjectile 3.1347, Unlock 15.0814 |
| `CD_MissFortune19_Attack` | Chronos | 2.6667 | LaunchAttackVariant2 0.2664, LaunchAttackVariant1 0.2664, Unlock 1.0667 |
| `CD_MissFortune19_CashoutCeremony` | Chronos | 3.9561 | Loot 1.9859 |
| `CD_MissFortune19_CastAnim` | Chronos | 1.0696 | LaunchProjectile 0.2862, Unlock 1.0482 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Play3Star5CostCamera`, `GA_ReduceOutgoing3StarDamage`, `GA_GainDamageReductionAt3Star`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_MissFortune19_Spell`, `GA_ShopEvents`, `GA_MissFortune19_SpellPinball`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_MissFortune19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_MissFortune19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_MissFortune19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_MissFortune19_Spell.txt

<!-- AUTO END -->

## Status

- Worksheet status: **not started**
- Keep in the simulator: **undecided** (remove if it can't be simulated realistically; give the reason)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | predicted | |
| Q2 | Mana per attack and per second follow the role | AttackCaster | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2664 s (7.99 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.1 s (33 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.0667 s (32 ticks) | predicted | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted | |
| Q14 | Passives and other mechanics that need modelling | see ability text | open | |
| Q15 | Can this unit be simulated realistically? | | open | |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| Date | Build | Source (VOD URL @ time) | fps | Measured | Frames / values | Result | Question |
|---|---|---|---|---|---|---|---|

## Decisions and notes

