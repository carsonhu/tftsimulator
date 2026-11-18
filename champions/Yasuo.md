# Yasuo (4-cost AttackFighter) · `DA_Yasuo19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 4, pool 10; traits: True Damage, Slayer
- **HP** 1100 / 1980 / 3564 · **AD** 60 / 90 / 135 · **AS** 0.85 · **Range** 1 · **Armor** 65 · **MR** 65 · **Mana** 0 / 30
- **Unlock**: 7 unique star levels of True Damage or Slayer Champions.

### Ability: Last Breath

> Dash and thrust forward, dealing 165/250/1400 × AD physical damage to enemies in a line.
> 
> Every 3rd cast, knock up the target and deal 400/600/2500 × AD physical damage. Then slam them down, dealing 1 × GenericCalc1 + 1 × GenericCalc2 physical damage to enemies within 1/1/2 Hex.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 60 | 90 | 135 |
| UltDamageAD | 400 | 600 | 2500 |
| SlashDamageAD | 165 | 250 | 1400 |
| SlashHexLength | 2 | 2 | 2 |
| UltDamageAOEAD | 180 | 270 | 1500 |
| AOEHexRadius | 1 | 1 | 2 |
| UltDamageAOEAP | 30 | 45 | 200 |
| TargetSearchRadius | 1 | 1 | 1 |
| NumCastsToUlt | 3 | 3 | 3 |
| UltKnockupDuration | 1 | 1 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 165/250/1400 × AD
- `PhysicalDamageCalc2` = 400/600/2500 × AD
- `GenericCalc1` = 180/270/1500 × AD
- `GenericCalc2` = 30/45/200 × AP
- `PhysicalDamageCalc3` = 1 × GenericCalc1 + 1 × GenericCalc2

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Yasuo19_Attack`: launch 0.26 s (7.8 ticks), variants 0.26, 0.2775, 0.2823; animation length 1.6333 s (49 ticks); release at base AS 0.26 s (7.8 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Yasuo19_Spell` (chrono `CD_Yasuo19_UltWhirlwind`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Yasuo19_Attack` | Chronos | 1.6 | LaunchAttack 0.26, LaunchAttack 0.2775, LaunchAttack 0.2823, Unlock 0.6533, Unlock 0.6664 |
| `CD_Yasuo19_BaseSpell` | Chronos | 0.8709 | Default 0, Thrust 0.2204, Damage 0.4115, Unlock 0.8568 |
| `CD_Yasuo19_BaseSpell_NoDash` | Chronos | 0.716 | Damage 0.194, Unlock 0.6409 |
| `CD_Yasuo19_UltKnockup` | Chronos | 1.4355 | Default 0, Knockup 0.1273, Damage1 0.1888, Damage2 0.5278, Slam 1.1514, ReturnToHex 1.2504, Unlock 1.4317 |
| `CD_Yasuo19_UltNoKnockup` | Chronos | 1.4355 | Default 0, Knockup 0.1273, Damage1 0.1888, Damage2 0.5278, Slam 1.1514, ReturnToHex 1.2504, Unlock 1.4317 |
| `CD_Yasuo19_UltWhirlwind` | Chronos | 0.9999 | FireWind 0.3025 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_TrueDamage19_PlayChronoOnTraitActivation`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Yasuo19_Spell`, `GA_ShopEvents`, `GA_Yasuo19_SpellIndicatorHandler`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Yasuo19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Yasuo19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Yasuo19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Yasuo19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.26 s (7.8 ticks) | predicted | |
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

