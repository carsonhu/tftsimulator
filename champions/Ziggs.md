# Ziggs (1-cost MagicMarksman) · `DA_Ziggs19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Hyperpop, Arcanist, Swiftstriker
- **HP** 500 / 900 / 1620 · **AD** 10 / 15 / 22.5 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 0 / 50

### Ability: GlitterBOM3S

> Passive: Attacks deal 40/60/90 × AP bonus magic damage.
> 
> Active: Throw a bomb at the target that deals 180/270/405 × AP magic damage to them and 80/120/180 × AP magic damage to adjacent enemies.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 10 | 15 | 22.5 |
| InitialDamage | 180 | 270 | 405 |
| AADamageAP | 40 | 60 | 90 |
| SecondaryDamageAP | 80 | 120 | 180 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 180/270/405 × AP
- `MagicDamageCalc2` = 80/120/180 × AP
- `MagicDamageCalc3` = 40/60/90 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Ziggs19_Attack`: launch 0.4 s (12 ticks); animation length 1.001 s (30.03 ticks); release at base AS 0.5709 s (17.13 ticks)
- Attack projectile: DA_Ziggs19_AutoAttackProjectile (TFTFixedSpeedWithHeightMovement)
- Spell `GA_Ziggs19_Spell` (chrono `CD_Ziggs19_CastAnim`): cast ends 0.8 s (24 ticks), next attack can start 0.8333 s (25 ticks), mana lock removed 0.8 s (24 ticks); **script reads attack speed**; ended by `FinishCasting via OnEventBegin:CD_Ziggs19_CastAnim:Unlock`
  - notes: rate from unresolved CallFunc_PlayChronoWithTargetActor_Speed_ImplicitCast ×1; projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Ziggs19_Attack` | CD_Ziggs19_Attack | 1.001 | LaunchAttackVariant2 0.4, LaunchAttackVariant1 0.4, Unlock 0.7 |
| `CD_Ziggs19_CastAnim` | CD_Ziggs19_CastAnim | 0.8002 | Unlock 0.779 |
| `CD_Ziggs19_HyperpopHypemeter_Intro` | CD_Ziggs19_HyperpopHypemeter_Intro | 1 | StartHype 0.95 |
| `CD_Ziggs19_HyperpopHypemeter_Outro` | CD_Ziggs19_HyperpopHypemeter_Outro | 1.0312 | EndOutro 0.9791 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_Ziggs19_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Ziggs19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Ziggs19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Ziggs19_LaunchProjectileAttack.txt, GA_Ziggs19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Ziggs19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: GA_Ziggs19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Ziggs19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicMarksman | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.4 s (12 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | not fixed speed | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 0.8333 s (25 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script reads AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.8 s (24 ticks) | predicted | |
| Q10 | Does the mana lock scale with attack speed? | script reads AS | predicted | |
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

