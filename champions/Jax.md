# Jax (2-cost MagicFighter) · `DA_Jax19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive ⟨computed in game: TFTStageMagnitude⟩; MovementSpeed + 200; ManaMax at least 10)
- **Cost** 2, pool 25; traits: EDM, Bodyguard, Swiftstriker
- **HP** 750 / 1350 / 2430 · **AD** 15 / 22.5 / 33.75 · **AS** 0.75 · **Range** 1 · **Armor** 50 · **MR** 50 · **Mana** 0 / 30

### Ability: Instant Crush

> Bash the current target, dealing 200/300/480 × AP magic damage and healing for 0.2 of damage dealt. Gain [ASOnCast?] Attack Speed for the rest of combat.
> 
> EDM Upgrade: Fire beams at the 2 nearest enemies that deal 50/75/115 × AP50/75/115 × AP magic damage, reduced by [EDM_DamageReductionPerEnemyHit ?] for each enemy they pass through.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 15 | 22.5 | 33.75 |
| PercentHeal | 0.2 | 0.2 | 0.2 |
| EDM_AttackSpeed | 0.08 | 0.08 | 0.08 |
| EDM_NumBeams | 2 | 2 | 2 |
| EDM_APDamage | 50 | 75 | 115 |
| EDM_DamageReductionPerEnemyHit | 0.4 | 0.4 | 0.4 |
| APDamage | 200 | 300 | 480 |
| ASonCast | 0.15 | 0.15 | 0.15 |
| ASDuration | 60 | 60 | 60 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 200/300/480 × AP
- `ShieldCalc1` = ? × AP + ? × max HP
- `MagicDamageCalc2` = 50/75/115 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Jax19_AttackNew`: launch 0.3239 s (9.72 ticks); animation length 2.1333 s (64 ticks); release at base AS 0.3239 s (9.72 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Jax19_Spell` (chrono `CD_Jax19_SlamOnTarget`): cast ends 0.5667 s (17 ticks), next attack can start 0.6 s (18 ticks), mana lock removed 0.5667 s (17 ticks); ended by `FinishCasting via OnEventBegin:CD_Jax19_SlamOnTarget:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Jax19_SlamOnTarget` | Chronos/Ability | 0.5759 | DealDamage 0.42, Unlock 0.5581 |
| `CD_Jax19_AttackNew` | Chronos/Basic | 2.1 | LaunchAttack 0.3239, Unlock 0.8532 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_ForceSequentialAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_ShopEvents`, `GA_Jax19_Spell`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Jax19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Jax19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Jax19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Jax19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Jax19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3239 s (9.72 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 0.6 s (18 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.5667 s (17 ticks) | predicted | |
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

