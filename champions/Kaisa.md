# Kai'Sa (3-cost AttackMarksman) · `DA_Kaisa19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 3, pool 18; traits: K/DA, Trickshot
- **HP** 650 / 1170 / 2106 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 5 · **Armor** 35 · **MR** 35 · **Mana** 0 / 30

### Ability: Make it Rain

> Passive: Every 3 attacks, fire 3 missiles that deal ⟨⟩AP physical damage. 
> 
> Active: Gain 0.15 Attack Speed for the rest of combat.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| HexSearchRangeAroundCurrentTarget | 2 | 2 | 2 |
| NumAttacksForMissiles | 3 | 3 | 3 |
| NumMissiles | 3 | 3 | 3 |
| ADDamage | 36 | 54 | 85 |
| APDamage | 6 | 9 | 15 |
| ASOnCast | 0.15 | 0.15 | 0.15 |
| ASDuration | 60 | 60 | 60 |
| MaxSecondaryTargets | 2 | 2 | 2 |
| PercentMissilesOnCurrentTarget | 0.5 | 0.5 | 0.5 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 36/54/85 × AD + 6/9/15 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Kaisa19_Attack`: launch 0.1361 s (4.08 ticks), variants 0.1361, 0.169, 0.3219, 0.3255, 0.3425, 0.3578, 0.4242; animation length 2.8333 s (85 ticks); release at base AS 0.1361 s (4.08 ticks)
- Attack projectile: DA_Kaisa19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Kaisa19_Spell` (chrono `–`): cast ends 0 s (0 ticks), next attack can start 0.0333 s (1 ticks), mana lock removed –; ended by `FinishCasting via activate`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Kaisa19_Attack` | Chronos | 1.3955 | LaunchAttackVariant2 0.1361, LaunchAttackVariant1 0.169, LaunchAttackVariant1 0.3219, LaunchAttackVariant2 0.3255, LaunchAttackVariant2 0.3425, LaunchAttackVariant2 0.3578, LaunchAttackVariant1 0.4242, Unlock 0.56, Unlock 1.04, Unlock 1.1066, Unlock 1.1464 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Kaisa19_Passive`, `GA_Kaisa19_TrickshotHandler`, `GA_Trickshot19_HandleAutoAttackBounce`, `GA_PlayChronoOnTraitActivation`, `GA_AutoAttack`, `GA_LaunchProjectileAttack_Trickshot19`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Kaisa19_Spell`, `GA_ShopEvents`, `GA_ForceSequentialAttack`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Kaisa19_Passive.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Kaisa19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.1361 s (4.08 ticks) | predicted | |
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

