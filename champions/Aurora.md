# Aurora (4-cost MagicCaster) · `DA_Aurora19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Ionic Spark, Renegade
- **HP** 850 / 1530 / 2754 · **AD** 35 / 67.5 / 101.25 · **AS** 0.75 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 0 / 60

### Ability: Between Worlds Apart

> Blink away and fire a blast through the best line. The blast deals 275/415/2000 × AP magic damage to the 2 highest Health enemies, and 90/135/1500 × AP magic damage to the rest. Then, blink back.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 35 | 67.5 | 101.25 |
| PrimaryDamageAP | 275 | 415 | 2000 |
| AOEDamageAP | 90 | 135 | 1500 |
| MaximumHexMove | 10 | 10 | 10 |
| MinimumHexMove | 0 | 0 | 0 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 90/135/1500 × AP
- `MagicDamageCalc2` = 275/415/2000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Aurora19_Attack`: launch 0.3348 s (10.04 ticks), variants 0.3348, 0.3365; animation length 2.6 s (78 ticks); release at base AS 0.3348 s (10.04 ticks)
- Attack projectile: DA_Aurora19_AutoAttackProjectile, speed 1250 units/s
- Spell `GA_Aurora19_Spell` (chrono `CD_Aurora19_CastAnim`): cast ends 2.0333 s (61 ticks), next attack can start 2.0667 s (62 ticks), mana lock removed 2.0333 s (61 ticks); ended by `FinishCasting via OnEventBegin:CD_Aurora19_CastAnim:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Aurora19_Attack` | CD_Aurora19_Attack | 2.6 | LaunchAttack 0.3348, LaunchAttack 0.3365, Unlock 1.04 |
| `CD_Aurora19_CastAnim` | CD_Aurora19_CastAnim | 0.4985 | Retargetable1 0.0177, Mark 0.0612, Damage 0.1821, ResetChronoTarget 0.2784, Untargetable2 0.3686, Retargetable2 0.4027, Untargetable1 0.4358, Unlock 0.4853 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Aurora19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Aurora19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Aurora19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3348 s (10.04 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1250 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 2.0667 s (62 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2.0333 s (61 ticks) | predicted | |
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

