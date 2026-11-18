# Vi (5-cost AttackFighter) · `DA_Vi19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 5, pool 9; traits: EDM, Juggernaut
- **HP** 1200 / 2160 / 3888 · **AD** 80 / 120 / 180 · **AS** 0.9 · **Range** 1 · **Armor** 65 · **MR** 65 · **Mana** 0 / 50

### Ability: Drop the Beatdown

> Summon 2 giant hologram fists. Gain 300/400/500 × AP Shield for 2 seconds and grant 125/165/215 × AP Shield to 2/2/10 nearby allies. Slam the target 5/5/40 times, each dealing 130/200/1000 × AD physical damage to them and 35/55/400 × AD damage to all other enemies within 2 hexes.
> 
> EDM Upgrade: Slam one more time and heal 15% of damage dealt by this ability.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 80 | 120 | 180 |
| ShieldAmountAP | 300 | 400 | 500 |
| ADDamageOnTarget | 130 | 200 | 1000 |
| ShieldDuration | 2 | 2 | 2 |
| NumBonusAlliesForShield | 2 | 2 | 10 |
| BoardSlamsTotal | 5 | 5 | 40 |
| ADDamageOnOtherUnits | 35 | 55 | 400 |
| EDMUpgradeHealPercent | 0.15 | 0.15 | 0.15 |
| EDMExtraSlams | 1 | 1 | 1 |
| NumStrikesForSimulatedAuto | 2 | 2 | 2 |
| AllyShieldPercentAP | 125 | 165 | 215 |

Formulas (as stored; AD and AP are multipliers):

- `ShieldCalc1` = 300/400/500 × AP
- `ShieldCalc2` = 125/165/215 × AP
- `PhysicalDamageCalc1` = 130/200/1000 × AD
- `PhysicalDamageCalc2` = 35/55/400 × AD

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Vi19_Attack`: launch 0.2724 s (8.17 ticks), variants 0.2724, 0.2924, 0.3526; animation length 1.6333 s (49 ticks); release at base AS 0.2724 s (8.17 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Vi19_Spell` (chrono `CD_Vi19_SpellIntro`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_EDM19.UpgradeAbility input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast), used star 2 ×1; projectile (hit time depends on travel) ×189

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Vi19_3Star5Cost_JaxSpawnCeremony` | Chronos/Base | 0.5743 | Targetable 0.1513, Land 0.5016, Unlock 0.5428 |
| `CD_Vi19_3Star5Cost_Jax_Size` | Chronos/Base | 89.9866 | Default 0, Loop 0.9997 |
| `CD_Vi19_Attack` | Chronos/Base | 1.1333 | LaunchAttack 0.2724, LaunchAttack 0.2924, LaunchAttack 0.3526, Unlock 0.4533, Unlock 0.6533, Unlock 0.8267 |
| `CD_Vi19_SpellIntro` | Chronos/SpellAnims | 0.6462 | ShieldSelfAndAlly 0.3051, SpawnFists 0.4522, StartSlamming 0.5664 |
| `CD_Vi19_SpellOutro` | Chronos/SpellAnims | 0.5997 | EndSpell 0.396 |
| `CD_Vi19_Spell_LeftGroundStrike` | Chronos/SpellAnims | 0.5468 | Slam 0.2824 |
| `CD_Vi19_Spell_RightGroundStrike` | Chronos/SpellAnims | 0.5468 | Slam 0.2191 |
| `CD_Vi19_ShieldNew` | Chronos/SpellVFX | 6.0928 | Default 0, Loop 0.2001 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Play3Star5CostCamera`, `GA_Play3Star5CostCamera`, `GA_ReduceOutgoing3StarDamage`, `GA_GainDamageReductionAt3Star`, `GA_Vi19_3Star5Cost_Passive`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Vi19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Vi19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Vi19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Vi19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Vi19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2724 s (8.17 ticks) | predicted | |
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

