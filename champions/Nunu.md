# Nunu & Willump (5-cost MagicSpecialist) · `DA_Nunu19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** MagicSpecialist: "Specialists generate resources in a unique way." ()
- **Cost** 5, pool 9; traits: Disco, Frontman
- **HP** 1200 / 2160 / 3888 · **AD** 15 / 23 / 34 · **AS** 0.5 · **Range** 1 · **Armor** 60 · **MR** 60 · **Mana** 20 / 75
- Other stats: MovementSpeed 300

### Ability: It's the Time to Disco!

> Passive: Gain 10/10/40 Mana Regen. Slowly roll around a Disco Ball, dealing 120/180/1500 × AP + 1 × MagicDamageCalc2 magic damage to all enemies it passes through.
> 
> Active: For the rest of combat, move faster and increase the size and damage of the Disco Ball by 30%/30%/200%.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 15 | 23 | 34 |
| ManaRegen | 10 | 10 | 40 |
| Damage | 120 | 180 | 1500 |
| MoveSpeed | 75 | 75 | 150 |
| SizeDamageIncrease | 0.3 | 0.3 | 2 |
| DamageCooldown | 1 | 1 | 1 |
| MaxMovementSpeed | 900 | 900 | 1200 |
| MinMovementSpeed | 250 | 250 | 250 |
| BeamDamage | 1000 | 1000 | 1000 |
| SilvermereDawnMSPercentReduction | 0.6 | 0.6 | 0.6 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 120/180/1500 × AP + 1 × MagicDamageCalc2
- `MagicDamageCalc2` = 0.3/0.3/2 × Stack + 1
- `MagicDamageCalc3` = 1000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `–`: launch –; animation length –; release at base AS –
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Nunu19_Spell` (chrono `CD_Nunu19_BallGrow`): cast ends 0.6 s (18 ticks), next attack can start 0.6333 s (19 ticks), mana lock removed 0.6 s (18 ticks); ended by `FinishCasting via OnEventBegin:CD_Nunu19_BallGrow:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Nunu19_BallGrow` | Chronos | 1.0001 | Unlock 0.6 |
| `CD_Nunu19_CastingDiscoBall` | Chronos | 14.2648 | Default 0, LaunchProjectile 0.6, DanceBegin 1.2, DanceLoopBegin 3.0309, DanceLoopEnd 8.0331 |
| `CD_Nunu19_ThreeStarDiscoFloor` | Chronos | 4 | Default 0, LoopEnd 1.6 |
| `CD_Nunu19_UniqueTrait_BoardDiscoFever` | UniqueTrait/Chronos | 2 | DiscoFever 0.2997 |

### Scripts on the unit

`GA_Nunu19_Passive`, `GA_RoamingMovement_LaunchMeleeAttack`, `GA_RoamingMovement`, `GA_Celebration`, `GA_Death`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Play3Star5CostCamera`, `GA_Nunu19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Nunu19_Passive.txt, Abilities/GA_Nunu19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Nunu19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: UniqueTrait/Abilities/GA_Nunu19_UniqueTrait_TakedownManager.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicSpecialist | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | – | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 0.6333 s (19 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.6 s (18 ticks) | predicted | |
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

