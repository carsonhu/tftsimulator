# Ashe (2-cost AttackMarksman) · `DA_Ashe19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Beach Pop, Swiftstriker
- **HP** 550 / 990 / 1782 · **AD** 50 / 75 / 112.5 · **AS** 0.75 · **Range** 5 · **Armor** 30 · **MR** 30 · **Mana** 20 / 60
- **Unlock**: A Beach Pop Champion with 2 items.

### Ability: Feelin' Shot Shot Shot

> The next 6 attacks have 0.3 + 0.2 × AP Attack Speed and are replaced with flurries of 3 arrows. Each arrow deals 33/50/75 × AD physical damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 50 | 75 | 112.5 |
| SpellASBase | 0.3 | 0.3 | 0.3 |
| NumFlurryAttacks | 6 | 6 | 6 |
| ArrowsPerFlurry | 3 | 3 | 3 |
| ArrowDamageAD | 33 | 50 | 75 |
| SpellASAP | 0.2 | 0.2 | 0.2 |
| OnHitEffectivenessPerFlurryArrow | 0.6 | 0.6 | 0.6 |

Formulas (as stored; AD and AP are multipliers):

- `AttackSpeedCalc1` = 0.3 + 0.2 × AP
- `PhysicalDamageCalc1` = 33/50/75 × AD

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Ashe19_Attack_new`: launch 0.2971 s (8.91 ticks); animation length 2.1333 s (64 ticks); release at base AS 0.2971 s (8.91 ticks)
- Attack projectile: DA_Ashe19_AutoAttackProjectile, speed 2500 units/s
- Spell `GA_Ashe19_Spell` (chrono `CD_Ashe19_CastAnim`): cast ends 0.3333 s (10 ticks), next attack can start 0.3667 s (11 ticks), mana lock removed –; **script reads attack speed**; ended by `FinishCasting via OnChronoStopped:CD_Ashe19_CastAnim:None`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Ashe19_Attack_new` | Chronos | 2.1333 | CustomLaunchAttack1 0, LaunchAttack 0.2971, Unlock 0.4, Unlock 0.5 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Ashe19_Spell`, `GA_ShopEvents`, `GA_Ashe19_EmpoweredAttack`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Ashe19_Spell.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: Abilities/GA_Ashe19_EmpoweredAttack.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Ashe19_EmpoweredAttack.txt, Abilities/GA_Ashe19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Ashe19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Ashe19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2971 s (8.91 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2500 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 0.3667 s (11 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script reads AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | predicted | |
| Q10 | Does the mana lock scale with attack speed? | script reads AS | predicted | |
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

