# Gnar (1-cost HybridSpecialist_Ammo) · `DA_Gnar19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** HybridSpecialist_Ammo: "Specialists generate resources in a unique way." ()
- **Cost** 1, pool 30; traits: Pentakill, Trickshot
- **HP** 500 / 900 / 1620 · **AD** 40 / 60 / 90 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 0 / 3

### Ability: Hard Rock

> Passive: Every 3rd attack is replaced with a rock that deals 120/180/270 × AD physical damage and grants Gnar 0.09 × AP + 1 Attack Speed.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 40 | 60 | 90 |
| ADDamage | 120 | 180 | 270 |
| AttackSpeedAP | 0.09 | 0.09 | 0.09 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 120/180/270 × AD
- `AttackSpeedCalc1` = 0.09 × AP + 1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Gnar19__Attack`: launch 0.2678 s (8.03 ticks); animation length 1.9667 s (59 ticks); release at base AS 0.2678 s (8.03 ticks)
- Attack projectile: DA_Gnar19_AutoAttackProjectile, speed 1500 units/s
- No spell timeline decoded (no spell ability, or the script never reaches a cast end).

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Gnar19__Attack` | Chronos | 1.2333 | LaunchAttack 0.2678, CustomLaunchAttack1 0.38, Unlock 0.4932, Unlock 0.7864 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Trickshot19_HandleAutoAttackBounce`, `GA_PlayChronoOnTraitActivation`, `GA_AutoAttack`, `GA_LaunchProjectileAttack_Trickshot19`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Gnar19_Passive`, `GA_ShopEvents`, `GA_Gnar19_TrickshotHandler`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- `AppliesOnHit`: something in the script is flagged as applying on-hit effects: GA_Gnar19_Passive.txt
- `IsAttack`: damage flagged as an attack (or checked for it): GA_Gnar19_Passive.txt
- `LaunchAttack`: launches or listens for attacks: GA_Gnar19_Passive.txt
- `AttackSpeed`: reads or changes attack speed: GA_Gnar19_Passive.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: GA_Gnar19_TrickshotHandler.txt

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
| Q2 | Mana per attack and per second follow the role | HybridSpecialist_Ammo | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2678 s (8.03 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1500 | predicted | |
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

