# Jhin (4-cost AttackSpecialist_Ammo) · `DA_Jhin19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5986094.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5986094.Set19.Shipping.pbe`

- **Role** AttackSpecialist_Ammo: "Specialists generate resources in a unique way." ()
- **Cost** 4, pool 10; traits: Classical, Encore
- **HP** 804 / 1447.2 / 2604.96 · **AD** 30 / 45 / 67.5 · **AS** 0.84 · **Range** 5 · **Armor** 44 · **MR** 44 · **Mana** 4 / 4

### Ability: String Quartet

> Passive: Convert 1% bonus Attack Speed into 0.8% Attack Damage.
> 
> Attacks summon violins that attack in unison, dealing 25/38/124 × AD physical damage and Captivating the target for 4 seconds. Every 4th attack is empowered, dealing 80/120/744 × AD + 14/21/104 × AP physical damage and resetting the violins.
> 
> On the 4th sequence onwards, all violins remain out, Jhin gains infinite range, and attacks pierce, dealing 60% reduced damage for each target hit.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| 4thShotDamageAP | 14 | 21 | 104 |
| DamageReductionPerHit | 0.6 | 0.6 | 0.6 |
| BaseAttackSpeed | 0.84 | 0.84 | 1.04 |
| CaptivateDuration | 4 | 4 | 4 |
| ViolinDamageAD | 25 | 38 | 124 |
| MinDamagePercent | 0.4 | 0.4 | 0.4 |
| ASToADRatio | 0.8 | 0.8 | 0.8 |
| 4thShotDamageAD | 80 | 120 | 744 |
| Num4thShotsToAscend | 3 | 3 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 25/38/124 × AD
- `PhysicalDamageCalc2` = 80/120/744 × AD + 14/21/104 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Jhin19_Attack_new`: launch 0.534 s (16.02 ticks); animation length 1.6506 s (49.52 ticks); release at base AS 0.534 s (16.02 ticks)
- Attack projectile: DA_Jhin19_AutoAttackProjectile, speed 2600 units/s
- No spell timeline decoded (no spell ability, or the script never reaches a cast end).

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Jhin19_Attack_new` | Chronos | 1.2519 | CustomEventOnAttack1 0, CustomEventOnAttack4 0, CustomLaunchAttack2 0.2508, CustomLaunchAttack3 0.2508, CustomLaunchAttack1 0.534, LaunchAttack 0.534, EncorePiercing 0.7508, Encore 1.0321, Unlock 1.2338 |
| `CD_Jhin19_CastAnim` | Chronos | 0.8387 | Unlock 0.8358 |
| `CD_Jhin19_ViolinAttack` | Chronos | 0.5004 | Shoot 0, Encore 0.494 |
| `CD_Jhin19_ViolinAttackEncore` | Chronos | 0.402 | Shoot 0, Death 0.3997 |
| `CD_Jhin19_ViolinAttackEncore_Piercing` | Chronos | 0.402 | Shoot 0, Death 0.3997 |
| `CD_Jhin19_ViolinAttack_Piercing` | Chronos | 0.5004 | Shoot 0, Encore 0.494 |
| `CD_Jhin19_ViolinDeath` | Chronos | 0.5008 | Despawn 0.3709 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_ForceSequentialAttack_Jhin`, `GA_ShopEvents`, `GA_Jhin19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- `LaunchAttack`: launches or listens for attacks: GA_ForceSequentialAttack_Jhin.txt, GA_Jhin19_Passive.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: GA_Jhin19_Passive.txt
- `AttackSpeed`: reads or changes attack speed: GA_Jhin19_Passive.txt
- `GE_UnitStopAttackingMovingCasting`: stops the unit attacking/moving/casting: GA_Jhin19_Passive.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackSpecialist_Ammo | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.534 s (16.02 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2600 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | no spell timeline | open | |
| Q8 | Does the cast time scale with attack speed? | no spell timeline | open | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | no spell timeline | open | |
| Q10 | Does the mana lock scale with attack speed? | no spell timeline | open | |
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

