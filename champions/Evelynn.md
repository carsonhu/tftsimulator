# Evelynn (3-cost MagicFighter) · `DA_Evelynn19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6005555.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6005555.Set19.Shipping.pbe`

- **Role** MagicFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 3, pool 18; traits: K/DA, Renegade
- **HP** 850 / 1530 / 2754 · **AD** 30 / 45 / 67.5 · **AS** 0.8 · **Range** 1 · **Armor** 50 · **MR** 50 · **Mana** 0 / 40
- **Unlock**: 3 unique K/DA or Renegade champions.

### Ability: Villainous

> Passive: At combat start, teleport behind the current target, then become enshrouded for 15 seconds. While enshrouded, become untargetable to attacks and gain 50% Durability if at least 3 other allies are alive.
> 
> Active: Deal 230/345/550 × AP magic damage to the current target and 90/135/215 × AP magic damage to other enemies in a semicircle. Ignore 40% of enemy Magic Resist.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| DamageTarget | 230 | 345 | 550 |
| PassiveDurability | 0.5 | 0.5 | 0.5 |
| PassiveNumAllies | 3 | 3 | 3 |
| DamageNonTarget | 90 | 135 | 215 |
| SemiCircleHex | 1.5 | 1.5 | 1.5 |
| MRPercentIgnore | 0.4 | 0.4 | 0.4 |
| PassiveDuration | 15 | 15 | 15 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 230/345/550 × AP
- `MagicDamageCalc2` = 90/135/215 × AP
- `GenericCalc1` = 1 + -0.4

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Evelynn19_Attack`: launch 0.3514 s (10.54 ticks); animation length 2.3333 s (70 ticks); release at base AS 0.3514 s (10.54 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Evelynn19_Spell` (chrono `CD_Evelynn19_SpellRepositionDash`): cast ends 0.6 s (18 ticks), next attack can start 0.6333 s (19 ticks), mana lock removed 0.6 s (18 ticks); ended by `FinishCasting via OnChronoStopped:CD_Evelynn19_Spell:None`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Evelynn19_Attack` | Chronos | 2.3 | LaunchAttack 0.3514, Unlock 0.932 |
| `CD_Evelynn19_CombatStartDash` | Chronos | 0.3403 | Arrive 0.15 |
| `CD_Evelynn19_Spell` | Chronos | 0.5995 | EndFizzle 0.1803, Damage 0.2042 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayChronoOnTraitActivation`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Evelynn19_Spell`, `GA_ShopEvents`, `GA_Evelynn19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Evelynn19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Evelynn19_Spell.txt

### Changed since `rls-19.1.0.5995286.Set19.Shipping.pbe`

- row DamageNonTarget: 120 / 180 / 300 -> 90 / 135 / 215
- row DamageTarget: 280 / 420 / 700 -> 230 / 345 / 550
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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3514 s (10.54 ticks) | predicted | |
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

