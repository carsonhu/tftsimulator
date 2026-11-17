# Mel (4-cost MagicCaster) · `DA_Mel19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: R&B, Arcanist
- **HP** 850 / 1530 / 2754 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 0 / 40

### Ability: Chain of Blues

> Fire 30/30/60 missiles split between the 3 closest enemies that each deal 18/28/200 × AP magic damage and apply a stack of Blues. For every 3 stacks of Blues, enemies take 5% more damage from this Ability.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| NumEnemies | 3 | 3 | 3 |
| NumMissiles | 30 | 30 | 60 |
| APDamage | 18 | 28 | 200 |
| PercentDamageOnCurrentTarget | 0.6 | 0.6 | 0.6 |
| RadianceStacksForNegativeDR | 3 | 3 | 3 |
| NegativeDRForRadianceBundle | 0.05 | 0.05 | 0.05 |
| AoeRangeAroundTarget | 10 | 10 | 10 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 18/28/200 × AP
- `GenericCalc1` = 0.05 + 3

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Mel19_Attack_New`: launch 0.365 s (10.95 ticks); animation length 2.6667 s (80 ticks); release at base AS 0.365 s (10.95 ticks)
- Attack projectile: DA_Mel19_AutoAttackProjectile, speed 1600 units/s
- Spell `GA_Mel19_Spell` (chrono `CD_Mel19_CastAnim`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Mel19_Attack_New` | Chronos | 2.1667 | LaunchAttack 0.365, Unlock 0.8664 |
| `CD_Mel19_CastAnim` | Chronos/Spell | 2.1785 | Fire 0.5076 |
| `CD_Mel19_CastAnimOut` | Chronos/Spell | 0.3473 | Unlock 0.3214 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Mel19_Spell`, `GA_ShopEvents`, `GA_Mel19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Mel19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Mel19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.365 s (10.95 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1600 | predicted | |
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

