# Seraphine (2-cost MagicCaster) · `DA_SeraphineIndie19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Indie
- **HP** 700 / 1260 / 2268 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 50
- **Unlock**: Reroll 4 times before Stage 2 Carousel.

### Ability: Livestream of Note

> Indie: Release a stream of notes at the target while posing for the fans, dealing 600/900/1350 × AP magic damage over 2.5 seconds.
> 
> Rising Star: Release bonus notes at nearby enemies.
> 
> Superstar: Toss high notes at every enemy.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| ShieldAmount | 0 | 0 | 0 |
| DamageAP | 600 | 900 | 1350 |
| HealRadius | 0 | 0 | 0 |
| HealAmount | 0 | 0 | 0 |
| ShieldDuration | 0 | 0 | 0 |
| RewardsForFirstUpgrade | 1 | 1 | 1 |
| PopularityPerFreeReroll | 1 | 1 | 1 |
| PopularityPerPaidReroll | 2 | 2 | 2 |
| RewardsForSecondUpgrade | 4 | 4 | 4 |
| PopularityForReward | 20 | 20 | 20 |
| HighNoteDamageAP | 70 | 105 | 160 |
| ExtraNoteDamageAP | 20 | 30 | 45 |
| RisingStarExtraNotes | 8 | 8 | 8 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 600/900/1350 × AP
- `HealthCalc1` = 0
- `ShieldCalc1` = 0
- `MagicDamageCalc2` = 20/30/45 × AP
- `MagicDamageCalc3` = 70/105/160 × AP
- `GenericCalc1` = 8

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Seraphine19_Attack`: launch 0.2682 s (8.05 ticks); animation length 1.6333 s (49 ticks); release at base AS 0.2682 s (8.05 ticks)
- Attack projectile: DA_Seraphine19_AutoAttackProjectile, speed 1300 units/s
- Spell `GA_Seraphine19_Spell` (chrono `CD_Seraphine19_CastAnim`): cast ends 2.7 s (81 ticks), next attack can start 2.7333 s (82 ticks), mana lock removed 2.7 s (81 ticks); ended by `FinishCasting via OnEventBegin:CD_Seraphine19_CastAnim:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Seraphine19_Attack` | Chrono | 1.6333 | LaunchAttack 0.2682, Unlock 0.6533 |
| `CD_Seraphine19_CastAnim` | Chrono | 0.8986 | ThirdFire 0.2472, HighNote 0.269, SecondFire 0.2757, BeginFire 0.2997, Unlock 0.8808 |
| `CD_Seraphine19_RisingStarCeremony` | Chrono | 5.3313 | Transform 0.5815, Loot 0.6219 |
| `CD_Seraphine19_SuperstarCeremony` | Chrono | 5.0259 | Transform 0.1964, Loot 0.9112 |
| `CD_Seraphine19_CatGrantLoot` | UniqueTraits | 4.186 | BeginSpawn 2.7984, Loot 2.9578 |
| `CD_Seraphine19_GrantLoot` | UniqueTraits | 3.4034 | BeginSpawn 0.8866, Loot 0.9886 |
| `CD_Seraphine19_SpawnOnBench` | UniqueTraits | 2.0011 | AllowStarUp 1.2366 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Seraphine19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Seraphine19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Seraphine19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2682 s (8.05 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1300 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 2.7333 s (82 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2.7 s (81 ticks) | predicted | |
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

