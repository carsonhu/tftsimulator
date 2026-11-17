# Samira (2-cost AttackCaster) · `DA_Samira19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Classical, Renegade, Trickshot
- **HP** 550 / 990 / 1782 · **AD** 42 / 63 / 94.5 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 60
- **Unlock**: 2 items on a Classical, Renegade, or Trickshot Champion.

### Ability: Bullets N' Roses

> Passive: When Samira critically strikes an enemy, they become Captivated for 3 seconds.
> 
> Active: Fire 10 bullets at the current target, each dealing 4/6/9 × AP + 35/53/80 × AD damage.
> 
> Captivated enemies grant bonuses to Classical champions.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 42 | 63 | 94.5 |
| NumBullets | 10 | 10 | 10 |
| DamageAP | 4 | 6 | 9 |
| DamageAD | 35 | 53 | 80 |
| CaptivateDuration | 3 | 3 | 3 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 4/6/9 × AP + 35/53/80 × AD

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Samira19_Attack`: launch 0.2669 s (8.01 ticks), variants 0.2669, 0.267, 0.2693; animation length 2.9 s (87 ticks); release at base AS 0.2669 s (8.01 ticks)
- Attack projectile: DA_Samira19_AutoAttackProjectile, speed 2800 units/s
- Spell `GA_Samira19_Spell` (chrono `CD_Samira19_CastAnim`): cast ends 1.3333 s (40 ticks), next attack can start 1.3667 s (41 ticks), mana lock removed 1.3333 s (40 ticks); ended by `FinishCasting via OnEventBegin:CD_Samira19_CastAnim:Unlock`
  - notes: curve CT_Trickshot19.RichochetDamage input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_2), used star 2 ×1; curve CT_Trickshot19.NumRichochets input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_1), used star 2 ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Samira19_Attack` | CD_Samira19_Attack | 2.9 | LaunchAttack 0.2669, LaunchAttack 0.267, LaunchAttack 0.2693, Unlock 1.0533, Unlock 1.1067, Unlock 1.16 |
| `CD_Samira19_CastAnim` | CD_Samira19_CastAnim | 1.3385 | BeginFire 0.1962, EndFire 0.5712, Unlock 1.3105 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Samira19_TrickshotHandler`, `GA_Trickshot19_HandleAutoAttackBounce`, `GA_AutoAttack`, `GA_LaunchProjectileAttack_Trickshot19`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Samira19_Spell`, `GA_ShopEvents`, `GA_Samira19_CaptivateCritTracker`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Samira19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Samira19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Samira19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Samira19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2669 s (8.01 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2800 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.3667 s (41 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.3333 s (40 ticks) | predicted | |
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

