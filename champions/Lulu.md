# Lulu (2-cost MagicCaster) · `DA_Lulu19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5995286.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5995286.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Hyperpop, Choreographer
- **HP** 550 / 990 / 1782 · **AD** 35 / 52.5 / 78.75 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 40
- **Unlock**: Have your Hyperpop Champions cast 10 times with the trait active.

### Ability: Hype Girl

> Rotate between 2 effects:
> 
> Whimsy!: Grant an ally 0.45/0.55/0.65 × AP + 0.35 decaying Attack Speed and 20/30/45 × AP magic damage on hit for 5 seconds. 
> 
> Wild Growth: Increase an ally's Health by 175/260/395 × AP for 5 seconds. While active, adjacent enemies take 20/30/45 × AP magic damage each second.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 35 | 52.5 | 78.75 |
| WildGrowthHealth | 175 | 260 | 395 |
| Damage | 400 | 600 | 900 |
| WhimsyDuration | 5 | 5 | 5 |
| WildGrowthDuration | 5 | 5 | 5 |
| WhimsyASFlat | 0.35 | 0.35 | 0.35 |
| WhimsyAS_AP | 0.45 | 0.55 | 0.65 |
| WildGrowthTickInterval | 1 | 1 | 1 |
| WildGrowthPerTickDamage | 20 | 30 | 45 |
| WhimsyMagicDamageBonus | 20 | 30 | 45 |

Formulas (as stored; AD and AP are multipliers):

- `AttackSpeedCalc1` = 0.45/0.55/0.65 × AP + 0.35
- `HealthCalc1` = 175/260/395 × AP
- `MagicDamageCalc1` = 400/600/900 × AP
- `GenericCalc1` = 5 ÷ 1 + 1
- `MagicDamageCalc2` = 20/30/45 × AP
- `MagicDamageCalc3` = 20/30/45 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Lulu19_Attack`: launch 0.3 s (9 ticks); animation length 1.1 s (33 ticks); release at base AS 0.3636 s (10.91 ticks)
- Attack projectile: DA_Lulu19_AutoAttackProjectile, speed 1450 units/s
- Spell `GA_Lulu19_Spell` (chrono `–`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_Encore19.RecastEffectiveness input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast), used star 2 ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Lulu19_Attack` | Chronos | 1.0005 | LaunchAttack 0.3, Unlock 0.6, Unlock 0.7 |
| `CD_Lulu19_HyperpopHypemeter_Intro` | Chronos | 1 | StartHype 0.95 |
| `CD_Lulu19_HyperpopHypemeter_Outro` | Chronos | 0.5108 | EndOutro 0.485 |
| `CD_Lulu19_Whimsy` | Chronos | 1 | Unlock 0.987 |
| `CD_Lulu19_WhimsySelf` | Chronos | 1 | SelfCast 0.3971, EncoreSelfCast 0.6855 |
| `CD_Lulu19_WhimsyTar` | Chronos | 5.5 | Default 0, Loop 0.1004 |
| `CD_Lulu19_WildGrowth` | Chronos | 1 | UpWeGo 0.3045, EncoreUpWeGo 0.5305 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Lulu19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Lulu19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: GA_Lulu19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Lulu19_Spell.txt
- `AppliesOnHit`: something in the script is flagged as applying on-hit effects: GA_Lulu19_Whismy.txt
- `IsAttack`: damage flagged as an attack (or checked for it): GA_Lulu19_Whismy.txt

### Changed since `rls-19.1.0.5986094.Set19.Shipping.pbe`

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3 s (9 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1450 | predicted | |
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

