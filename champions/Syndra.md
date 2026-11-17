# Syndra (3-cost MagicCaster) · `DA_Syndra19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 3, pool 18; traits: Beach Pop, Choreographer
- **HP** 650 / 1170 / 2106 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 35 · **MR** 35 · **Mana** 0 / 30

### Ability: Serve's Up

> Spike a volleyball at target, dealing 300/450/720 × AP magic damage. It bounces to an enemy behind them with the least items, dealing 110/165/265 × AP magic damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| SecondaryDamageAP | 110 | 165 | 265 |
| ShredPercent | 20 | 20 | 20 |
| PrimaryDamageAP | 300 | 450 | 720 |
| ShredDuration | 0 | 0 | 0 |
| StartingBounceAngle | 120 | 120 | 120 |
| SearchAngleIncreasePerCheck | 30 | 30 | 30 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 300/450/720 × AP
- `MagicDamageCalc2` = 110/165/265 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Syndra19_Attack`: launch 0.1377 s (4.13 ticks), variants 0.1377, 0.27; animation length 2.4667 s (74 ticks); release at base AS 0.1377 s (4.13 ticks)
- Attack projectile: DA_Syndra19_AutoAttackProjectile, speed 1800 units/s
- Spell `GA_Syndra19_Spell` (chrono `CD_Syndra19_CastAnim`): cast ends 2 s (60 ticks), next attack can start 2.0333 s (61 ticks), mana lock removed 2 s (60 ticks); ended by `FinishCasting via OnEventBegin:CD_Syndra19_CastAnim:Unlock`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Syndra19_Attack` | CD_Syndra19_Attack | 2.4667 | LaunchAttackVariant1 0.1377, LaunchAttackVariant2 0.27, Unlock 0.8667, Unlock 0.9867 |
| `CD_Syndra19_CastAnim` | CD_Syndra19_CastAnim | 0.7749 | LaunchProjectile 0.4061, Unlock 0.7364 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Syndra19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Syndra19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Syndra19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role | MagicCaster | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.1377 s (4.13 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1800 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 2.0333 s (61 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2 s (60 ticks) | predicted | |
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

