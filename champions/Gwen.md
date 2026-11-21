# Gwen (5-cost MagicFighter) · `DA_Gwen19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** MagicFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Ionic Spark, Melodic Heart
- **HP** 1200 / 2160 / 3888 · **AD** 10 / 15 / 22.5 · **AS** 0.8 · **Range** 2 · **Armor** 60 · **MR** 60 · **Mana** 0 / 100
- **Unlock**: Ionic Spark fans cheer 250 times.

### Ability: Glimmer in the Night

> Passive: Attacks deal 60/90/1000 × AP bonus magic damage to the target and 22/35/500 × AP to other enemies in a cone. Dash to new targets.
> 
> Active: Summon a massive pair of scissors over the battlefield. After a short delay, snip a horizontal line on the target, dealing 90/135/4000 × AP magic damage to all enemies hit + 830/1300/8000 × AP split between them. If 1 or fewer enemies are hit, refund 50/50/200 Mana.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 10 | 15 | 22.5 |
| BonusAutoDamageAP | 60 | 90 | 1000 |
| BonusConeDamageAP | 22 | 35 | 500 |
| RowDamageAP | 90 | 135 | 4000 |
| SplitDamageAP | 830 | 1300 | 8000 |
| RecastEffectiveness | 0 | 0 | 0 |
| UniqueTraitHexRange | 1 | 1 | 1 |
| UniqueTraitDR | 0.1 | 0.1 | 0.1 |
| UniqueTraitSeconds | 12 | 12 | 12 |
| RefundManaAmount | 50 | 50 | 200 |
| RefundManaNumEnemies | 1 | 1 | 1 |
| ConeOnHitEffectiveness | 0.3 | 0.3 | 0.3 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 60/90/1000 × AP
- `MagicDamageCalc2` = 22/35/500 × AP
- `MagicDamageCalc3` = 90/135/4000 × AP
- `GenericCalc1` = 830/1300/8000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Gwen19_Attack`: launch 0.3377 s (10.13 ticks); animation length 3.0666 s (92 ticks); release at base AS 0.3377 s (10.13 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Gwen19_Spell` (chrono `CD_Gwen19_CastAnim_new`): cast ends 1.9667 s (59 ticks), next attack can start 2 s (60 ticks), mana lock removed 1.9667 s (59 ticks); ended by `FinishCasting via OnEventBegin:CD_Gwen19_CastAnim_new:RecastCheck`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Gwen19_3Star_CopiesPopOut` | 3Star | 0.2998 | Arrived 0.2998 |
| `CD_Gwen19_Attack` | Chronos | 3.0666 | LaunchAttack 0.3377, Unlock 1.2267 |
| `CD_Gwen19_CastAnim_3Star` | Chronos | 2.4703 | BigSnipSpawn 0, SNIP 1.4838, RecastCheck 2.4513 |
| `CD_Gwen19_CastAnim_new` | Chronos | 1.9539 | BigSnipSpawn 0, SNIP 1.4838, RecastCheck 1.9361 |
| `CD_Gwen19_DashMove` | Chronos | 0.2714 | Arrived 0.2667 |
| `CD_Gwen19_ScissorsAnimation` | Chronos | 2.6445 | BigSnipSpawn 0, SNIP 1.4846, ByeScissors 2.5279 |
| `CD_Gwen19_Scissors_3Star_SmallVersion` | Chronos | 3.63 | BigSnipSpawn 0, SNIP 1.4846, ByeScissors 2.7085 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_PlayChronoOnTraitActivation`, `GA_ReduceOutgoing3StarDamage`, `GA_Play3Star5CostCamera`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Gwen19_MoveToTargetDash`, `GA_Celebration`, `GA_Death`, `GA_Gwen19_Spell`, `GA_ShopEvents`, `GA_Gwen19_ConeAttack`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Gwen19_Spell.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: GA_Gwen19_ConeAttack.txt
- `LaunchAttack`: launches or listens for attacks: GA_Gwen19_ConeAttack.txt
- `GE_ManaLock`: applies mana lock: GA_Gwen19_Spell.txt
- `GE_UnitStopAttackingMovingCasting`: stops the unit attacking/moving/casting: GA_Gwen19_Spell.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

- nothing in this unit's data

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3377 s (10.13 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 2 s (60 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.9667 s (59 ticks) | predicted | |
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

