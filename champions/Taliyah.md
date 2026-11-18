# Taliyah (5-cost MagicCaster) · `DA_Taliyah19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Beach Pop, Encore
- **HP** 950 / 1710 / 3078 · **AD** 30 / 45 / 67.5 · **AS** 0.8 · **Range** 4 · **Armor** 50 · **MR** 50 · **Mana** 0 / 40
- **Unlock**: A Champion of each cost starts in a Beach Pop hex.

### Ability: Crowd Surfing

> Throw 3 rocks at the target, each dealing 185/280/2000 × AP magic damage.
> 
> Every 3/3/1rd cast, quickly reposition and surf in a line instead. Enemies hit take 160/240/2000 × AP + 0.02/0.03/0.5 × AP max Health magic damage and are briefly knocked up.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| KnockupDuration | 0.5 | 0.5 | 10 |
| SpellDamageAP | 160 | 240 | 2000 |
| PercentMaxHPDamageAP | 0.02 | 0.03 | 0.5 |
| ChanceChest | 0 | 0 | 1 |
| MaxGoldChest | 3 | 3 | 3 |
| MinGoldChest | 2 | 2 | 2 |
| ChanceComponent | 0 | 0 | 1 |
| PercentTreasurePerHit | 0 | 0 | 1.5 |
| PercentJunkPerHit | 0 | 0 | 0 |
| ChanceCoin | 0 | 0 | 0.75 |
| SmallSpellDamageAP | 185 | 280 | 2000 |
| SmallSpellNumRocks | 3 | 3 | 3 |
| WaveEveryNthCast | 3 | 3 | 1 |
| ComponentCooldown | 5 | 5 | 0 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 160/240/2000 × AP
- `GenericCalc1` = 0.02/0.03/0.5 × AP
- `MagicDamageCalc2` = 185/280/2000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Taliyah19_Attack`: launch 0.2284 s (6.85 ticks); animation length 1.6667 s (50 ticks); release at base AS 0.2284 s (6.85 ticks)
- Attack projectile: DA_Taliyah19_AutoAttackProjectile, speed 1500 units/s
- Spell `GA_Taliyah19_Spell` (chrono `CD_Taliyah19_Windup`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_Encore19.RecastEffectiveness input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_9), used star 2 ×1; projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Taliyah19_3StarCelebrate` | Chronos | 9.9643 | Default 0, SurfLoop 0.5817, Arrived 3.0309, DanceLoop 4.1309 |
| `CD_Taliyah19_3StarCeremony` | Chronos | 3 | Default 0, Land 2 |
| `CD_Taliyah19_Attack` | Chronos | 1.6667 | LaunchAttackVariant1 0.2284, LaunchAttackVariant2 0.2284, Unlock 0.6667 |
| `CD_Taliyah19_BringWave` | Chronos | 3.9961 | Arrived 3.9961 |
| `CD_Taliyah19_BringWave3Star` | Chronos | 3.9961 | Arrived 3.9961 |
| `CD_Taliyah19_HopOff` | Chronos | 0.6007 | ArriveSafe 0.2358, Unlock 0.5807 |
| `CD_Taliyah19_SmallCast` | Chronos | 1.9324 | Unlock 1.9113 |
| `CD_Taliyah19_Windup` | Chronos | 1.3499 | Default 0, Untargetable 1.3191, BeginSurf 1.3488 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Play3Star5CostCamera`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Taliyah19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Taliyah19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Taliyah19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2284 s (6.85 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1500 | predicted | |
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

