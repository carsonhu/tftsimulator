# Baron Nashor (5-cost AttackFighter) · `DA_BaronNashor19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 5, pool 9; traits: One Monster Band
- **HP** 2500 / 4500 / 8100 · **AD** 140 / 210 / 315 · **AS** 0.55 · **Range** 2 · **Armor** 80 · **MR** 80 · **Mana** 80 / 120
- Other stats: MovementSpeed 250, TeamSizeContribution 2
- **Unlock**: Collect all 5 members of Baron&#x27;s ensemble. / Deal 60000 damage with your strongest Malzahar.

### Ability: Assemble the Ensemble

> Summon an 8-man orchestra and a Riff Herald, knocking up all enemies for 1 seconds. Deal 550/825/2475 × AD physical damage and 650/1000/3000 × AP magic damage split among all enemies.
> 
> Each minion attacks 4 times, with each attack dealing 33/50/250 × AD physical damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 140 | 210 | 315 |
| NumEnemiesToTarget | 4 | 4 | 4 |
| APDamage | 650 | 1000 | 3000 |
| ADDamage | 550 | 825 | 2475 |
| ADDamagePerSummonAttack | 33 | 50 | 250 |
| NumAttacksPerSummon | 4 | 4 | 4 |
| UniqueTrait_StatSteal | 0.05 | 0.05 | 0.3 |
| BenchPercentScaleDecrease | 0.9 | 0.9 | 0.9 |
| KnockupDuration | 1 | 1 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 33/50/250 × AD
- `PhysicalDamageCalc2` = 550/825/2475 × AD
- `MagicDamageCalc1` = 650/1000/3000 × AP
- `GenericCalc1` = 1 + 0.05/0.05/0.3
- `GenericCalc2` = 1 + -0.05/-0.05/-0.3

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_BaronNashor19_Attack`: launch 0.4224 s (12.67 ticks); animation length 1.3333 s (40 ticks); release at base AS 0.576 s (17.28 ticks)
- Attack projectile: DA_BaronNashor19_AutoAttackProjectile, speed 1300 units/s
- Spell `GA_BaronNashor19_Spell` (chrono `CD_BaronNashor19_SpellNew`): cast ends 1.9333 s (58 ticks), next attack can start 1.9667 s (59 ticks), mana lock removed 1.9333 s (58 ticks); ended by `FinishCasting via OnEventBegin:CD_BaronNashor19_SpellNew:Unlock`
  - notes: projectile (hit time depends on travel) ×27

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_BaronNashor19_Accordian_Attack` | Accordian | 1.6667 | LaunchAttack 0.2671, Unlock 0.6667 |
| `CD_BaronNashor19_Accordian_CombineCeremony` | Accordian | 5.8333 | LaunchAttack 0.2671, Unlock 0.6667, Jump 1.6492, RAA!!! 3.5893, Disappear 4.8563 |
| `CD_BaronNashor19_Accordian_Death` | Accordian | 1.501 | Done 1.0036 |
| `CD_BaronNashor19_Accordian_SpawnCeremony` | Accordian | 0.5017 | Unlock 0.4967 |
| `CD_BaronNashor19_Banjo_Attack` | Banjo | 0.9333 | LaunchAttack 0.4, Unlock 0.75 |
| `CD_BaronNashor19_Banjo_CombineCeremony` | Banjo | 5.8333 | Jump 1.0731, RAA!!! 3.5893, Disappear 4.8563 |
| `CD_BaronNashor19_Banjo_Death` | Banjo | 1.5 | Done 1.0029 |
| `CD_BaronNashor19_Banjo_SpawnCeremony` | Banjo | 0.5002 | Unlock 0.4925 |
| `CD_BaronNashor19_Attack` | BaronNashor/Chronos/Basic | 1.3333 | LaunchAttack 0.4224, Unlock 0.76 |
| `CD_BaronNashor19_CombineCeremony` | BaronNashor/Chronos/Basic | 5.8333 | RAA!!! 3.5893 |
| `CD_BaronNashor19_SpellNew` | BaronNashor/Chronos/Spell | 1.9237 | Summon1 0.5019, Unlock 1.9092 |
| `CD_BaronNashor19_Disappear` | CD_BaronNashor19_Disappear | 0.9894 | Disappear 0.7698 |
| `CD_BaronNashor19_Drum_Attack` | Drum | 1 | LaunchAttack 0.26, LaunchAttack 0.27, Unlock 0.4, Unlock 0.452 |
| `CD_BaronNashor19_Drum_CombineCeremony` | Drum | 5.8333 | Jump 1.2179, RAA!!! 3.5893, Disappear 4.8563 |
| `CD_BaronNashor19_Drum_Death` | Drum | 0.8012 | Done 0.5357 |
| `CD_BaronNashor19_Drum_SpawnCeremony` | Drum | 0.504 | Unlock 0.4967 |
| `CD_BaronNashor19_RiftHerald_Attack` | RiftHerald | 2.3333 | LaunchAttack 0.2372, Unlock 0.9332 |
| `CD_BaronNashor19_RiftHerald_CombineCeremony` | RiftHerald | 5.8333 | Jump 0, RAA!!! 3.5893, Disappear 4.8563 |
| `CD_BaronNashor19_RiftHerald_Death` | RiftHerald | 1.5 | Done 1.0029 |
| `CD_BaronNashor19_RiftHerald_SpawnCeremony` | RiftHerald | 1.4556 | Unlock 1.4398 |
| `CD_BaronNashor19_Trumpet_Attack` | Trumpet | 1 | LaunchAttack 0.27, Unlock 0.452 |
| `CD_BaronNashor19_Trumpet_CombineCeremony` | Trumpet | 5.8333 | Jump 1.8309, RAA!!! 3.5893, Disappear 4.8563 |
| `CD_BaronNashor19_Trumpet_Death` | Trumpet | 1.5038 | Done 1.0055 |
| `CD_BaronNashor19_Trumpet_SpawnCeremony` | Trumpet | 0.5034 | Unlock 0.4967 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_BaronNashor19_Passive`, `GA_Death`, `GA_BaronNashor19_3Star5Cost_BonusInstruments`, `GA_ReduceOutgoing3StarDamage`, `GA_Play3Star5CostCamera`, `GA_GainDamageReductionAt3Star`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Celebration`, `GA_MoveToTarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_BaronNashor19_Spell`, `GA_FaceAATarget`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): BaronNashor/GA_BaronNashor19_Spell.txt
- `GE_ManaLock`: applies mana lock: BaronNashor/GA_BaronNashor19_Spell.txt
- `GE_UnitStopAttackingMovingCasting`: stops the unit attacking/moving/casting: BaronNashor/3Star5Cost/GA_BaronNashor19_3Star5Cost_BonusInstruments.txt, BaronNashor/GA_BaronNashor19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: BaronNashor/BaronMinionAttacks/GA_BaronNashor19_SummonLaunchMeleeAttack.txt, BaronNashor/BaronMinionAttacks/GA_BaronNashor19_SummonLaunchProjectileAttack.txt, BaronNashor/GA_BaronNashor19_SummonAttackTracker.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.4224 s (12.67 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1300 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.9667 s (59 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.9333 s (58 ticks) | predicted | |
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

