# Yunara (1-cost AttackMarksman) · `DA_Yunara19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Ionic Spark, Swiftstriker
- **HP** 500 / 900 / 1620 · **AD** 50 / 75 / 112.5 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 50 / 80

### Ability: Cultivation of Teen Spirit

> For the rest of combat, attacks fire an additional orb that deals 13/20/30 × AD + 3/5/7 × AP physical damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 50 | 75 | 112.5 |
| APDamage | 3 | 5 | 7 |
| NumOrbsToAdd | 1 | 1 | 1 |
| ADDamage | 13 | 20 | 30 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 13/20/30 × AD + 3/5/7 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Yunara19_AttackNew`: launch 0.2667 s (8 ticks); animation length 2.5666 s (77 ticks); release at base AS 0.2667 s (8 ticks)
- Attack projectile: DA_Yunara19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Yunara19_Spell` (chrono `CD_Yunara19_Empower`): cast ends 0 s (0 ticks), next attack can start 0.0333 s (1 ticks), mana lock removed –; ended by `FinishCasting via activate`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Yunara19_AttackNew` | Chronos | 2.5666 | LaunchAttackVariant1 0.2667, Unlock 1.12 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_ForceSequentialAttack`, `GA_PlayChronoOnTraitActivation`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Yunara19_Spell`, `GA_ShopEvents`, `GA_Yunara19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Yunara19_Passive.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Yunara19_Passive.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackMarksman | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2667 s (8 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
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

