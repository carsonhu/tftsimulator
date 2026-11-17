# Pyke (5-cost AttackFighter) · `DA_Pyke19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive ⟨computed in game: TFTStageMagnitude⟩; MovementSpeed + 200; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Rock, Renegade
- **HP** 1200 / 2160 / 3888 · **AD** 70 / 105 / 157.5 · **AS** 0.9 · **Range** 1 · **Armor** 65 · **MR** 65 · **Mana** 0 / 30
- **Unlock**: Have 85 or more Gold at the end of combat.

### Ability: Execute Gon' Give it to Ya

> Passive: Whenever an enemy drops below 0.08 + 0.02/0.02/0.85 × AP max Health, instantly cast on them, then dash back to the current target.
> 
> Active: Deal 300/470/4000 × AD physical damage to the target and 130/215/800 × AD to all other enemies in an X shape. Execute any enemies below 0.08 + 0.02/0.02/0.85 × AP Health.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 70 | 105 | 157.5 |
| ExecuteAP | 0.02 | 0.02 | 0.85 |
| ExecuteBase | 0.08 | 0.08 | 0.08 |
| ExecutesForBigBoom | 5 | 5 | 1 |
| BigBoomADDamage | 300 | 470 | 4000 |
| DashADDamage | 130 | 215 | 800 |
| ShadowADDamage | 320 | 480 | 1600 |
| PercentDealtToOtherUnits | 0.3 | 0.3 | 0.3 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 300/470/4000 × AD
- `PhysicalDamageCalc2` = 130/215/800 × AD
- `PhysicalDamageCalc3` = 1 × AD
- `GenericCalc1` = 0.08 + 0.02/0.02/0.85 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Pyke19_AttackNew`: launch 0.2646 s (7.94 ticks); animation length 1.6667 s (50 ticks); release at base AS 0.2646 s (7.94 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Pyke19_SpellNew` (chrono `–`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Pyke19_3StarDashAnim` | 3Star | 1.3987 | Spawn 0.3372 |
| `CD_Pyke19_3StarTeleport` | 3Star | 0.2019 | Teleport 0.0189 |
| `CD_Pyke19_AttackNew` | Chronos/Basic | 1.5667 | LaunchAttack 0.2646, Unlock 0.624 |
| `CD_Pyke19_Execute` | Chronos/Passive | 1.0011 | ExecuteEnemy 0.4831, EndExecute 0.5889 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Pyke19_SlamOnEnemy`, `GA_Pyke19_SpellNew`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Pyke19_Passive`, `GA_ShopEvents`, `GA_Play3Star5CostCamera`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Pyke19_SpellNew.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Pyke19_SlamOnEnemy.txt, Abilities/GA_Pyke19_SpellNew.txt
- `GE_UnitStopAttackingMovingCasting`: stops the unit attacking/moving/casting: Abilities/GA_Pyke19_SlamOnEnemy.txt, Abilities/GA_Pyke19_SpellNew.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2646 s (7.94 ticks) | predicted | |
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

