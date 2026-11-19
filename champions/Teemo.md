# Teemo (5-cost MagicCaster) · `DA_Teemo19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5986094.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5986094.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Hyperpop, Hype Man
- **HP** 900 / 1620 / 2916 · **AD** 55 / 82.5 / 123.75 · **AS** 0.8 · **Range** 4 · **Armor** 45 · **MR** 45 · **Mana** 0 / 100
- **Unlock**: Collect 900 Hyperpop Hype.

### Ability: Going Viral

> Passive: Attacks apply Viral, dealing 90/135/1337 × AP magic damage over 15 seconds. Infected enemies become zombies on death, seeking out unaffected enemies and exploding, dealing 70/105/800 × AP damage to adjacent enemies and applying Viral.
> 
> Active: Launch a mushroom that applies Viral to enemies in a 3 hex radius and deals 530/800/13337 × AP magic damage, reduced by 20% per hex away from the center.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 55 | 82.5 | 123.75 |
| ViralDuration | 15 | 15 | 15 |
| ZombieExplosionDamage | 70 | 105 | 800 |
| PercentReductionFromCenter | 0.2 | 0.2 | 0.2 |
| CastDamage | 530 | 800 | 13337 |
| ViralDamage | 90 | 135 | 1337 |
| DOTTickRate | 0.5 | 0.5 | 0.5 |
| AbilityCenterHexRange | 4 | 4 | 4 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 90/135/1337 × AP
- `MagicDamageCalc2` = 70/105/800 × AP
- `MagicDamageCalc3` = 530/800/13337 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Teemo19_Attack`: launch 0.3 s (9 ticks); animation length 2 s (60 ticks); release at base AS 0.3 s (9 ticks)
- Attack projectile: DA_Teemo19_AutoAttackProjectile, speed 1300 units/s
- Spell `GA_Teemo19_SpellNew` (chrono `CD_Teemo19_CastAnim`): cast ends 2.0333 s (61 ticks), next attack can start 2.0667 s (62 ticks), mana lock removed –; ended by `FinishCasting via OnChronoStopped:CD_Teemo19_CastAnim:None`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Teemo19_3Star5Cost_GrabEnemyTactician` | Champion/Chrono/3Star5Cost | 2 | Default 0, Wait 1.6 |
| `CD_Teemo19_3Star5Cost_LaunchEnemyTactician` | Champion/Chrono/3Star5Cost | 3.2 | Default 0, Boom 2 |
| `CD_Teemo19_3Star5Cost_Swing` | Champion/Chrono/3Star5Cost | 3.6 | Default 0, Swing 1.6, Launch 2.4808 |
| `CD_Teemo19_Attack` | Champion/Chrono/Basic | 1.5901 | LaunchAttack 0.3, Unlock 0.9 |
| `CD_Teemo19_HyperpopHypemeter_Intro` | Champion/Chrono/Hyperpop | 1 | StartHype 0.95 |
| `CD_Teemo19_HyperpopHypemeter_Outro` | Champion/Chrono/Hyperpop | 0.5485 | EndOutro 0.5207 |
| `CD_Teemo19_CastAnim` | Champion/Chrono/Spell | 2.004 | StartProjectile 0.8899, Unlock 1.9902 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_TriggerWhenPurchasedAfterBeingUnlockedandForcedInShop`, `GA_Teemo19_Passive`, `GA_Play3Star5CostCamera`, `GA_GainDamageReductionAt3Star`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Teemo19_SpellNew`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Champion/Abilities/GA_Teemo19_SpellNew.txt
- `AppliesOnHit`: something in the script is flagged as applying on-hit effects: Champion/Abilities/GA_Teemo19_Passive.txt
- `GE_ManaLock`: applies mana lock: Champion/Abilities/GA_Teemo19_SpellNew.txt
- `GE_UnitStopAttackingMovingCasting`: stops the unit attacking/moving/casting: Champion/Abilities/GA_Teemo19_ViralOnDeath.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

- row ViralDamage: 110 / 165 / 1337 -> 90 / 135 / 1337
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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3 s (9 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1300 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 2.0667 s (62 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | predicted | |
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

