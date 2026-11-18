# Janna (5-cost MagicCaster) · `DA_Janna19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Windblessed, Gu Feng, Prodigy
- **HP** 900 / 1620 / 2916 · **AD** 35 / 52.5 / 78.75 · **AS** 0.85 · **Range** 4 · **Armor** 45 · **MR** 45 · **Mana** 0 / 45
- **Unlock**: Earn 20 interest while fielding Xayah.

### Ability: Hymn of the Heaven's Gale

> Fire celestial dragons at up to 3 nearby enemies, each dealing 155/250/9999 × AP magic damage.
> 
> After 4/4/1 casts, the arena is enveloped by the Heaven's Gale, dealing 1800/2700/9000 × AP magic damage to every enemy over 45 seconds.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 35 | 52.5 | 78.75 |
| StormDamageAP | 1800 | 2700 | 9000 |
| NumCastsForStorm | 4 | 4 | 1 |
| StormDuration | 45 | 45 | 45 |
| StormTickRate | 0.5 | 0.5 | 0.5 |
| NumMissiles | 3 | 3 | 3 |
| MissileDamageAP | 155 | 250 | 9999 |
| MissileHexRange | 2 | 2 | 2 |
| UniqueKnockupDuration | 1.25 | 1.75 | 99 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc2` = 155/250/9999 × AP
- `MagicDamageCalc1` = 1800/2700/9000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Janna19_Attack`: launch 0.3297 s (9.89 ticks); animation length 1 s (30 ticks); release at base AS 0.3879 s (11.64 ticks)
- Attack projectile: DA_Janna19_AutoAttackProjectile, speed 1600 units/s
- Spell `GA_Janna19_Spell` (chrono `CD_Janna19_Spell`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_Janna19.NumMissiles input unresolved (self.JannaStarLevel), used star 2 ×1; curve CT_Janna19.NumCastsForStorm input unresolved (self.JannaStarLevel), used star 2 ×1; curve CT_Janna19.MissileHexRange input unresolved (self.JannaStarLevel), used star 2 ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Janna19_3StarKnockup` | Chronos | 8 | SpinOut 5.5 |
| `CD_Janna19_Attack` | Chronos | 1 | LaunchAttack 0.3297, Unlock 0.8 |
| `CD_Janna19_Spell` | Chronos | 1.5109 | LaunchProjectiles 0.3373, Storm 0.4037, Unlock 1.5021 |
| `CD_Janna19_Storm` | Chronos | 2.0041 | 3StarCast 0.1423 |
| `CD_Janna19_UniqueTrait_Tornado` | UniqueTrait | 1.7232 | Unlock 0.7 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Play3Star5CostCamera`, `GA_Janna19_DragonCounter`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Janna19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Janna19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Janna19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3297 s (9.89 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1600 | predicted | |
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

