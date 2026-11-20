# Seraphine (2-cost MagicCaster) · `DA_SeraphineIndie19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6005555.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6005555.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Indie
- **HP** 700 / 1260 / 2268 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 50
- **Unlock**: Reroll 4 times before Stage 2 Carousel.

### Ability: Livestream of Note

> Indie: Release a stream of notes at the target while posing for the fans, dealing 550/825/1240 × AP magic damage over 2.5 seconds.
> 
> Rising Star: Release bonus notes at nearby enemies.
> 
> Superstar: Toss high notes at every enemy.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| ShieldAmount | 0 | 0 | 0 |
| DamageAP | 550 | 825 | 1240 |
| HealRadius | 0 | 0 | 0 |
| HealAmount | 0 | 0 | 0 |
| ShieldDuration | 0 | 0 | 0 |
| RewardsForFirstUpgrade | 1 | 1 | 1 |
| PopularityPerFreeReroll | 1 | 1 | 1 |
| PopularityPerPaidReroll | 2 | 2 | 2 |
| RewardsForSecondUpgrade | 4 | 4 | 4 |
| PopularityForReward | 20 | 20 | 20 |
| HighNoteDamageAP | 45 | 68 | 100 |
| ExtraNoteDamageAP | 20 | 30 | 45 |
| RisingStarExtraNotes | 8 | 8 | 8 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 550/825/1240 × AP
- `HealthCalc1` = 0
- `ShieldCalc1` = 0
- `MagicDamageCalc2` = 20/30/45 × AP
- `MagicDamageCalc3` = 45/68/100 × AP
- `GenericCalc1` = 8

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Seraphine19_Attack`: launch 0.2682 s (8.05 ticks); animation length 1.6333 s (49 ticks); release at base AS 0.2682 s (8.05 ticks)
- Attack projectile: DA_Seraphine19_AutoAttackProjectile, speed 1300 units/s
- Spell `GA_Seraphine19_Spell` (chrono `CD_Seraphine19_CastAnim`): cast ends 2.7 s (81 ticks), next attack can start 2.7333 s (82 ticks), mana lock removed 2.7 s (81 ticks); ended by `FinishCasting via OnEventBegin:CD_Seraphine19_CastAnim:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Seraphine19_Attack` | Chrono | 1.6333 | LaunchAttack 0.2682, Unlock 0.6533 |
| `CD_Seraphine19_CastAnim` | Chrono | 2.7156 | Default 0, HighNote 0.269, BeginFire 0.2997, Pose1 0.8986, SecondFire 1.1739, Pose2 1.7956, ThirdFire 2.0487, Unlock 2.6974 |
| `CD_Seraphine19_Celebration` | Chrono | 11.4 | Default 0, Loop 0.3297 |
| `CD_Seraphine19_RisingStarCeremony` | Chrono | 5.3313 | Transform 0.5815, Loot 0.6219 |
| `CD_Seraphine19_SuperstarCeremony` | Chrono | 5.0259 | Transform 0.1964, Loot 0.9112 |
| `CD_Seraphine19_CatGrantLoot` | UniqueTraits | 4.186 | BeginSpawn 2.7984, Loot 2.9578 |
| `CD_Seraphine19_GrantLoot` | UniqueTraits | 3.4034 | BeginSpawn 0.8866, Loot 0.9886 |
| `CD_Seraphine19_SpawnOnBench` | UniqueTraits | 2.0011 | AllowStarUp 1.2366 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Seraphine19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Seraphine19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Seraphine19_Spell.txt

### Changed since `rls-19.1.0.5995286.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Seraphine`, `SeraphineRisingStar`, `SeraphineSuperstar`;
  D1); the mana lock checked on VOD6 (E2); the per-note damage / 30 (owner, D2)
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has her at 1-6 and 2-4). Her three forms are three
  champions on the page (same stats; the spell reads the form)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (HP 775 = 700 + Heartsteel's Sett 75; mana 50, 2/s, range 4) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster: 7 per attack, 2/s | confirmed (+7 steps, +1 every 0.5 s) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2682 s (8.05 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1300 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 2.7333 s (82 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2.7 s (81 ticks) | confirmed: the banked 2 shows 82 ticks after the bar empties (81 + the tick after the fill) | E2 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 (no GE_SimulateLaunchAttack) | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | 30 notes at the target; Rising Star 2 x 4 bonus notes; Superstar a high note at every enemy | predicted | D1 |
| Q14 | Passives and other mechanics that need modelling | the forms (Indie / Rising Star / Superstar, from rerolls) | three champions on the page | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |
| Q16 | Each stream note's damage: MagicDamageCalc1 with DivideAdditive NumFires (15) and 2 | the engine's channel rule (I5, GAS): / (1 + 14 + 1) = / 16, so 30 notes = 1.875 x the tooltip's total; the tooltip implies / 30 | **owner, 2026-11-18**: / 30 (D2): VOD6's 12s are single notes, the 25s two shown merged. At AP 120% a note is 22.8 before MR, so 12 implies ~90 MR on the target (not inspected) | E3, D2 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18, 60 fps; client rls-19.1.0.5986652, not exported: the simulator's newest is 5986094). Round 1-6:
Seraphine 1 star, Indie, two items; Heartsteel (3) on the board (Sett fielded). Mana from
`tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 4:24.6 (round 1-6) | 60 | inspection panel | 775/775, x/50, 2/s, range 4 hex, Back, Magic Caster; AD 30, AP 20%, armor 38, MR 38, AS 1.43, crit 35% | HP 700 + 75 (Sett), AD, mana, regen, range match; AP, AS, crit, armor and MR carry items and traits not identified | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f15542-16518 | 60 | mana text | +7 steps and +1 every 30 frames; casts f15819 (45 + 7 = 52), f16168, f16518; after f15819 the banked 2 shows at f15983 (+164 frames = 82 ticks) | mana lock 81 + the tick after the fill; the cast at f16518 was cut by the round's end | Q2, Q9 |
| E3 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 4:23.9-4:26.4 (the target every 1/15 s) | 60 | magic damage numbers on her target during the cast | 25 and 12, alternating, about every 0.08 s | see Q16; the target's MR is not known, and the 12s may be another unit's | Q16 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Seraphine` and its two form subclasses):
  - **Forms:** DA_SeraphineIndie19 (in the shop), _RisingStar19, _Superstar19: the same stats and rows; the spell
    reads the unit's data asset (SeraphineFormIndex 1 / 2 / 3, 0x3e8c). The page lists each.
  - **Cast (GA_Seraphine19_Spell):** commit, mana lock (0x4449), CD_Seraphine19_CastAnim at her target. NumFires =
    Round(SpellDuration / SpellTickRate + 1) = 15 (defaults 2.1 s, 0.15 s).
  - **Stream:** 'BeginFire' (0.2997 s): RepeatAction(0.15, 15), first at once (A1); each fire: a left-speaker note
    and, 0.075 s later, a right-speaker note (CD_Seraphine19_Splines 'SpellMis', 1900 units/s) at her target.
    GE_Seraphine19_Damage: MagicDamageCalc1 (DamageAP x AP), DivideAdditive SetByCaller (NumFires) and DivideAdditive
    2; magic, on-spell, RollIfCanSpellCrit. Divisor (I5): 1 + (15 - 1) + (2 - 1) = 16 (Q16; replaced by D2).
  - **Rising Star / Superstar:** 'SecondFire' (1.1739 s): FireBonusNotes(8 - Round(8 / 2) = 4); 'ThirdFire' (2.0487
    s): FireBonusNotes(Round(8 / 2) = 4). The notes go in turn to the N nearest enemies (TR_Add_N_NearestEnemies...,
    SortByRowDistance; her target if none; GetRepeatingListFromTargetData), CD_Seraphine19_SplinesBonus (1900),
    GE_Seraphine19_DamageBonusNote = MagicDamageCalc2 (ExtraNoteDamageAP x AP).
  - **Superstar:** 'HighNote' (0.269 s): CD_Seraphine19_HighNoteMis ('HighNote', 1800, arc 500) at every enemy,
    GE_Seraphine19_DamageHighNote = MagicDamageCalc3 (HighNoteDamageAP x AP).
  - **End:** 'Unlock' (2.6974 s) ends the cast (81 / 82 ticks).
  - **Simulated:** flights over the target's distance (G4; the speakers' places and the splines' curves not
    modelled); the Indie trait itself (rerolls, popularity, loot) gives no combat power.

- 2026-11-18, D2 (owner): each stream note deals DamageAP x AP / (NumFires x 2) = / 30, so a cast's 30 notes deal
  the tooltip's total. The owner reads VOD6's numbers as 12 per note, with the left and right notes (0.075 s apart)
  merged into one 25. The two DivideAdditive SetByCallers are taken as a product here, not GAS's 1 + sum(d - 1)
  (ledger I5's note).
