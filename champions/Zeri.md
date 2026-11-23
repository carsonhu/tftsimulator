# Zeri (5-cost AttackCaster) · `DA_Zeri19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6018196.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6018196.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Goth, Swiftstriker
- **HP** 900 / 1620 / 2916 · **AD** 60 / 90 / 135 · **AS** 0.8 · **Range** 4 · **Armor** 45 · **MR** 45 · **Mana** 0 / 150

### Ability: Lasers After Midnight

> Quickly dash around the arena, aiming 6 lasers at the current target. Lasers fire in rapid succession, each dealing 30/45/500 × AP + 135/200/1000 × AD physical damage to enemies hit and ignoring 40% of their Armor.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 60 | 90 | 135 |
| LaserDamageAP | 30 | 45 | 500 |
| LaserDamageAD | 135 | 200 | 1000 |
| NumLasers | 6 | 6 | 6 |
| BonusTankDamage | 0 | 0 | 0 |
| BonusFighterDamage | 0 | 0 | 0 |
| UniqueTraitHealthThreshold | 0 | 0 | 0 |
| ArmorPen | 0.4 | 0.4 | 0.4 |
| UniqueTraitADSteal | 0.08 | 0.08 | 0.08 |
| SimulateAutoEveryXLasers | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 30/45/500 × AP + 135/200/1000 × AD
- `GenericCalc1` = 1 + -0.4

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Zeri19_Attack`: launch 0.0759 s (2.28 ticks), variants 0.0759, 0.1996; animation length 1.0667 s (32 ticks); release at base AS 0.0889 s (2.67 ticks)
- Attack projectile: DA_Zeri19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Zeri19_Spell` (chrono `CD_Zeri19_CastAnim_new`): cast ends 2.9667 s (89 ticks), next attack can start 3 s (90 ticks), mana lock removed 2.9667 s (89 ticks); ended by `FinishCasting via OnEventBegin:CD_Zeri19_CastAnim_new:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Zeri19_3Star_HopToCenterIntoCelebrate` | Chronos | 3.3894 | Default 0, Windup 0.5583, Arrived 0.9289, Loop 1.7858 |
| `CD_Zeri19_Attack` | Chronos | 1.0333 | LaunchAttack 0.0759, LaunchAttack 0.1996, Unlock 0.62,  0.64 |
| `CD_Zeri19_CastAnim_3Star` | Chronos | 3.016 | Default 0, FaceTarget 0.6237, Movement 0.9991, Start1 1, Start2 1.1, Start3 1.2, Start4 1.3, Start5 1.4, Start6 1.5, LastMoveDone 1.59, DoneMovement 1.5999 |
| `CD_Zeri19_CastAnim_new` | Chronos | 3.016 | Default 0, Movement 0.9991, Start1 1, Start2 1.1, Start3 1.2, Start4 1.3, Start5 1.4, Movement2 1.4998, Start6 1.5, LastMoveDone 1.59, DoneMovement 1.9009, Telegraph 2.1073, Boom 2.4159, Unlock 2.9572 |
| `CD_Zeri19_Celebration` | Chronos | 2.2579 | Default 0, loop 0.7013 |
| `CD_Zeri19_CloneShoot` | Chronos | 0.7986 | Shoot 0 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Zeri19_AAVisuals`, `GA_Play3Star5CostCamera`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Zeri19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Zeri19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Zeri19_AAVisuals.txt, GA_Zeri19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Zeri19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Zeri19_Spell.txt

### Changed since `rls-19.1.0.6011486.Set19.Shipping.pbe`

- row LaserDamageAD: 145 / 215 / 1000 -> 135 / 200 / 1000
- ability text changed

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.0759 s (2.28 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 3 s (90 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2.9667 s (89 ticks) | predicted | |
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

