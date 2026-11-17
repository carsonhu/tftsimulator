# Neeko (1-cost MagicCaster) · `DA_Neeko19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 1, pool 30; traits: K/DA, Encore, Prodigy
- **HP** 500 / 900 / 1620 · **AD** 30 / 45 / 67.5 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 0 / 40

### Ability: K/DA Fan Club

> Convene the K/DA fan club, throwing 3 confetti streams at target that each deal 75/115/175 × AP magic damage. If they kill, permanently gain 1% Ability Power.
> 
> Current Bonus: ⟨live⟩ Ability Power

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| APGain | 0.01 | 0.01 | 0.01 |
| DamageAP | 75 | 115 | 175 |
| NumProjectiles | 3 | 3 | 3 |
| KillBuffer | 0.2 | 0.2 | 0.2 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 75/115/175 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Neeko19_Attack`: launch 0.4219 s (12.66 ticks), variants 0.4219, 0.4443; animation length 3.1 s (93 ticks); release at base AS 0.4219 s (12.66 ticks)
- Attack projectile: DA_Neeko19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Neeko19_SpellUsingVFX` (chrono `CD_Neeko19_CastAnimWithClone`): cast ends 0.8 s (24 ticks), next attack can start 0.8333 s (25 ticks), mana lock removed 0.8 s (24 ticks); ended by `FinishCasting via OnEventBegin:CD_Neeko19_CastAnimWithClone:Unlock`
  - notes: curve CT_Encore19.RecastEffectiveness input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast), used star 2 ×1; projectile (hit time depends on travel) ×18

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Neeko19_Attack` | Chronos | 3.1 | LaunchAttack 0.4219, LaunchAttack 0.4443, Unlock 1.24 |
| `CD_Neeko19_CastAnimWithClone` | Chronos | 1.3712 | Throw1 0.2331, Throw2 0.3467, Throw3 0.46, Throw4 0.5733, Throw5 0.6867, Throw6 0.8, Unlock 0.8 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayChronoOnTraitActivation`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_Neeko19_SpellUsingVFX`, `GA_ShopEvents`, `GA_Neeko19_PassiveKillTracker`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Neeko19_SpellUsingVFX.txt
- `GE_ManaLock`: applies mana lock: GA_Neeko19_SpellUsingVFX.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.4219 s (12.66 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 0.8333 s (25 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.8 s (24 ticks) | predicted | |
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

