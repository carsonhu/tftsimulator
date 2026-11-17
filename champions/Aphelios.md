# Aphelios (5-cost AttackMarksman) · `DA_Aphelios19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Heartsteel
- **HP** 900 / 1620 / 2916 · **AD** 60 / 90 / 135 · **AS** 0.8 · **Range** 5 · **Armor** 45 · **MR** 45 · **Mana** 40 / 180
- **Unlock**: 2-star Alune or Yone.

### Ability: BANG BANG BANGERS

> Passive: Gain a Chakram every 4 attacks, up to 15. Attacks deal 7/10/200 × AD bonus physical damage for every Chakram equipped. After collecting 15, gain 30%/30%/500% Attack Damage and infinite range.
> 
> Active: Fire bolts at the 3 nearest enemies that deal 280/420/3000 × AD + 60/90/300 × AP physical damage, then split into 16 bolts that deal 0.15/0.15/1 × PhysicalDamageCalc1 physical damage to enemies they pass through. Gain 0.75 Attack Speed for 4 seconds.
> 
> Heartsteel Upgrade: Start combat with 5 Chakrams equipped.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 60 | 90 | 135 |
| APDamage | 60 | 90 | 300 |
| NumEnemies | 3 | 3 | 3 |
| PostCaseAS | 0.75 | 0.75 | 0.75 |
| PercentSecondaryDamage | 0.15 | 0.15 | 1 |
| ADDamage | 280 | 420 | 3000 |
| HeartsteelStan_ExcessChakramArmorReduction | 10 | 10 | 10 |
| HeartsteelStan_MaxChakrams | 15 | 15 | 15 |
| HeartsteelStan_ADDamage | 7 | 10 | 200 |
| HeartsteelStan_NumAttacksForChakram | 4 | 4 | 4 |
| NumBoltsToSplitTo | 16 | 16 | 16 |
| PostCaseASPerEnemyHit | 0 | 0 | 0 |
| PostCaseASDuration | 4 | 4 | 4 |
| HeartsteelStan_CombatStartChakrams | 5 | 5 | 5 |
| MaxChakramsExtraRange | 6 | 6 | 6 |
| MaxChakramsExtraAD | 0.3 | 0.3 | 5 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 280/420/3000 × AD + 60/90/300 × AP
- `PhysicalDamageCalc2` = 0.15/0.15/1 × PhysicalDamageCalc1
- `PhysicalDamageCalc3` = 7/10/200 × AD
- `AttackSpeedCalc1` = 1 + 0.75
- `GenericCalc1` = 1 + 0

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Aphelios19_AttackNew`: launch 0.3 s (9 ticks), variants 0.3, 0.3342; animation length 2.3 s (69 ticks); release at base AS 0.3 s (9 ticks)
- Attack projectile: DA_Aphelios19_AutoAttackProjectileCalibrum, speed 3000 units/s
- Spell `GA_Aphelios19_Ability` (chrono `CD_Aphelios19_CastSustained`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_Aphelios19.NumEnemies input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_1), used star 2 ×1; curve CT_Aphelios19.NumBoltsToSplitTo input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast), used star 2 ×1; projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Aphelios19_AttackNew` | Chronos/Basic | 2.3 | LaunchAttack 0.3, LaunchAttack 0.3342, Unlock 0.6, Unlock 0.65 |
| `CD_Aphelios19_CastSustained` | Chronos/Basic | 3.1974 | LaunchAttack 2.1 |
| `CD_Aphelios19_CastAnim` | Chronos/Cast | 2.2009 | StartLasers 0.1453, FireBlasts 0.9834, Unlock 2.1371 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Aphelios19_CombatPassive`, `GA_PlayChronoOnTraitActivation`, `GA_Celebration`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Death`, `GA_Aphelios19_Ability`, `GA_ShopEvents`, `GA_Aphelios19_StartGunManager`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Aphelios19_Ability.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Aphelios19_Ability.txt, Abilities/GA_Aphelios19_CombatPassive.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Aphelios19_Ability.txt, Abilities/GA_Aphelios19_CombatPassive.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Aphelios19_Ability.txt
- `AppliesOnHit`: something in the script is flagged as applying on-hit effects: Abilities/GA_Aphelios19_CombatPassive.txt
- `IsAttack`: damage flagged as an attack (or checked for it): Abilities/GA_Aphelios19_CombatPassive.txt

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
| Q2 | Mana per attack and per second follow the role | AttackMarksman | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3 s (9 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 3000 | predicted | |
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

