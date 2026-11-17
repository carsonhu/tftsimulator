# Vayne (4-cost AttackMarksman) · `DA_Vayne19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Rock, Trickshot
- **HP** 850 / 1530 / 2754 · **AD** 62 / 93 / 139.5 · **AS** 0.8 · **Range** 5 · **Armor** 40 · **MR** 40 · **Mana** 0 / 50
- **Unlock**: Field Rock for 3 combats.

### Ability: Darkest Hour

> Passive: On cast or when hit, tumble and gain 0.5 × AP + 1 × GenericCalc2 Durability for 2 seconds. (4 second cooldown)
> 
> Active: Gain demonic power, enhancing the next 3 attacks to deal 175/265/2000 × AD + 2%/3%/20% of the target's max Health as physical damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 62 | 93 | 139.5 |
| TumbleDurability | 0.5 | 0.5 | 0.5 |
| NumAttacks | 3 | 3 | 3 |
| DamageAD | 175 | 265 | 2000 |
| PercentMaxHealthDamage | 0.02 | 0.03 | 0.2 |
| DurabilityDuration | 2 | 2 | 2 |
| TumbleCooldown | 4 | 4 | 4 |
| MaxTumbleHexDistance | 3 | 3 | 3 |

Formulas (as stored; AD and AP are multipliers):

- `GenericCalc1` = 0.5 × AP + 1 × GenericCalc2
- `GenericCalc2` = 1 + 0.5 × AP + -0.5
- `DurabilityCalc1` = 1 + -1 × GenericCalc1
- `PhysicalDamageCalc1` = 175/265/2000 × AD
- `GenericCalc3` = 4 + 1 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Vayne19_Attack`: launch 0.2317 s (6.95 ticks), variants 0.2317, 0.3007, 0.3039; animation length 1.6667 s (50 ticks); release at base AS 0.2317 s (6.95 ticks)
- Attack projectile: DA_Vayne19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Vayne19_Spell` (chrono `CD_Vayne19_CastAnim`): cast ends 0.7 s (21 ticks), next attack can start 0.7333 s (22 ticks), mana lock removed –; **script reads attack speed**; ended by `FinishCasting via OnEventBegin:CD_Vayne19_CastAnim:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Vayne19_Attack` | Chronos | 1.3 | LaunchAttack 0.2317, CustomLaunchAttack1 0.2323, LaunchAttack 0.3007, LaunchAttack 0.3039, CustomLaunchAttack1 0.3677, Unlock 0.52, Unlock 0.56, Unlock 0.6533, Unlock 0.6667, Unlock 1.2 |
| `CD_Vayne19_CastAnim` | Chronos | 0.7003 | DemonON 0.0726, Unlock 0.6968 |
| `CD_Vayne19_TumbleUnlock` | Chronos | 0.5118 | Unlock 0.5062 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Vayne19_TrickshotHandler`, `GA_Trickshot19_HandleAutoAttackBounce`, `GA_AutoAttack`, `GA_LaunchProjectileAttack_Trickshot19`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Vayne19_Spell`, `GA_ShopEvents`, `GA_Vayne19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Vayne19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Vayne19_Passive.txt, GA_Vayne19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: GA_Vayne19_Spell.txt, GA_Vayne19_Tumble.txt
- `GE_ManaLock`: applies mana lock: GA_Vayne19_Spell.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: GA_Vayne19_TrickshotHandler.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2317 s (6.95 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 0.7333 s (22 ticks) | predicted | |
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

