# Briar (3-cost AttackAssassin) · `DA_Briar19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackAssassin: "Attacks grant 10 Mana. Take 15% less damage from all enemies except the current target." (ManaPerAttack + 10; ManaMax at least 10; MovementSpeed + 200; Threat + -10)
- **Cost** 3, pool 18; traits: Ionic Spark, Slayer
- **HP** 850 / 1530 / 2754 · **AD** 50 / 75 / 112.5 · **AS** 0.8 · **Range** 1 · **Armor** 50 · **MR** 50 · **Mana** 0 / 30

### Ability: Snack Attack

> Heal 100/150/200 × AP and kick a snack at the furthest enemy within 3 hexes. Dash toward it, dealing 100/150/240 × AD physical damage in a 1 hex area.
> 
> Then chow down, gaining 200% Attack Speed for the next 3 attacks and replacing them with slashes that deal 100/150/240 × AD physical damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 50 | 75 | 112.5 |
| DamageAOE_AD | 100 | 150 | 240 |
| HexRangeAOE | 1 | 1 | 1 |
| NumFrenzyAttacks | 3 | 3 | 3 |
| DamageFrenzyAD | 100 | 150 | 240 |
| HealFrenzyAP | 100 | 150 | 200 |
| HexRangeSnack | 3 | 3 | 3 |
| FrenzyAS | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 100/150/240 × AD
- `PhysicalDamageCalc2` = 100/150/240 × AD
- `HealthCalc1` = 100/150/200 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Briar19_Attack`: launch 0.3289 s (9.87 ticks); animation length 2.7667 s (83 ticks); release at base AS 0.3289 s (9.87 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Briar19_Spell` (chrono `CD_Briar19_Windup`): cast ends 1 s (30 ticks), next attack can start 1.0333 s (31 ticks), mana lock removed –; ended by `FinishCasting via OnEventBegin:CD_Briar19_CastAnim_Short:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Briar19_Attack` | CD_Briar19_Attack | 2.6333 | LaunchAttack 0.3289, CustomLaunchAttack1 0.4853, CustomLaunchAttack1 0.5099, Unlock 0.64, Unlock 1.0533, Unlock 1.1067 |
| `CD_Briar19_CastAnim_Long` | CD_Briar19_CastAnim_Long | 0.31 | SlideBack 0.1059, Unlock 0.2923 |
| `CD_Briar19_CastAnim_Short` | CD_Briar19_CastAnim_Short | 0.31 | SlideBack 0.1059, Unlock 0.2923 |
| `CD_Briar19_Windup` | CD_Briar19_Windup | 0.5013 | HealOverWindup 0, Kick 0.191 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Briar19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Briar19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Briar19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Briar19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role | AttackAssassin | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3289 s (9.87 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 1.0333 s (31 ticks) | predicted | |
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

