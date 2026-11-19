# Jinx (4-cost AttackMarksman) · `DA_Jinx19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5995286.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5995286.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Ionic Spark, Hitmaker
- **HP** 850 / 1530 / 2754 · **AD** 55 / 83.25 / 124.875 · **AS** 0.8 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 30 / 90
- **Unlock**: 3 items on an Ionic Spark or Hitmaker Champion.

### Ability: Boom Boom POW POW

> Rapidly fire ⟨computed in game: MMC_Jinx19_AttackSpeedScaling⟩ missiles at nearby enemies, each dealing 43/65/300 × AD + 6/9/30 × AP physical damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 55 | 83.25 | 124.875 |
| BaseMissiles | 16 | 16 | 16 |
| DamagePerMissileAP | 6 | 9 | 30 |
| DamagePerMissileAD | 43 | 65 | 300 |
| PercentMissilesOnCurrentTarget | 0.75 | 0.75 | 0.75 |
| NumMissilesPerSimulatedAuto | 5 | 5 | 5 |
| BonusASPerBonusMissile | 0.35 | 0.35 | 0.35 |
| PercentMissilesOnNHexWithinTarget | 0.15 | 0.15 | 0.15 |
| PercentMissilesEveryoneElse | 0.1 | 0.1 | 0.1 |
| NHex | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 43/65/300 × AD + 6/9/30 × AP
- `GenericCalc2` = 1 × AS
- `AttackSpeedCalc1` = ⟨computed in game: MMC_Jinx19_AttackSpeedScaling⟩

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Jinx19_Attack`: launch 0.2402 s (7.21 ticks); animation length 1.5333 s (46 ticks); release at base AS 0.2402 s (7.21 ticks)
- Attack projectile: DA_Jinx19_AutoAttackProjectile, speed 2750 units/s
- Spell `GA_Jinx19_Spell` (chrono `CD_Jinx19_Spell_FixedTime`): cast ends 2.2333 s (67 ticks), next attack can start 2.2667 s (68 ticks), mana lock removed 2.2333 s (67 ticks); ended by `FinishCasting via OnEventBegin:CD_Jinx19_Spell_FixedTime:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Jinx19_Attack` | Chronos | 1.5333 | LaunchAttack 0.2402, Unlock 0.6133 |
| `CD_Jinx19_Spell_FixedTime` | Chronos | 2.2436 | BeginFiring 0.5604, EndFiring 1.7799, Unlock 2.2235 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Jinx19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Jinx19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Jinx19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Jinx19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Jinx19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Jinx19_Spell.txt

### Changed since `rls-19.1.0.5986094.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Jinx`, D1); the missile count rule and the damage from
  VOD6's tooltip (E1), the cast rhythm consistent (E2)
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has her at 2-7)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | mana 30 / 90, range 4 confirmed; HP 1025 vs 850 (items / traits not identified) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackMarksman: 10 per attack, no regen | confirmed (+10 steps) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2402 s (7.21 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2750 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 2.2667 s (68 ticks) | consistent: the next attack's mana 73-76 ticks after each cast (68 + release + the tick after the fill) | E2 |
| Q8 | Does the cast time scale with attack speed? | no (chrono speed 1; the missile count does) | predicted (script) | D1 |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2.2333 s (67 ticks) | predicted (no regen to show it) | |
| Q10 | Does the mana lock scale with attack speed? | no | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 1 GE_SimulateLaunchAttack per 5 missiles | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | Round(16 + bonus AS / 35%) missiles of DamagePerMissileAD x AD + DamagePerMissileAP x AP | confirmed by the tooltip: 17 at +30% AS (pro rata, rounded), 68 = 43 x 1.42 + 6 x 1.2 | E1 |
| Q14 | Passives and other mechanics that need modelling | none | not applicable | |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18, 60 fps; client rls-19.1.0.5986652, not exported: the simulator's newest is 5986094). Round 2-7:
Jinx with three items. Mana from `tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 16:40.4 (round 2-7, planning) | 60 | inspection panel; ability tooltip | 1025/1025, 30/90, range 4, Back, Attack Marksman; AD 78, AD 42%, AP 20%, AS 1.04, crit 25%; tooltip "Rapidly fire 17 missiles ... each dealing 68"; "Number of Missiles: 17 = 16 + 1 per 35% bonus" | AS 1.04 / 0.8 = +30%: 16 + 0.30 / 0.35 = 16.86 -> 17 (pro rata, then Round, as the script's Round(AttackSpeedCalc1)); 43 x 1.42 + 6 x 1.2 = 68.3 | Q1, Q13 |
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f60139-61692 | 60 | mana text | +10 steps; casts f60390, f60783, f61105, f61424, f61692; the next +10 at f60542, f60931, f61252, f61570 (+152, +148, +147, +146 frames) | 73-76 ticks: the 68-tick cast lock, the release (~5 ticks at her AS) and the tick after the fill | Q2, Q7 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Jinx`):
  - **Cast (GA_Jinx19_Spell):** mana lock (0x18c6); CD_Jinx19_Spell_FixedTime (speed 1). NumMissilesToFire =
    Round(AttackSpeedCalc1) (MMC_Jinx19_AttackSpeedScaling, native: BaseMissiles + bonus AS /
    BonusASPerBonusMissile, E1). The missiles are dealt out as Round(N x 0.75) 'AATarget', Round(N x 0.15)
    'NHexRange' (an enemy within NHex 2 of the target), Round(N x 0.1) 'Other', padded with 'AATarget', cut to N,
    shuffled.
  - **Firing:** 'BeginFiring' (0.5604 s): RepeatAction(FireOverTime 1.2 / (N - 1), N), first at once; 'Rocket'
    (2400 units/s); arrival: GE_Jinx19_RocketDamage = PhysicalDamageCalc1, physical, on-spell, RollIfCanSpellCrit.
    Every 5 missiles: GE_SimulateLaunchAttack. 'Unlock' (2.2235 s) ends the cast (67 / 68 ticks).
  - **Simulated:** the shuffle as an even interleave; NHexRange missiles spread over the enemies within 2 hexes of
    the target (the target if none); Other over the rest (else those near the target, else the target).
