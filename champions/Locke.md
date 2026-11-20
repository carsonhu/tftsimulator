# Locke (4-cost MagicAssassin) · `DA_Locke19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6005555.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6005555.Set19.Shipping.pbe`

- **Role** MagicAssassin: "Attacks grant 10 Mana. Take 15% less damage from all enemies except the current target." (ManaPerAttack + 10; ManaMax at least 10; MovementSpeed + 200; Threat + -10)
- **Cost** 4, pool 10; traits: Rock, Swiftstriker
- **HP** – · **AD** 10 / 15 / 22.5 · **AS** 0.9 · **Range** 1 · **Armor** 65 · **MR** 65 · **Mana** 0 / 30

### Ability: Pursue Sin (The Soul Nail Song)

> Passive: Attacks deal 45/68/500 × AP bonus magic damage. All damage Locke deals to enemies is increased by 15% for each mark he has applied to them.
> 
> Active: Hurl 3 Soul Nails at the furthest enemy within 4 hexes, each dealing 15/22/400 × AP magic damage and marking all enemies hit. Then, teleport to the enemy and deal 135/205/2000 × AP magic damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 10 | 15 | 22.5 |
| BonusPercentPerNail | 0.15 | 0.15 | 0.15 |
| SearchHexRange | 4 | 4 | 4 |
| APDamage | 15 | 22 | 400 |
| AP_DamageOnAttack | 45 | 68 | 500 |
| FinalAPDamage | 135 | 205 | 2000 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 15/22/400 × AP
- `MagicDamageCalc2` = 45/68/500 × AP
- `MagicDamageCalc3` = 135/205/2000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Locke19_Attack`: launch 0.2945 s (8.83 ticks), variants 0.2945, 0.3178, 0.3318; animation length 3.1667 s (95 ticks); release at base AS 0.2945 s (8.83 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Locke19_Spell` (chrono `CD_Locke19_Windup`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: projectile (hit time depends on travel) ×18

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Locke19_Attack` | Chronos | 3.1667 | LaunchAttack 0.2945, LaunchAttack 0.3178, LaunchAttack 0.3318, Unlock 1.1732, Unlock 1.1866, Unlock 1.2664 |
| `CD_Locke19_CastAnim` | Chronos | 0.801 | Teleport 0.2649, Damage 0.6379, Unlock 0.7716 |
| `CD_Locke19_Windup` | Chronos | 1.0395 | NormalProjectile 0.3154, NormalProjectile 0.6394, FinalProjectile 0.9788 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Locke19_Spell`, `GA_ShopEvents`, `GA_Locke19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Locke19_Spell.txt
- `AppliesOnHit`: something in the script is flagged as applying on-hit effects: GA_Locke19_Passive.txt
- `IsAttack`: damage flagged as an attack (or checked for it): GA_Locke19_Passive.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Locke19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Locke19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Locke19_Spell.txt

### Changed since `rls-19.1.0.5995286.Set19.Shipping.pbe`

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicAssassin | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2945 s (8.83 ticks) | predicted | |
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

