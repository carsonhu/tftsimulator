# Smeech (5-cost AttackSpecialist_Time) · `DA_Smeech19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackSpecialist_Time: "Specialists generate resources in a unique way." ()
- **Cost** 5, pool 9; traits: Jazz, Slayer
- **HP** 1300 / 2340 / 4212 · **AD** 70 / 105 / 157.5 · **AS** 0.9 · **Range** 1 · **Armor** 65 · **MR** 65 · **Mana** 0 / 4
- **Unlock**: Have 8 or more non-unique traits active

### Ability: Upswing

> Passive: Gain between 1/1/4 and 4/4/10 Beats per attack. Every 4 seconds, cast.
> 
> Active: Gain 250/375/40000 × AP Shield for 3/3/10 seconds and deal 100/150/4000 × AD physical damage to all enemies within 2 hexes. Then strike the current target 4 times, each dealing 240/360/2600 × AD physical damage + 12/18/350 × AD per Beat.
> 
> After unleashing 15 Beats, gain an emblem of a trait you don't have active and increase the number of Beats required.
> 
> (Unleashed Beats: ⟨⟩/⟨⟩)

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 70 | 105 | 157.5 |
| BaseBeatReq | 15 | 15 | 15 |
| ResourcePerSecond | 1 | 1 | 4 |
| BeatGainMax | 4 | 4 | 10 |
| BeatGainMin | 1 | 1 | 4 |
| DamagePerBeat | 12 | 18 | 350 |
| PassiveDuration | 4 | 4 | 4 |
| MaxStrikes | 4 | 4 | 4 |
| BaseDamagePerStrike | 240 | 360 | 2600 |
| MinStrikes | 4 | 4 | 4 |
| ShieldDuration | 3 | 3 | 10 |
| ShieldAP | 250 | 375 | 40000 |
| AoEDamageAD | 100 | 150 | 4000 |
| SpecialEnemyDamage | 7000 | 7000 | 7000 |
| SpecialDamageDuration | 1000000 | 1000000 | 1000000 |
| SpecialDamageInterval | 0.3 | 0.3 | 0.3 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc3` = 240/360/2600 × AD
- `PhysicalDamageCalc2` = 12/18/350 × AD
- `GenericCalc1` = 15
- `GenericCalc3` = 1
- `ShieldCalc1` = 250/375/40000 × AP
- `PhysicalDamageCalc1` = 100/150/4000 × AD
- `MagicDamageCalc3` = 7000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Smeech19_Attack`: launch 0.1602 s (4.81 ticks), variants 0.1602, 0.325, 0.35; animation length 2.0333 s (61 ticks); release at base AS 0.1602 s (4.81 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Smeech19_Spell` (chrono `CD_Smeech19_Leap`): cast ends –, next attack can start –, mana lock removed –; **script reads attack speed**; **no cast end found**
  - notes: chrono not found switch(Temp_bool_Variable_2){false: Temp_object_Variable_18; true: Temp_object_Variable_17; default: K2Node_Select_Default_2} ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Smeech19_Attack` | Chronos | 1.7333 | LaunchAttack 0.1602, LaunchAttack 0.325, LaunchAttack 0.35, Unlock 0.5, Unlock 0.55, Unlock 0.6932 |
| `CD_Smeech19_BeatSpawn_Mis` | Chronos | 9.9928 | LaunchProjectile 1 |
| `CD_Smeech19_GainEmblem` | Chronos | 1.9996 | GainEmblem 1 |
| `CD_Smeech19_SpecialCast` | Chronos | 2.1 | GainShield 0.2285, AoE 0.775, SpawnBeats 0.8072, Unlock 1.2442 |
| `CD_Smeech19_SpecialEnemyTar` | Chronos | 10 | Instakill 9 |
| `CD_Smeech19_Spell` | Chronos | 0.6356 | Strike 0.0937, Strike 0.2781, Unlock 0.4478, Unlock 0.6322 |
| `CD_Smeech19_SpellJazzSpin` | Chronos | 1.639 | GainShield 0.2285, AoE 0.7235, SpawnBeats 0.7257, Unlock 1.0885 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Play3Star5CostCamera`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Smeech19_Spell`, `GA_ShopEvents`, `GA_Smeech19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Smeech19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Smeech19_Passive.txt, Abilities/GA_Smeech19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Smeech19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Smeech19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Smeech19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackSpecialist_Time | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.1602 s (4.81 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | – | open | |
| Q8 | Does the cast time scale with attack speed? | script reads AS | open | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | open | |
| Q10 | Does the mana lock scale with attack speed? | script reads AS | open | |
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

