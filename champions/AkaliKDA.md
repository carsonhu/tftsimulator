# Akali (5-cost AttackAssassin) · `DA_AkaliKDA19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackAssassin: "Attacks grant 10 Mana. Take 15% less damage from all enemies except the current target." (ManaPerAttack + 10; ManaMax at least 10; MovementSpeed + 200; Threat + -10)
- **Cost** 5, pool 9; traits: K/DA
- **HP** 1200 / 2160 / 3888 · **AD** 60 / 90 / 135 · **AS** 0.85 · **Range** 1 · **Armor** 60 · **MR** 60 · **Mana** 0 / 45
- **Unlock**: 12 unique star levels of K/DA without True Damage Akali unlocked.

### Ability: Sk8er Gurl

> Skateboard through the longest line of unpainted enemies, dealing 70/105/5000 × AD + 10/15/999 × AP physical damage to enemies hit and spray-painting them and any hexes along the path. Enemies covered in paint or standing in painted hexes are 10% Vulnerable.
> 
> After every 3rd cast, ignite the paint, dealing 3.25 × PhysicalDamageCalc1 physical damage to all enemies who are painted or are standing in a painted hex.
> 
> Vulnerable: Increase Damage Taken

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 60 | 90 | 135 |
| NormalCastSecondaryTargetsPercentDamage | 1 | 1 | 1 |
| ADDamage | 70 | 105 | 5000 |
| APDamage | 10 | 15 | 999 |
| VunerablePercent | 10 | 10 | 10 |
| MegaCastPercentDamage | 3.25 | 3.25 | 3.25 |
| NumCastsForMegaCast | 3 | 3 | 3 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 70/105/5000 × AD + 10/15/999 × AP
- `PhysicalDamageCalc2` = 1 × PhysicalDamageCalc1
- `PhysicalDamageCalc3` = 3.25 × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_AkaliKDA19_Attack`: launch 0.2964 s (8.89 ticks), variants 0.2964, 0.3064, 0.3832; animation length 3 s (90 ticks); release at base AS 0.2964 s (8.89 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_AkaliKDA19_Spell` (chrono `–`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_AkaliKDA19.NumCastsForMegaCast input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast), used star 2 ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_AkaliKDA19_3StarSkateboardExplosion` | Chronos/3Star | 1.8494 | Damage 0.2566 |
| `CD_AkaliKDA19_3StarSkateboard_Moving` | Chronos/3Star | 46.2873 | Arrive 46.2873 |
| `CD_AkaliKDA19_Attack` | Chronos | 3 | LaunchAttack 0.2964, LaunchAttack 0.3064, LaunchAttack 0.3832, Unlock 0.4532, Unlock 1.1864, Unlock 1.2 |
| `CD_AkaliKDA19_PaintedHex` | Chronos | 1.3788 | Default 0, Loop 0.7572 |
| `CD_AkaliKDA19_CastAnim` | Chronos/NormalCast | 0.3666 | StartDash 0.3286 |
| `CD_AkaliKDA19_MoveToCastLocation` | Chronos/NormalCast | 0.3495 | Default 0, Arrive 0.01, StartSkating 0.01, Loop 0.0188 |
| `CD_AkaliKDA19_MoveToFinalHex` | Chronos/NormalCast | 1.1473 | Default 0, Arrive 0.1498, LoopAnim 0.1498 |
| `CD_AkaliKDA19_EmpoweredCastAnimation` | Chronos/SpecialCast | 1.0167 | FireProjectiles 0.3685, Unlock 0.9956 |
| `CD_AkaliKDA19_ExplosionOnHex` | Chronos/SpecialCast | 1.0012 | BlowUpAnotherHex 0.0449 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_PlayChronoOnTraitActivation`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Play3Star5CostCamera`, `GA_ReduceOutgoing3StarDamage`, `GA_GainDamageReductionAt3Star`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_AkaliKDA19_Spell`, `GA_ShopEvents`, `GA_AkaliKDA19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_AkaliKDA19_Spell.txt, Abilities/GA_Akali_DeleteMe.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_AkaliKDA19_Spell.txt, Abilities/GA_Akali_DeleteMe.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackAssassin | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2964 s (8.89 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
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

