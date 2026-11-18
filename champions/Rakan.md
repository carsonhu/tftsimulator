# Rakan (5-cost MagicAssassin) · `DA_Rakan19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** MagicAssassin: "Attacks grant 10 Mana. Take 15% less damage from all enemies except the current target." (ManaPerAttack + 10; ManaMax at least 10; MovementSpeed + 200; Threat + -10)
- **Cost** 5, pool 9; traits: Boy Band, Choreographer
- **HP** 1450 / 2610 / 4698 · **AD** 65 / 97.5 / 146.25 · **AS** 0.9 · **Range** 2 · **Armor** 80 · **MR** 80 · **Mana** 0 / 55
- **Unlock**: Win 4 combats in a row at Level 8+ / Lose 3 combats in a row at Level 8+

### Ability: Fly like a Peacock

> Dash to a nearby group of enemies, then fling 8/8/32 feathers split amongst enemies within 1 hex, each dealing 100/180/2400 × AP magic damage.
> 
> The main Rakan hits enemies within 2 hexes and briefly knocks up them up.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 65 | 97.5 | 146.25 |
| NumFeathers | 8 | 8 | 32 |
| APDamage | 100 | 180 | 2400 |
| NumRepeatsBase | 0 | 0 | 99 |
| NumRepeatsPerKill | 0 | 0 | 0 |
| KnockupDuration | 0.5 | 0.5 | 0.5 |
| CloneHealthMulitiplier | 0.5 | 0.5 | 0.5 |
| CloneDamageMultiplier | 0.3 | 0.3 | 0.3 |
| NumClones | 2 | 2 | 9 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 100/180/2400 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Rakan19_Attack`: launch 0.3888 s (11.66 ticks), variants 0.3888, 0.3942; animation length 3.3333 s (100 ticks); release at base AS 0.3888 s (11.66 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Rakan19_Spell` (chrono `CD_Rakan19_Dash`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_Rakan19.NumRepeatsBase input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_2), used star 2 ×1; curve CT_Rakan19.NumRepeatsPerKill input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_1), used star 2 ×1; curve CT_Rakan19.KnockupDuration input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast), used star 2 ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Rakan19_Attack` | Chronos/Basic | 1.6013 | LaunchAttack 0.3888, LaunchAttack 0.3942, Unlock 1.0533, Unlock 1.068 |
| `CD_Rakan19_CastAnim` | Chronos/Spell | 1.1589 | KnockUp 0.4206, SpawnFeathers 0.4414, RemoveIndicator 0.5857, Unlock 1.1345 |
| `CD_Rakan19_Dash` | Chronos/Spell | 0.3489 | Default 0, LoopAnim 0.0995, Arrive 0.0996 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Play3Star5CostCamera`, `GA_ReduceOutgoing3StarDamage`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Rakan19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`, `GA_UnlockAbility_Rakan19_WinStreakMilestone`, `GA_UnlockAbility_Rakan19_LossStreakMilestone`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Rakan19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Rakan19_Spell.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicAssassin | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3888 s (11.66 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | – | open | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | open | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | open | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | open | |
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

