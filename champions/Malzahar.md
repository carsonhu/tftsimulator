# Malzahar (3-cost MagicCaster) · `DA_Malzahar19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 3, pool 18; traits: Composer, Prodigy
- **HP** 800 / 1440 / 2592 · **AD** 35 / 52.5 / 78.75 · **AS** 0.8 · **Range** 4 · **Armor** 35 · **MR** 35 · **Mana** 0 / 50

### Ability: Forbidden Cacophony

> Fire a beam at the target for 2 seconds, dealing 380/570/960 × AP magic damage. The energy rhythmically explodes 4 times, 30% Shredding enemies in a 1 hex area for 4 seconds, and dealing 40/60/110 × AP magic damage each time.
> 
> Shred: Reduce Magic Resist

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 35 | 52.5 | 78.75 |
| SecondaryDamageAP | 40 | 60 | 110 |
| DamageOverSecondsDONTCHANGE | 2 | 2 | 2 |
| ShredPercent | 30 | 30 | 30 |
| ShredDuration | 4 | 4 | 4 |
| UniqueTrait_GLP_NumShops | 10 | 10 | 10 |
| UniqueTrait_GLP_NumInstruments | 2 | 2 | 2 |
| UniqueTrait_DamageDealt_TOOLTIPONLYEDITUNLOCKCONDITION | 60000 | 60000 | 60000 |
| DamageAP | 380 | 570 | 960 |
| PrimaryTickRate | 0.25 | 0.25 | 0.25 |
| AOEHexRange | 1 | 1 | 1 |
| UniqueTrait_APPerInstrument | 0.03 | 0.03 | 0.03 |
| UniqueTrait_MalzaharBonusAPPercent | 1 | 1 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 380/570/960 × AP
- `MagicDamageCalc2` = 40/60/110 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Malzahar19_Attack`: launch 0.445 s (13.35 ticks); animation length 1 s (30 ticks); release at base AS 0.5563 s (16.69 ticks)
- Attack projectile: DA_Malzahar19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Malzahar19_SpellNew` (chrono `CD_Malzahar19_CastAnim_new`): cast ends 2.5 s (75 ticks), next attack can start 2.5333 s (76 ticks), mana lock removed 2.5 s (75 ticks); ended by `FinishCasting via OnEventBegin:CD_Malzahar19_CastAnim_new:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Malzahar19_Attack` | Chronos | 1 | LaunchAttack 0.445, Unlock 0.925 |
| `CD_Malzahar19_CastAnim_new` | Chronos | 2.5007 | BeginBeam 0.3523, Burst 0.9923, Burst 1.6323, Burst 2.2723, Unlock 2.4688 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Malzahar19_SpellNew`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Malzahar19_SpellNew.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Malzahar19_SpellNew.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.445 s (13.35 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 2.5333 s (76 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2.5 s (75 ticks) | predicted | |
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

