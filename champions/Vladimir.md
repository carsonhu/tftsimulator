# Vladimir (5-cost MagicFighter) · `DA_Vladimir19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Classical, Arcanist
- **HP** 1150 / 2070 / 3726 · **AD** 40 / 60 / 90 · **AS** 0.75 · **Range** 2 · **Armor** 60 · **MR** 60 · **Mana** 0 / 40
- **Unlock**: Only 1 Champion in the two front rows of the battlefield.

### Ability: The Opera Phantom

> Passive: Gain 30%/30%/100% Omnivamp. Debuffed enemies are Captivated.
> 
> Active: Deal 100/150/999 × AP magic damage to the 3 nearest enemies and Captivate them for 3 seconds. 
> 
> Every 5/5/1th cast, drop a chandelier on the board. It deals 380/600/9999 × AP magic damage to all enemies, reduced by 10% per hex they are away from the epicenter.
> 
> Debuffs: Burn, Wound, Shred, Sunder, Mana Reave, Weaken, Slow, Vunerable

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 40 | 60 | 90 |
| CaptivateDuration | 60 | 60 | 60 |
| APDamage | 100 | 150 | 999 |
| NumCastsForChandelier | 5 | 5 | 1 |
| ShredPercent | 0.2 | 0.2 | 0.2 |
| ChandelierDamage | 380 | 600 | 9999 |
| DamageReductionPerHexFromCenter | 0.1 | 0.1 | 0.1 |
| DamageMinimumPercent | 0.01 | 0.01 | 0.01 |
| NumEnemiesMainCast | 3 | 3 | 3 |
| PassiveOmnivamp | 0.3 | 0.3 | 1 |
| 3StarDamageAmpNerf | 0.2 | 0.2 | 0.2 |
| CaptivateSpellDuration | 3 | 3 | 3 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 100/150/999 × AP
- `MagicDamageCalc2` = 380/600/9999 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Vladimir19_Attack`: launch 0.38 s (11.4 ticks); animation length 1.0012 s (30.04 ticks); release at base AS 0.5061 s (15.18 ticks)
- Attack projectile: DA_Vladimir19_AutoAttackProjectile, speed 1600 units/s
- Spell `GA_Vladimir19_Spell` (chrono `CD_Vladimir19_CastTracker`): cast ends 1.8 s (54 ticks), next attack can start 1.8333 s (55 ticks), mana lock removed 1.8 s (54 ticks); ended by `FinishCasting via OnEventBegin:CD_Vladimir19_CastSpecial:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Vladimir19_3StarCast` | Chronos | 2.5959 | Clap 0.5076, Clap 0.6692, Drop 0.6692, Drop 2 |
| `CD_Vladimir19_Attack` | Chronos | 1.0012 | LaunchAttack 0.38, Unlock 0.7495 |
| `CD_Vladimir19_CastNormal` | Chronos | 0.961 | Cast 0.1425, Unlock 0.9503 |
| `CD_Vladimir19_CastSpecial` | Chronos | 1.8148 | Unlock 1.8 |
| `CD_Vladimir19_Chandelier` | Chronos | 5 | Teleport 0, Damage 1.7963, DestroyActor 4.2469 |

### Scripts on the unit

`GA_LaunchProjectileAttack`, `GA_SetAATarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Play3Star5CostCamera`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_DoLaunchAttackLogic`, `GA_Vladimir19_Spell`, `GA_ShopEvents`, `GA_Vladimir19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Vladimir19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Vladimir19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.38 s (11.4 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1600 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.8333 s (55 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.8 s (54 ticks) | predicted | |
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

