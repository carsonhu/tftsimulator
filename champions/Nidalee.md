# Nidalee (5-cost MagicFighter) · `DA_Nidalee19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** MagicFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Mariachi, Choreographer
- **HP** 1200 / 2160 / 3888 · **AD** 50 / 75 / 112.5 · **AS** 0.8 · **Range** 6 · **Armor** 65 · **MR** 65 · **Mana** 20 / 45

### Ability: Pounce Party/Dance of Life

> Pounce Party: Pounce 4/4/99 times on enemies, dealing 125/185/1500 × AP magic damage, increased by 40% each pounce.
> 
> Dance of Life: Heal 325/500/2000 × AP. Hurl a javelin at the target, dealing 360/540/3000 × AP magic damage and scattering 3 flowers around them. Flowers deal 80/120/500 × AP magic damage to enemies in a 1 Hex radius after a brief delay.
> 
> Casts Pounce Party in Cougar Form and Dance of Life in Human form.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 50 | 75 | 112.5 |
| ExtraDamagePercentPerPounce | 0.4 | 0.4 | 0.4 |
| SpearDamageAP | 360 | 540 | 3000 |
| PounceDamageAP | 125 | 185 | 1500 |
| FlowerDamageAP | 80 | 120 | 500 |
| AOEHexRange | 1 | 1 | 1 |
| HealAP | 325 | 500 | 2000 |
| NumPounces | 4 | 4 | 99 |
| PounceSearchRadius | 2 | 2 | 2 |
| UniqueHumanDurability | 0 | 0 | 0 |
| UniqueCougarDA | 0 | 0 | 0 |
| HealthThresholdCougar | 0.75 | 0.75 | 0.75 |
| HealthThresholdHuman | 0.5 | 0.5 | 0.5 |
| WeakenLevel | 0 | 0 | 0 |
| WeakenDuration | 0 | 0 | 0 |
| NumFlowers | 3 | 3 | 3 |
| HealPercentWeaken | 0 | 0 | 0 |
| CougarManaReduction | 15 | 15 | 15 |
| 3Star5CostMaxHealthRegen | 0 | 0 | 0.2 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 360/540/3000 × AP
- `MagicDamageCalc2` = 125/185/1500 × AP
- `MagicDamageCalc3` = 80/120/500 × AP
- `DurabilityCalc1` = 1 + 0
- `HealthCalc1` = 325/500/2000 × AP
- `GenericCalc1` = ⟨computed in game: MMC_Nidalee19_HPAboveThreshold⟩

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Nidalee19_Attack`: launch 0.2669 s (8.01 ticks), variants 0.2669, 0.3213; animation length 1.5667 s (47 ticks); release at base AS 0.2669 s (8.01 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Nidalee19_Spell` (chrono `CD_Nidalee19_TransformPoof`): cast ends 0.8333 s (25 ticks), next attack can start 0.8667 s (26 ticks), mana lock removed 0.8333 s (25 ticks); ended by `FinishCasting via OnEventBegin:CD_Nidalee19_SlideBack:Unlock`
- Spell `GA_Nidalee19_RunAwayChecker` (chrono `CD_Nidalee19_EscapePounce`): cast ends 0.6 s (18 ticks), next attack can start 0.6333 s (19 ticks), mana lock removed –; ended by `FinishCasting via OnEventBegin:CD_Nidalee19_EscapePounce:Arrived`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Nidalee19_3Star5CostAllyBounce` | 3Star5Cost | 0.6 | Arrived 0.56 |
| `CD_Nidalee19_Attack` | Chronos | 1.5667 | LaunchAttack 0.2669, LaunchAttack 0.3213, Unlock 0.5333, Unlock 0.6267 |
| `CD_Nidalee19_EscapePounce` | Chronos | 0.5998 | Arrived 0.5867 |
| `CD_Nidalee19_FinalPounce` | Chronos | 0.6002 | Damage 0.5504, Arrived 0.5934 |
| `CD_Nidalee19_FlowerBloom` | Chronos | 0.6499 | Bloom 0 |
| `CD_Nidalee19_LongPounce` | Chronos | 0.5998 | Damage 0.5695, Arrived 0.5867 |
| `CD_Nidalee19_ShortPounce1` | Chronos | 0.4299 | Damage 0.3942, Arrived 0.425 |
| `CD_Nidalee19_ShortPounce2` | Chronos | 0.4506 | Damage 0.4132, Arrived 0.4455 |
| `CD_Nidalee19_ShortPounce3` | Chronos | 0.4701 | Damage 0.4311, Arrived 0.4648 |
| `CD_Nidalee19_ShortPounce4` | Chronos | 0.4903 | Damage 0.4496, Arrived 0.4847 |
| `CD_Nidalee19_SlideBack` | Chronos | 0.2042 | Arrived 0.2, Unlock 0.2029 |
| `CD_Nidalee19_Spear` | Chronos | 1.4899 | Heal 0, Throw 0.7567, Unlock 1.4829 |
| `CD_Nidalee19_CougarAttack` | Chronos/OLD | 1.3333 | LaunchAttack 0.3213, Unlock 0.5333 |
| `CD_Nidalee19_CougarCelebration` | Chronos/OLD | 2.136 | Default 0, Loop 1.3027 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Play3Star5CostCamera`, `GA_ReduceOutgoing3StarDamage`, `GA_GainDamageReductionAt3Star`, `GA_Play3Star5CostCamera`, `GA_AutoAttack`, `GA_Nidalee19_LaunchAttack_MeleeOrRanged`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Nidalee19_Spell`, `GA_ShopEvents`, `GA_Nidalee19_RunAwayChecker`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Nidalee19_RunAwayChecker.txt, GA_Nidalee19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Nidalee19_LaunchAttack_MeleeOrRanged.txt
- `GE_ManaLock`: applies mana lock: GA_Nidalee19_Spell.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2669 s (8.01 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 0.8667 s (26 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.8333 s (25 ticks) | predicted | |
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

