# Ezreal (2-cost AttackCaster) · `DA_Ezreal19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Heartsteel, Encore
- **HP** 550 / 990 / 1782 · **AD** 40 / 60 / 90 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 35

### Ability: Bite the Bullet

> Fire a missile that marks the target, then fire a second blast that detonates it. The explosion deals 190/285/430 × AD + 30/45/70 × AP physical damage to the target and 0.33 × PhysicalDamageCalc1 physical damage to enemies within 1 hex.
> 
> Heartsteel Upgrade: Detonation deals 0.25 more damage. Every 3rd cast hits enemies in a 2 hex radius instead.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 40 | 60 | 90 |
| ADDamage | 190 | 285 | 430 |
| APDamage | 30 | 45 | 70 |
| AoEPercentDamage | 0.33 | 0.33 | 0.33 |
| HeartsteelStan_PercentIncreasedAbilityDamage | 0.25 | 0.25 | 0.25 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 190/285/430 × AD + 30/45/70 × AP
- `PhysicalDamageCalc2` = 0.33 × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Ezreal19_Attack`: launch 0.3371 s (10.11 ticks); animation length 2.7333 s (82 ticks); release at base AS 0.3371 s (10.11 ticks)
- Attack projectile: DA_Ezreal19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Ezreal19_Spell` (chrono `CD_Ezreal19_CastAnim`): cast ends 1.1667 s (35 ticks), next attack can start 1.2 s (36 ticks), mana lock removed 1.1667 s (35 ticks); ended by `FinishCasting via OnEventBegin:CD_Ezreal19_CastAnim2:Unlock`
  - notes: curve CT_Encore19.RecastEffectiveness input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_1), used star 2 ×1; projectile (hit time depends on travel) ×6

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Ezreal19_Attack` | Chrono | 2.7333 | LaunchAttack 0.3371, Unlock 1.0932 |
| `CD_Ezreal19_CastAnim` | Chrono | 0.7984 | Unlock 0.6663 |
| `CD_Ezreal19_CastAnim2` | Chrono | 0.4837 | Unlock 0.4781 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Ezreal19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Ezreal19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Ezreal19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Ezreal19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Ezreal19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3371 s (10.11 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.2 s (36 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.1667 s (35 ticks) | predicted | |
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

