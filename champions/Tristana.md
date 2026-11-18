# Tristana (2-cost AttackCaster) · `DA_Tristana19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Hyperpop, Hitmaker
- **HP** 550 / 990 / 1782 · **AD** 45 / 67.5 / 101.25 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 55
- **Unlock**: Get 5 kills with Hyperpop Active

### Ability: Head Banger

> Throw bombs at 3 nearby enemies and detonate them, each dealing 125/190/285 × AD + 15/20/30 × AP physical damage. The final blast deals 2 × PhysicalDamageCalc1 damage instead.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 45 | 67.5 | 101.25 |
| ADDamage | 125 | 190 | 285 |
| APDamage | 15 | 20 | 30 |
| FinalShotPercentOfNormalShot | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 125/190/285 × AD + 15/20/30 × AP
- `PhysicalDamageCalc2` = 2 × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Tristana19_Attack`: launch 0.2217 s (6.65 ticks); animation length 1.8333 s (55 ticks); release at base AS 0.2217 s (6.65 ticks)
- Attack projectile: DA_Tristana19_AutoAttackProjectile, speed 2250 units/s
- Spell `GA_Tristana19_Spell` (chrono `CD_Tristana19_CastAnim_Part1`): cast ends 1.2333 s (37 ticks), next attack can start 1.2667 s (38 ticks), mana lock removed 1.2333 s (37 ticks); ended by `FinishCasting via OnEventBegin:CD_Tristana19_CastAnim_FinalShot:Unlock`
  - notes: projectile (hit time depends on travel) ×15; rate from unresolved switch(Temp_int_Variable_2){0: Temp_real_Variable_3; 1: Temp_real_Variable_2; 2: Temp_real_Variable_1; 3: Temp_real_Variable; default: K2Node_Select_Default_2} ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Tristana19_Attack` | Chronos/Default | 1.7986 | LaunchAttack 0.2217, Unlock 0.7333 |
| `CD_Tristana19_HyperpopHypemeter_Intro` | Chronos/Default | 1 | StartHype 0.95 |
| `CD_Tristana19_HyperpopHypemeter_Outro` | Chronos/Default | 1.0006 | EndOutro 0.95 |
| `CD_Tristana19_CastAnim_FinalShot` | Chronos/Spell | 0.6571 | Unlock 0.6386 |
| `CD_Tristana19_CastAnim_Part1` | Chronos/Spell | 0.5531 | Fire 0.1549, Fire2 0.1738, Fire3 0.1906, Unlock 0.5454 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Tristana19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Tristana19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Tristana19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Tristana19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Tristana19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2217 s (6.65 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2250 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.2667 s (38 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.2333 s (37 ticks) | predicted | |
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

