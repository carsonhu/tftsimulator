# Renata Glasc (2-cost MagicCaster) · `DA_RenataGlasc19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Classical, Choreographer
- **HP** 550 / 990 / 1782 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 45

### Ability: Hostile Measures

> Fire a musical bar at the target, applying 2 stacks of Toxin. Toxin stacks deal 160/240/580 × AP magic damage over 15 seconds. Additionally, apply 1 stack of Toxin to 2 nearby enemies, prioritizing unpoisoned enemies. 
> 
> Enemies are Captivated for 3 seconds upon Toxin application, increased to 6 seconds if their star level is less than or equal to Renata's.
> 
> Captivated enemies grant bonuses to Classical champions.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| SecondaryTargetSpellDamage | 0 | 0 | 0 |
| PrimaryTargetSpellDamage | 0 | 0 | 0 |
| StunDuration | 0 | 0 | 0 |
| NumSecondaryTargets | 2 | 2 | 2 |
| PrimaryTargetStacks | 2 | 2 | 2 |
| SecondaryTargetStacks | 1 | 1 | 1 |
| ToxinDamageAP | 160 | 240 | 580 |
| TickRate | 0.25 | 0.25 | 0.25 |
| ToxinDuration | 15 | 15 | 15 |
| CaptivateDurationShort | 3 | 3 | 3 |
| CaptivateDurationLong | 6 | 6 | 6 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 0 × AP
- `MagicDamageCalc2` = 0 × AP
- `MagicDamageCalc3` = 160/240/580 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_RenataGlasc19_Attack`: launch 0.3307 s (9.92 ticks); animation length 2.3333 s (70 ticks); release at base AS 0.3307 s (9.92 ticks)
- Attack projectile: DA_RenataGlasc19_AutoAttackProjectile, speed 1800 units/s
- Spell `GA_RenataGlasc19_Spell` (chrono `CD_RenataGlasc19_Spell`): cast ends 3.6667 s (110 ticks), next attack can start 3.7 s (111 ticks), mana lock removed 3.6667 s (110 ticks); ended by `FinishCasting via OnEventBegin:CD_RenataGlasc19_SpellEnd:Unlock`
  - notes: curve CT_RenataGlasc19.NumSecondaryTargets input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.ToxinDuration input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.StunDuration input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.PrimaryTargetStacks input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.SecondaryTargetStacks input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.CaptivateDurationShort input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.CaptivateDurationLong input unresolved (self.RenataStarLevel), used star 2 ×1; projectile (hit time depends on travel) ×6

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_RenataGlasc19_Attack` | CD_RenataGlasc19_Attack | 2.3333 | LaunchAttack 0.3307, Unlock 0.9333 |
| `CD_RenataGlasc19_Spell` | CD_RenataGlasc19_Spell | 0.9328 | LaunchChains 0.1974 |
| `CD_RenataGlasc19_SpellEnd` | CD_RenataGlasc19_SpellEnd | 0.6804 | Unlock 0.6578 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_RenataGlasc19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_RenataGlasc19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_RenataGlasc19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3307 s (9.92 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1800 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 3.7 s (111 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 3.6667 s (110 ticks) | predicted | |
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

