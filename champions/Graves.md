# Graves (4-cost AttackFighter) · `DA_Graves19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6005555.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6005555.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Beach Pop, Renegade
- **HP** 1100 / 1980 / 3564 · **AD** 85 / 127.5 / 191.25 · **AS** 0.6 · **Range** 2 · **Armor** 60 · **MR** 60 · **Mana** 0 / 30

### Ability: Left Hand Free

> For the next 2 attacks, gain 125% Attack Speed, dash to targets, and replace attacks with a cone of 5 bullets that deal 40/60/325 × AD + 5/7/35 × AP physical damage each. On kill, empower an additional attack.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 85 | 127.5 | 191.25 |
| ADDamage | 40 | 60 | 325 |
| NumAttacks | 2 | 2 | 2 |
| APDamage | 5 | 7 | 35 |
| AttackSpeed | 1.25 | 1.25 | 1.25 |
| NumMissiles | 5 | 5 | 5 |
| ExtraAttackPerKill | 1 | 1 | 1 |
| ConeWidth | 500 | 500 | 500 |
| OnHitEffectivenessPerBullet | 0.8 | 0.8 | 0.8 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 40/60/325 × AD + 5/7/35 × AP
- `AttackSpeedCalc1` = 1.25 + 1
- `PhysicalDamageCalc2` = ? × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Graves19_Attack`: launch 0.12 s (3.6 ticks); animation length 1.4667 s (44 ticks); release at base AS 0.1364 s (4.09 ticks)
- Attack projectile: DA_Graves19_AutoAttackProjectile, speed 3000 units/s
- Spell `GA_Graves19_Spell` (chrono `–`): cast ends 0 s (0 ticks), next attack can start 0.0333 s (1 ticks), mana lock removed –; ended by `FinishCasting via activate`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Graves19_Attack` | Chronos | 1.3 | CustomLaunchAttack1 0.12, LaunchAttack 0.12, CustomEventOnAttack1 0.52, Unlock 0.5864 |
| `CD_Graves19_Dash` | Chronos | 3.2951 | Arrive 0.3964 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Graves19_Spell`, `GA_ShopEvents`, `GA_Graves19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Graves19_Spell.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: GA_Graves19_Passive.txt
- `IsAttack`: damage flagged as an attack (or checked for it): GA_Graves19_Passive.txt
- `LaunchAttack`: launches or listens for attacks: GA_Graves19_Passive.txt, GA_Graves19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: GA_Graves19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Graves19_Spell.txt

### Changed since `rls-19.1.0.5995286.Set19.Shipping.pbe`

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.12 s (3.6 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 3000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 0.0333 s (1 ticks) | predicted | |
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

