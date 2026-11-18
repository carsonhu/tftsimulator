# Yone (4-cost AttackFighter) · `DA_Yone19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Heartsteel, Slayer
- **HP** 1150 / 2070 / 3726 · **AD** 55 / 82 / 123 · **AS** 0.85 · **Range** 1 · **Armor** 70 · **MR** 70 · **Mana** 0 / 50

### Ability: Two Sides

> Passive: This ability scales Attack Damage or Ability Power, whichever is higher. Attacks deal 55/82/123 × AD physical damage.
> 
> Active: Rapidly strike the target and up to 2 nearby enemies 10/10/30 times, each dealing 35/55/400 × AD physical damage. After the assault, unleash a massive slash that deals 175/265/1500 × AD physical damage to target.
> 
> Heartsteel Upgrade: Casts strike 2 more times and ignore 25%25% of Armor.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 55 | 82 | 123 |
| NumSpirits | 10 | 10 | 30 |
| PrimaryDamage | 35 | 55 | 400 |
| TanksBonusDamage | 0 | 0 | 0 |
| NumBonusEnemies | 2 | 2 | 2 |
| AOERangeAroundCurrentTarget | 2 | 2 | 4 |
| PercentStrikesOnTarget | 0.5 | 0.5 | 0.5 |
| SecondaryDamage | 175 | 265 | 1500 |
| HeartsteelStan_ExtraClones | 2 | 2 | 2 |
| HeartsteelStan_ArmorIgnore | 0.25 | 0.25 | 0.25 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 35/55/400 × AD
- `PhysicalDamageCalc2` = 175/265/1500 × AD
- `PhysicalDamageCalc3` = 55/82/123 × AD
- `MagicDamageCalc1` = 35/55/400 × AP
- `MagicDamageCalc2` = 175/265/1500 × AP
- `MagicDamageCalc3` = 55/82/123 × AP
- `GenericCalc1` = 1 + -0.25

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Yone19_AttackNew`: launch 0.26 s (7.8 ticks), variants 0.26, 0.323, 0.353, 0.3542; animation length 2.5 s (75 ticks); release at base AS 0.26 s (7.8 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Yone19_Spell` (chrono `switch(Temp_bool_Variable_1){false: Temp_object_Variable_4; true: Temp_object_Variable_3; default: K2Node_Select_Default_1}`): cast ends –, next attack can start –, mana lock removed –; **script reads attack speed**; **no cast end found**
  - notes: chrono not found switch(Temp_bool_Variable_1){false: Temp_object_Variable_4; true: Temp_object_Variable_3; default: K2Node_Select_Default_1} ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Yone19_AttackNew` | Chrono | 2.5 | LaunchAttack 0.26, LaunchAttack 0.323, LaunchAttack 0.353, LaunchAttack 0.3542, Unlock 0.9864, Unlock 1 |
| `CD_Yone19_CastAnim` | Chrono | 9.9446 | Default 0, Loop 0.2966, StartStrikes 0.4992 |
| `CD_Yone19_CastAnim_Part2` | Chrono | 0.7915 | DealDamage 0.3453, Unlock 0.6589 |
| `CD_Yone19_Celebration` | Chrono | 12.2141 | Default 0, Loop 3.0894 |
| `CD_Yone19_SpellMissile` | Chrono | 0.3999 | Damage 0.0576, Damage 0.0793, Damage 0.0831, Damage 0.1619 |
| `CD_Yone19_CastAnimAlt` | Chrono/old | 9.9957 | Default 0, Loop 0.3478, StartStrikes 0.5504 |
| `CD_Yone19_CastAnim_Part2_Alt` | Chrono/old | 1.0058 | DealDamage 0.7784, Unlock 0.9879 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Yone19_Passive`, `GA_ForceSequentialAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_Yone19_LaunchMeleeAttack`, `GA_Yone19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Yone19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Yone19_LaunchMeleeAttack.txt, GA_Yone19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Yone19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: GA_Yone19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Yone19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.26 s (7.8 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | – | open | |
| Q8 | Does the cast time scale with attack speed? | script reads AS | open | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | open | |
| Q10 | Does the mana lock scale with attack speed? | script reads AS | open | |
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

