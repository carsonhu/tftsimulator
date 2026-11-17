# Bard (3-cost MagicMarksman) · `DA_Bard19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 3, pool 18; traits: Jazz, Swiftstriker
- **HP** 650 / 1170 / 2106 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 35 · **MR** 35 · **Mana** 20 / 80

### Ability: Come Chime with Me

> Passive: Gain the Horn of the Traveler. While equipped, casts generate XP and attacks grant bonus Mana.
> 
> Active: Summon a wave of meeps that deal 210/315/505 × AP magic damage to enemies hit, reduced by 0.3 for each one it passes through.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| Meeps Damage | 210 | 315 | 505 |
| ManaPerAttack | 2 | 7 | 20 |
| MaxMeeps | 9999 | 9999 | 9999 |
| FalloffPerUnit | 0.3 | 0.3 | 0.3 |
| MeepXP | 1 | 1 | 1 |
| MinimumDamagePercent | 0.2 | 0.2 | 0.2 |

Formulas (as stored; AD and AP are multipliers):

- `ManaCalc1` = 2/7/20 × AP
- `MagicDamageCalc1` = 210/315/505 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Bard19_Attack`: launch 0.2 s (6 ticks), variants 0.2, 0.35; animation length 2.0351 s (61.05 ticks); release at base AS 0.2 s (6 ticks)
- Attack projectile: DA_Bard19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Bard19_Spell` (chrono `CD_Bard19_CastAnim`): cast ends 1.0667 s (32 ticks), next attack can start 1.1 s (33 ticks), mana lock removed 1.0667 s (32 ticks); ended by `FinishCasting via OnEventBegin:CD_Bard19_CastAnim:Unlock`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Bard19_Attack` | Chronos | 2.0351 | LaunchAttack 0.2, LaunchAttack 0.35, Unlock 0.7708, Unlock 0.8141 |
| `CD_Bard19_CastAnim` | Chronos | 1.0963 | Unlock 1.0552 |
| `CD_Bard19_CastAnimMeeps` | Chronos | 0.8497 | FireMeeps 0.4381, Unlock 0.8402 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Bard19_Spell`, `GA_ShopEvents`, `GA_Bard19_PopHornOff`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Bard19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Bard19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role | MagicMarksman | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2 s (6 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.1 s (33 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.0667 s (32 ticks) | predicted | |
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

