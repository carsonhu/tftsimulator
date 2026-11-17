# Alune (4-cost MagicCaster) · `DA_Alune19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Heartsteel, Manager, Prodigy
- **HP** 800 / 1440 / 2592 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 20 / 65
- **Unlock**: 4 unique Heartsteel or Prodigy Champions.

### Ability: Spotlight

> Call down a spotlight on the target, dealing 315/475/2250 × AP magic damage. All enemies within 2 hexes of them split 340/510/2500 × AP magic damage. If the target dies, split excess damage between the 2 nearest enemies.
> 
> Heartsteel Upgrade: Fire 5 blasts at target that deal 30/45/72 × AP30/45/72 × AP magic damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| Damage | 315 | 475 | 2250 |
| HexRadius | 2 | 2 | 2 |
| MinimumDamage | 0.2 | 0.2 | 0.2 |
| HeartsteelStan_NumMissiles | 5 | 5 | 5 |
| HeartsteelStan_APDamage | 30 | 45 | 72 |
| AOESplitDamage | 340 | 510 | 2500 |
| OverkillNumTargets | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 315/475/2250 × AP
- `MagicDamageCalc2` = 30/45/72 × AP
- `MagicDamageCalc3` = 340/510/2500 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Alune19_Attack`: launch 0.3667 s (11 ticks); animation length 1.6667 s (50 ticks); release at base AS 0.3667 s (11 ticks)
- Attack projectile: DA_Alune19_AutoAttackProjectile, speed 1750 units/s
- Spell `GA_Alune19_Spell` (chrono `CD_Alune19_CastAnim`): cast ends 1.3 s (39 ticks), next attack can start 1.3333 s (40 ticks), mana lock removed 1.3 s (39 ticks); ended by `FinishCasting via OnEventBegin:CD_Alune19_CastAnim:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Alune19_Attack` | Chronos | 1.3004 | LaunchAttack 0.3667, Unlock 0.6667 |
| `CD_Alune19_CastAnim` | Chronos/Spell | 1.3068 | FireHeartsteelMissiles 0.9616, Damage 1.0606, Unlock 1.2952 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Alune19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Alune19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Alune19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3667 s (11 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1750 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.3333 s (40 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.3 s (39 ticks) | predicted | |
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

