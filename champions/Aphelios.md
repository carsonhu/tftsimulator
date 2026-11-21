# Aphelios (5-cost AttackMarksman) · `DA_Aphelios19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Heartsteel
- **HP** 900 / 1620 / 2916 · **AD** 60 / 90 / 135 · **AS** 0.8 · **Range** 5 · **Armor** 45 · **MR** 45 · **Mana** 40 / 180
- **Unlock**: 2-star Alune or Yone.

### Ability: BANG BANG BANGERS

> Passive: Gain a Chakram every 4 attacks, up to 15. Attacks deal 7/10/200 × AD bonus physical damage for every Chakram equipped. After collecting 15, gain 30%/30%/500% Attack Damage and infinite range.
> 
> Active: Fire bolts at the 3 nearest enemies that deal 280/420/3000 × AD + 60/90/300 × AP physical damage, then split into 16 bolts that deal 0.15/0.15/1 × PhysicalDamageCalc1 physical damage to enemies they pass through. Gain 75% Attack Speed for 4 seconds.
> 
> Heartsteel Upgrade: Start combat with 5 Chakrams equipped.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 60 | 90 | 135 |
| APDamage | 60 | 90 | 300 |
| NumEnemies | 3 | 3 | 3 |
| PostCaseAS | 0.75 | 0.75 | 0.75 |
| PercentSecondaryDamage | 0.15 | 0.15 | 1 |
| ADDamage | 280 | 420 | 3000 |
| HeartsteelStan_ExcessChakramArmorReduction | 10 | 10 | 10 |
| HeartsteelStan_MaxChakrams | 15 | 15 | 15 |
| HeartsteelStan_ADDamage | 7 | 10 | 200 |
| HeartsteelStan_NumAttacksForChakram | 4 | 4 | 4 |
| NumBoltsToSplitTo | 16 | 16 | 16 |
| PostCaseASPerEnemyHit | 0 | 0 | 0 |
| PostCaseASDuration | 4 | 4 | 4 |
| HeartsteelStan_CombatStartChakrams | 5 | 5 | 5 |
| MaxChakramsExtraRange | 6 | 6 | 6 |
| MaxChakramsExtraAD | 0.3 | 0.3 | 5 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 280/420/3000 × AD + 60/90/300 × AP
- `PhysicalDamageCalc2` = 0.15/0.15/1 × PhysicalDamageCalc1
- `PhysicalDamageCalc3` = 7/10/200 × AD
- `AttackSpeedCalc1` = 1 + 0.75
- `GenericCalc1` = 1 + 0

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Aphelios19_AttackNew`: launch 0.3 s (9 ticks), variants 0.3, 0.3342; animation length 2.3 s (69 ticks); release at base AS 0.3 s (9 ticks)
- Attack projectile: DA_Aphelios19_AutoAttackProjectileCalibrum, speed 3000 units/s
- Spell `GA_Aphelios19_Ability` (chrono `CD_Aphelios19_CastSustained`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_Aphelios19.NumEnemies input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_1), used star 2 ×1; curve CT_Aphelios19.NumBoltsToSplitTo input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast), used star 2 ×1; projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Aphelios19_AttackNew` | Chronos/Basic | 2.3 | LaunchAttack 0.3, LaunchAttack 0.3342, Unlock 0.6, Unlock 0.65 |
| `CD_Aphelios19_CastSustained` | Chronos/Basic | 8.6333 | Default 0, LaunchAttack 2.1, LoopBegin 3.1974, LoopEnd 6.2 |
| `CD_Aphelios19_CastAnim` | Chronos/Cast | 2.2009 | StartLasers 0.1453, FireBlasts 0.9834, Unlock 2.1371 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Aphelios19_CombatPassive`, `GA_PlayChronoOnTraitActivation`, `GA_Celebration`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Death`, `GA_Aphelios19_Ability`, `GA_ShopEvents`, `GA_Aphelios19_StartGunManager`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Aphelios19_Ability.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Aphelios19_Ability.txt, Abilities/GA_Aphelios19_CombatPassive.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Aphelios19_Ability.txt, Abilities/GA_Aphelios19_CombatPassive.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Aphelios19_Ability.txt
- `AppliesOnHit`: something in the script is flagged as applying on-hit effects: Abilities/GA_Aphelios19_CombatPassive.txt
- `IsAttack`: damage flagged as an attack (or checked for it): Abilities/GA_Aphelios19_CombatPassive.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-21, `set19champs.Aphelios`, D1); stats, attack speed with the cast's
  buff, the cast lock, the next attack and the mana lock checked on VOD8 at 5-5 and 6-1 (E1-E3)
- Keep in the simulator: **yes** (owner, 2026-11-21: VOD8 recorded for him)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (with Kraken's Fury and Heartsteel (3): HP 900, AD 66 = 60 x 1.10, bonus AD 10%, AS 0.93, armor 53, MR 73, 40/180, 5 hexes) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackMarksman: 10 per attack | confirmed (+10 on the frame of each Kraken launch stack: the release; 14 launches fill 40 -> 180) | E2 |
| Q3 | First attack at combat start: when does it land? | G3: Crescendum's 0.3342 s, released on tick 10 | engine 2 ticks early (VOD 12 and 12.5 ticks; T10 is +1) | E2, E3 |
| Q4 | Attack windup at base AS (attack start to hit / release) | Crescendum's LaunchAttack 0.3342 s (the build's attack_launch 0.3 is the Empowered group's, P15) | consistent (0.3 would release 1 tick earlier still) | E2 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2: never shortened (no PlayRateScalingThreshold) | unchanged at AS 1.53 (E2); **3 ticks shorter at AS 2.34** (E3): open | E2, E3 |
| Q6 | Projectile travel time (ranged only) | attack 3000 units/s; SpellMis 2600; AOEMis 1600; Chakram fixed time by tier | predicted | |
| Q7 | Cast time: cast start to the next attack starting | CastAnim 'Unlock' 2.1371 s on the tick grid + 1 tick (the build's spell timeline follows the 3-star CastSustained path) | confirmed (AS buff 66.5 ticks after the filling launch; next launch 77 ticks after it, engine 77) | E2 |
| Q8 | Does the cast time scale with attack speed? | no (CastAnim at speed 1) | confirmed (66.5 / 67 ticks at AS 0.93 and 1.68) | E2, E3 |
| Q9 | Mana lock: from cast start, when can mana be gained again? | when GE_Aphelios19_AttackSpeedBuff (Mana.Locked) ends, PostCaseASDuration after the Unlock | confirmed to a tick or two (buff end shown 186 / 185.5 ticks after the filling launch; engine 187) | E2, E3 |
| Q10 | Does the mana lock scale with attack speed? | no | confirmed | E2, E3 |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 below 3 stars | consistent (no Kraken stack from the cast) | E2 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | 3 bolts at the 3 nearest (repeated when fewer), PhysicalDamageCalc1 each; split bolts PhysicalDamageCalc2 to every other enemy within BoltTravelDistance; Chakrams PhysicalDamageCalc3 each per launch | predicted (GEs read); tooltip 368 = 280 x 1.10 + 60, 55 = 15%, Chakram 8 = 7 x 1.10 | D1, E1 |
| Q14 | Passives and other mechanics that need modelling | Chakrams (every 4th launch, up to 15; Bias starts at 5); the 15-Chakram AD buff | implemented; not seen on VOD8 (no damage numbers; Bias unknown) | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-21 (3 stars in expectation) | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD8 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-21-2026_12-18-17-802/` `…PBE_11-21-2026_13-2-9-650.mp4`
(owner's game, 2026-11-21, 60 fps). Client rls-19.1.0.6013636 (not exported; owner: only a Graves crash fix), so
6011486 is assumed. Aphelios 1 star, Heartsteel (3) (Bias unknown), Slayer, True Damage, Juggernaut on the board.
Items matched to client textures: Kraken's Fury at 5-5; Guinsoo's Rageblade + Kraken's Fury at 6-1. Launch marks:
Kraken's Fury's +3.5% AD per Combat.Event.LaunchAttack on the panel's bonus AD % (`tools/vod_text_changes.py --field ad`),
up to 15 stacks; mana and AS from `--field mana` / `--field as`.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 29:42-29:55 (5-5 planning) | 60 | inspection panel, ability tooltip | 900 / 900, 40 / 180, Back, 5 Hex; AD 66, bonus AD 10%, AP 0%, armor 53, MR 73, AS 0.93, crit 25%; tooltip Chakram 8, Damage 368 = 280 x AD + 60 x AP, Bolt 55 = 15% | engine with Kraken's Fury and Heartsteel (3): AS 0.8 x (1 + 0.10 + ApheliosAS 0.06) = 0.928, his own Heartsteel bonus counted; 368 = 280 x 1.10 + 60; 8 = 7 x 1.10 (`test_vod8_5_5_panel_attack_speed`) | Q1, Q13 |
| E2 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 f107940-109320 (5-5, away fight) | 60 | round timer, bonus AD %, mana, AS text | timer to 30 at f107962; launches f107986 (12 ticks in), 108050, 108134 (a 42-tick gap: target change?), then 63-66 frames apart to the 14th at f108872 (mana 180 -> 0); AS 1.53 at f109005; launch f109026 (Kraken's 15th: AS 1.65); AS 1.05 at f109244; mana +10 at f109254 | engine (`test_vod8_5_5_cast`): first release tick 10 (VOD 12); 32-33 ticks apart (0.928 AS); cast the tick after the 14th; AS buff 66 ticks after the 14th (VOD 66.5); next launch 77 ticks after (VOD 77); buff and mana lock end 187 ticks after (VOD AS change at 186) | Q2-Q5, Q7-Q11 |
| E3 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 f118900-120300 (6-1) | 60 | bonus AD %, mana, AS text | Guinsoo's stacks every 60 frames from f119107 (combat start f119047); first launch f119072 (12.5 ticks); 14 launches, gaps 57-39 frames; the 14th at f119697 (mana 0); AS 1.68 -> 2.34 at f119831 (AS buff + a Guinsoo stack); launch f119845 (Kraken's 15th); AS 2.08 at f120068 (buff over); mana +10 at f120072 | engine (`test_vod8_6_1_cast`): AS buff at +66 (VOD 67); next launch 77 ticks after the 14th, **VOD 74**: the fresh attack after the cast released 7 ticks after the buff at AS 2.34, against 10.5 at AS 1.53 (E2); fits a windup that shrinks once the period is under ~0.6 s (Crescendum's Unlock 0.6 s; G20 with T x 1.5 s = 0.6), not applied (one sighting); buff end 185.5 ticks after the 14th (engine 187) | Q5, Q8-Q10 |

## Decisions and notes

- 2026-11-21, D1 (implemented, `set19champs.Aphelios`; its docstring cites the scripts):
  - **Attack:** CD_Aphelios19_AttackNew's AttackGroup takes the first active of Crescendum (no filter) and Empowered
    (SharedSets.GenericUseEmpoweredAttack, which his cast's AS buff grants), so Crescendum always plays: LaunchAttack
    0.3342 s, module length 1.5 s, bUseRateScalingThreshold without a threshold (G2). The snapshot's attack_launch
    0.3 is Empowered's (ledger P15); the class takes the later LaunchAttack event of the chrono.
  - **Passive (GA_Aphelios19_CombatPassive):** Chakrams start at HeartsteelStan_CombatStartChakrams for a Heartsteel
    Bias (SpellUpgradeTierIsActive + Selected), else 0; each exact Combat.Event.LaunchAttack counts (TrackAttack: every
    4th adds one, up to 15) and fires a volley: each Chakram hits his attack target for PhysicalDamageCalc3
    (GE_Aphelios19_Heartsteel_ChakramDamage: physical, on-spell, crit only with Precision) after a fixed flight, the
    ChakramVariantTimes tier at or below clamp(interval x 0.35 / 2, 0.03, 0.4). Simulated launches don't count
    (OnlyMatchExact). At 15, the next attack damage's PreMitigation applies GE_Aphelios19_MaxChakramBuff once (+30% AD,
    range). The tier table and leg constants are script class defaults the snapshot doesn't keep: typed (P15).
  - **Cast below 3 stars:** CD_Aphelios19_CastAnim (speed 1). 'FireBlasts' 0.9834 s: the NumEnemies nearest enemies,
    repeated when fewer (GetRepeatingListFromTargetData: one enemy takes all three), each a SpellMis (2600 units/s):
    GE_Aphelios19_PrimaryDamage (PhysicalDamageCalc1) and NumBoltsToSplitTo AOEMis bolts (1600 units/s,
    BoltTravelDistance 540 units) round it: GE_Aphelios19_AOEDamage (PhysicalDamageCalc2, AOE) to each other enemy a
    bolt overlaps. Simulated: each enemy within 540 units of a primary victim, centre to centre, hit once per primary.
    'Unlock' 2.1371 s: GE_Aphelios19_AttackSpeedBuff (+PostCaseAS for PostCaseASDuration, with Mana.Locked), the
    cast's mana lock removed, FinishCasting; cast lock = Unlock + 1 tick (as Yasuo). With 2 dummies the three bolts go
    nearest, other, nearest (the game sorts them right to left first: open).
  - **3 stars (DoSpecialCast):** CD_Aphelios19_CastSustained; 'LaunchAttack' 2.1 s and every ThreeStarRefireDelay
    (0.2 s) after, until the round ends: no Unlock, so no more attacks. Each shot picks at random among all enemies and
    all unoccupied hexes, PrimaryDamage at once and split bolts from there. Simulated in expectation (as crits): each
    enemy per shot Calc1 / 55 and Calc2 x (hexes within 540 units of it but his own) / 55, assuming no other units on
    the board.
  - Open questions: docs/OPEN-QUESTIONS.md 7ab.
