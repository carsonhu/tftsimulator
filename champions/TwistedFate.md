# Twisted Fate (5-cost MagicMarksman) · `DA_TwistedFate19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Tango, Trickshot
- **HP** 900 / 1620 / 2916 · **AD** 30 / 45 / 67.5 · **AS** 0.8 · **Range** 4 · **Armor** 45 · **MR** 45 · **Mana** 0 / 50

### Ability: Wildcard Cortado

> Passive: At Combat Start, draw a card for each champion in the shop. If your shop has refreshed this round, gain loot based on the cards drawn!
> 
> 1 or 2 of a Kind: 1/1/100 Gold
> 3 of a Kind: Random champion
> 4 of a Kind: Item Component
> 5 of a Kind: Mystery Box!
> 
> Active: The next 5 attacks gain 100% Attack Speed and are replaced with cards that deal 100/150/2000 × AP magic damage to the target and 30/45/1000 × AP magic damage to 2 nearby enemies.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| 1MatchGold | 1 | 1 | 100 |
| 2MatchGold | 1 | 1 | 100 |
| APDamage | 30 | 45 | 1000 |
| AttackSpeed | 1 | 1 | 1 |
| AutoAttackDamage | 30 | 45 | 67.5 |
| BurnPercent | 1 | 1 | 1 |
| Duration | 3 | 3 | 3 |
| LootChance | 0.1 | 0.2 | 1 |
| ManaGrant | 8 | 8 | 8 |
| PercentDamagePerCost | 0.18 | 0.18 | 0.18 |
| PrimaryTargetDamage | 100 | 150 | 2000 |
| SecondaryOnHitEffectiveness | 0.3 | 0.3 | 0.3 |
| TraitAttackSpeed | 0.15 | 0.15 | 0.15 |
| UniqueTrait_MaxHealthDamage | 0.2 | 0.2 | 0.2 |
| WoundPercent | 33 | 33 | 33 |
| 3Star5CostDamage | 100 | 150 | 2000 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 30/45/1000 × AP
- `GenericCalc1` = 1 × AP + 1 × Stack
- `AttackSpeedCalc1` = 1
- `MagicDamageCalc2` = 100/150/2000 × AP
- `MagicDamageCalc3` = 100/150/2000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_TwistedFate19_Attack`: launch 0.2884 s (8.65 ticks); animation length 1.7 s (51 ticks); release at base AS 0.2884 s (8.65 ticks)
- Attack projectile: DA_TwistedFate19_AutoAttackProjectile, speed 1500 units/s
- Spell `GA_TwistedFate19_3Star5Cost_Spell` (chrono `CD_TwistedFate19_3Star5Cost_Spell`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
- Spell `GA_TwistedFate19_Spell` (chrono `–`): cast ends 0 s (0 ticks), next attack can start 0.0333 s (1 ticks), mana lock removed –; ended by `FinishCasting via activate`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_TwistedFate19_Attack` | Chronos | 1.0003 | LaunchAttackVariant1 0.2884, LaunchAttackVariant2 0.2884, CustomLaunchAttack1 0.33, Unlock 0.68, CustomLaunchAttack1 0.8108, CustomLaunchAttack1 0.9265 |
| `CD_TwistedFate19_CombatStart` | Chronos | 0.9999 | DrawCard1 0.4971, DrawCard2 0.6013, DrawCard3 0.7, DrawCard4 0.7967, DrawCard5 0.8985 |
| `CD_TwistedFate19_Redraw` | Chronos | 0.3202 | DrawCard1 0, DrawCard2 0.0697, DrawCard3 0.1367, DrawCard4 0.2045, DrawCard5 0.2731 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Play3Star5CostCamera`, `GA_Trickshot19_HandleAutoAttackBounce`, `GA_PlayAdditionalChronoOnStarUp`, `GA_TwistedFate19_3Star5Cost_Spell`, `GA_AutoAttack`, `GA_LaunchProjectileAttack_Trickshot19`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_TwistedFate19_Spell`, `GA_ShopEvents`, `GA_TwistedFate19_SpellTrickshot`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_TwistedFate19_3Star5Cost_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_TwistedFate19_3Star5Cost_Spell.txt, GA_TwistedFate19_Spell.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: GA_TwistedFate19_Spell.txt, GA_TwistedFate19_SpellTrickshot.txt
- `LaunchAttack`: launches or listens for attacks: GA_TwistedFate19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicMarksman | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2884 s (8.65 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1500 | predicted | |
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

