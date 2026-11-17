# Senna (3-cost AttackCaster) · `DA_Senna19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 3, pool 18; traits: True Damage, Hitmaker
- **HP** 650 / 1170 / 2106 · **AD** 55 / 82.5 / 123.75 · **AS** 0.75 · **Range** 4 · **Armor** 35 · **MR** 35 · **Mana** 0 / 20

### Ability: Reverberation Devastation

> Blast the target, dealing 140/210/340 × AD + 25/35/60 × AP physical damage and marking them. If they are marked, detonate it instead, dealing 1.5 × PhysicalDamageCalc1 damage.
> 
> On detonation or killing a marked enemy, gain 8% Damage Amp until the end of combat.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 55 | 82.5 | 123.75 |
| SpellAD | 140 | 210 | 340 |
| BonusDA | 0.08 | 0.08 | 0.08 |
| SpellAP | 25 | 35 | 60 |
| Duration | 10 | 10 | 10 |
| AOERange | 1 | 1 | 1 |
| MarkerPercentOfSpellAD | 1.5 | 1.5 | 1.5 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 140/210/340 × AD + 25/35/60 × AP
- `PhysicalDamageCalc2` = 1.5 × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Senna19_Attack`: launch 0.531 s (15.93 ticks), variants 0.531, 0.6364; animation length 3.3 s (99 ticks); release at base AS 0.531 s (15.93 ticks)
- Attack projectile: DA_Senna19_AutoAttackProjectile, speed 4000 units/s
- Spell `GA_Senna19_Spell` (chrono `CD_Senna19_CastAnim1`): cast ends 1.2 s (36 ticks), next attack can start 1.2333 s (37 ticks), mana lock removed 1.2 s (36 ticks); ended by `FinishCasting via OnEventBegin:CD_Senna19_CastAnim1:Unlock`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Senna19_Attack` | Chronos | 3.3 | LaunchAttack 0.531, LaunchAttack 0.6364, Unlock 1.2, Unlock 1.32 |
| `CD_Senna19_CastAnim1` | Chronos | 1.2546 | Unlock 1.1984 |
| `CD_Senna19_CastAnim2` | Chronos | 1.0002 | Damage 0.2851, Unlock 0.9864 |
| `CD_Senna19_FastYoink` | Chronos | 0.7728 | Lock 0, Unlock 0.5056 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_TrueDamage19_PlayChronoOnTraitActivation`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Senna19_Spell`, `GA_ShopEvents`, `GA_Senna19_MarkDeathTracker`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Senna19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Senna19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Senna19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Senna19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.531 s (15.93 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 4000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.2333 s (37 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.2 s (36 ticks) | predicted | |
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

