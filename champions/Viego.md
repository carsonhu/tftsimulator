# Viego (3-cost AttackFighter) · `DA_Viego19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 3, pool 18; traits: Pentakill, Choreographer, Slayer
- **HP** 850 / 1530 / 2754 · **AD** 60 / 90 / 135 · **AS** 0.8 · **Range** 1 · **Armor** 55 · **MR** 55 · **Mana** 0 / 40

### Ability: Singled Out

> Summon 10 + 1 × GenericCalc2 swords around the target. After a brief delay, impale them, dealing 36/54/86 × AP + 3/5/7 × AP physical damage per sword.
> 
> Every 8 takedowns, gain a permanent sword. (Current Takedowns: ⟨live⟩)

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 60 | 90 | 135 |
| KillsToGainSword | 8 | 8 | 8 |
| SwordPerStack | 1 | 1 | 1 |
| NumBaseSwords | 10 | 10 | 10 |
| DamagePerSwordAD | 36 | 54 | 86 |
| DamagePerSwordAP | 3 | 5 | 7 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 36/54/86 × AP + 3/5/7 × AP
- `GenericCalc1` = 10 + 1 × GenericCalc2

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Viego19_Attack`: launch 0.3 s (9 ticks); animation length 2.9 s (87 ticks); release at base AS 0.3 s (9 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Viego19_Spell` (chrono `CD_Viego19_SpellCast`): cast ends 1.8333 s (55 ticks), next attack can start 1.8667 s (56 ticks), mana lock removed 1.8333 s (55 ticks); ended by `FinishCasting via OnEventBegin:CD_Viego19_SpellCast:Unlock`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Viego19_Attack` | AnimChronos | 2.9 | LaunchAttack 0.3, Unlock 0.8 |
| `CD_Viego19_SpellCast` | AnimChronos | 1.8557 | FireSwords 1.0579, Unlock 1.832 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Viego19_SwordStacking`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Viego19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Viego19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Viego19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Viego19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Viego19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3 s (9 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 1.8667 s (56 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.8333 s (55 ticks) | predicted | |
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

