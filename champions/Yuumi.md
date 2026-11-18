# Yuumi (4-cost MagicCaster) · `DA_Yuumi19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Illbeats, Encore
- **HP** 850 / 1530 / 2754 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 0 / 20

### Ability: Girl, Put Your Records On (Your Head)

> Throw a spinning disc that deals 175/265/1400 × AP magic damage and stacks on the target's head, reducing their Magic Resist by 1 every second. 
> 
> When they have 4 + 1 discs, the stack topples over, dealing 40% of the stacked discs' total damage to the target and another 40% split among 4 nearby enemies.
> 
> If an enemy dies with a disc, it passes to another enemy.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| PopDamageAP | 0 | 0 | 0 |
| TickRate | 0.25 | 0.25 | 0.25 |
| DoTDuration | 999 | 999 | 999 |
| NumDiscsToPop | 4 | 4 | 4 |
| DoTDamageAP | 175 | 265 | 1400 |
| PoppedDotPercentToMainTarget | 0.4 | 0.4 | 0.4 |
| PoppedDotPercentToOtherTargets | 0.4 | 0.4 | 0.4 |
| NumTargetsToDistributeDiscs | 4 | 4 | 4 |
| MRShredPerSecond | 1 | 1 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 175/265/1400 × AP
- `MagicDamageCalc2` = 0 × AP
- `GenericCalc1` = 4 + 1
- `GenericCalc2` = 1 + 0.25
- `GenericCalc3` = 1 + 1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Yuumi19_Attack`: launch 0.3671 s (11.01 ticks); animation length 2.6667 s (80 ticks); release at base AS 0.3671 s (11.01 ticks)
- Attack projectile: DA_Yuumi19_AutoAttackProjectile, speed 1500 units/s
- Spell `GA_Yuumi19_Spell` (chrono `self.SpellChrono`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_Encore19.RecastEffectiveness input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_3), used star 2 ×1; chrono not found self.SpellChrono ×1; projectile (hit time depends on travel) ×6

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Yuumi19_Attack` | CD_Yuumi19_Attack | 2.6667 | LaunchAttack 0.3671, Unlock 1.0667 |
| `CD_Yuumi19_CastAnimLeft` | CD_Yuumi19_CastAnimLeft | 1.0145 | Disk 0.365, EncoreDisk 0.4615, Unlock 0.9997 |
| `CD_Yuumi19_CastAnimRight` | CD_Yuumi19_CastAnimRight | 1.0158 | Disk 0.365, EncoreDisk 0.4615, Unlock 0.9997 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Yuumi19_Spell`, `GA_ShopEvents`, `GA_Yuumi19_GESpecReceiver`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Yuumi19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Yuumi19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3671 s (11.01 ticks) | predicted | |
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

