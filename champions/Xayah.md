# Xayah (4-cost AttackCaster) · `DA_Xayah19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6018196.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6018196.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Gu Feng, Hitmaker
- **HP** 850 / 1530 / 2754 · **AD** 55 / 82.5 / 123.75 · **AS** 0.8 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 0 / 60

### Ability: Feathers Flying Like Leaves on the Wind

> Summon 30/30/60 feathers that strike the target, each dealing 22/33/150 × AD + 3/5/16 × AP physical damage and reducing Armor by 1.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 55 | 82.5 | 123.75 |
| FeatherDamage | 22 | 33 | 150 |
| RetractionDamage | 0 | 0 | 0 |
| ArmorReduction | 1 | 1 | 1 |
| NumFeathers | 30 | 30 | 60 |
| TankBonusDamage | 0 | 0 | 0 |
| FeatherDamageAP | 3 | 5 | 16 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 22/33/150 × AD + 3/5/16 × AP
- `PhysicalDamageCalc2` = 0 × AD
- `PhysicalDamageCalc3` = 0 × PhysicalDamageCalc2
- `GenericCalc1` = 1 ÷ 1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Xayah19_Attack`: launch 0.22 s (6.6 ticks), variants 0.22, 0.4; animation length 2.4667 s (74 ticks); release at base AS 0.22 s (6.6 ticks)
- Attack projectile: DA_Xayah19_AutoAttackProjectile, speed 2500 units/s
- Spell `GA_Xayah19_Spell` (chrono `CD_Xayah19_CastAnim`): cast ends 2.1333 s (64 ticks), next attack can start 2.1667 s (65 ticks), mana lock removed 2.1333 s (64 ticks); ended by `FinishCasting via OnEventBegin:CD_Xayah19_CastAnim:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Xayah19_Attack` | Chronos | 1.3004 | LaunchAttackVariant1 0.22, LaunchAttackVariant2 0.4, Unlock 0.6, Unlock 0.65 |
| `CD_Xayah19_CastAnim` | Chronos | 2.1334 | StartFeathers 0.2466, MoreFeathers 0.6989, FinishLaunching 1.3031, Unlock 2.1237 |
| `CD_Xayah19_RetractAnim` | Chronos/OLD | 0.6998 | RecallFeathers 0.3663, Unlock 0.6771 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Xayah19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Xayah19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Xayah19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Xayah19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Xayah19_Spell.txt

### Changed since `rls-19.1.0.6011486.Set19.Shipping.pbe`

- stat AttackSpeed: 0.75 -> 0.8

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Xayah`, D1); the cast's locks and the next attack
  checked on VOD4 (E3-E5) and again on VOD6 (E7), the damage formula on its tooltip (E2)
- Keep in the simulator: **yes** (owner, 2026-11-18: "we have a vod for xayah")

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (with items and traits; the AD with Illbeats, owner) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster: 7 per attack, 2/s | confirmed (+7 steps, +1 every 0.5 s) | E3 |
| Q3 | First attack at combat start: when does it land? | G3 | open (VOD4's targets walk in) | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.22 s (6.6 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2500 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 2.1667 s (65 ticks) | confirmed to a tick: the attack after the cast pays at +71.5 / +72.5 / +70 ticks (engine 72); VOD6 +72.5 | E3-E5, E7 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2.1333 s (64 ticks) | confirmed to a tick: the banked overflow shows +64.5 / +65.5 ticks after the bar emptied; VOD6 +65.5 / +65 | E3, E4, E7 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 1 GE_SimulateLaunchAttack at StartFeathers (G11) | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | 30/30/60 feathers on the target, each FeatherDamage x AD + FeatherDamageAP x AP | formula confirmed (tooltip 38 = 20 x 1.72 + 3 x 1.10); hit count predicted | E2, D1 |
| Q14 | Passives and other mechanics that need modelling | -1 flat Armor per feather; pass-through feathers | Armor: not modelled (flat armor reduction, owner policy); pass-through: PhysicalDamageCalc2 = 0 | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |
| Q16 | When the feathers land | 1.37-1.77 s into the cast at 4 hexes (engine 42-53 ticks) | consistent, not frame-exact (the VOD target was farther than 4 hexes) | E6 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD4 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-17-2026_16-22-12-687/` `…PBE_11-17-2026_19-0-51-650.mp4` (owner's
clip, 2026-11-17, build rls-19.1.0.5973071; Xayah's data is the same in 5986094). Xayah 1 star with Infinity Edge,
Quicksilver and Guinsoo's Rageblade (owner); Hitmaker (2) with her as the Big Shot; Illbeats (2) on the board (she isn't a member); Gu Feng 1/2 (inactive). Mana
from `tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5973071 | VOD4 19:16-19:26 (round 1-10, planning) | 60 | inspection panel | 850/850, 0/60, 2/s, range 4 hex, Back; AD 95, bonus AD 72%, AP 10%, armor 40, MR 60, AS 0.94, crit 80% | the simulator: 850, 0/60, AP 110%, AS 0.938, crit 80%, armor 40, MR 60; AD 91.85 (bonus 67%: Hitmaker 12 + 20, IE 35). The other 5%: Illbeats (2) on the board (owner, 2026-11-18); she isn't a member, so half the mix: 3 AD decibels = (3.5 + 3.5 + 3.2)% x 0.5 = 5.1% -> 172.1%, 94.7 AD; AP unchanged, so no AP decibels. Matches | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5973071 | VOD4 19:19 (ability tooltip) | 60 | damage per feather | 38 | 20 x 1.72 + 3 x 1.10 = 37.7: AD and AP are the multipliers (the panel's 172%, 110%) | Q13 |
| E3 | 2026-11-18 | rls-19.1.0.5973071 | VOD4 f70941-71084 (round 1-10, first cast) | 60 | bar empties (56 + 7 = 63); banked 3 shows; next +7 | f70941; f71070 (+129 fr = 64.5 ticks); f71084 (+143 fr = 71.5 ticks) | mana lock 64, plus up to a tick if the cast starts the tick after the fill; the attack after the cast at 65 + windup (engine 72) | Q2, Q7, Q9 |
| E4 | 2026-11-18 | rls-19.1.0.5973071 | VOD4 f73741-73886 (round 2-1, cast A) | 60 | as E3 (55 + 7 = 62) | banked 2 at f73872 (+131 fr = 65.5 ticks); next +7 at f73886 (+145 fr = 72.5 ticks) | as E3 | Q7, Q9 |
| E5 | 2026-11-18 | rls-19.1.0.5973071 | VOD4 f74137-74277 (round 2-1, cast B) | 60 | as E3 (53 + 7 = 60, nothing banked) | next +7 at f74277 (+140 fr = 70 ticks) | as E3 | Q7 |
| E6 | 2026-11-18 | rls-19.1.0.5973071 | VOD4 f73735-73887 (cast A, the board every 8 frames) | 60 | feathers | gather behind her ~1.0-1.4 s, fly ~1.5 s, damage numbers on the target ~1.6-1.9 s | consistent with D1's 0.88 / 0.4 s waits and 3200 units/s over more than 4 hexes | Q16 |
| E7 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f55930-56672 (round 2-6; VOD6 = `…PBE_11-18-2026_18-40-41-766.mp4`, 60 fps) | 60 | mana text (attacks +12 / +13, 3/s; she takes damage) | cast at f55958 (58 -> 0): the next attack's +12 at f56103 (+145 fr = 72.5 ticks); cast at f56307 (59 -> 0): banked 12 at f56438 (+131 fr = 65.5 ticks); cast at f56534 (52 -> 0): banked 4 at f56664 (+130 fr = 65 ticks) | the mana lock 64 + the tick after the fill, the attack after the cast at 72: as on VOD4 (the first cast banked nothing: filled by regen, not seen) | Q7, Q9 |

Not used: fight 1's second cast (f71290: the lock end shows 157 frames later, so the cast started ~28 frames after
the fill; her target had died) and the casts cut short by the end of the round (f71682, f74569).

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Xayah`):
  - **Cast (GA_Xayah19_Spell):** mana lock (0x1df9); CD_Xayah19_CastAnim. NumFeathers from the curve row; spawn
    delay 0.8 / NumFeathers (0x1d83). 'StartFeathers' (0.2466 s): one GE_SimulateLaunchAttack (0x2ba1) and wave 1,
    RepeatAction(spawn delay, NumFeathers / 2) (0x2caa; first action at once, A1). 'MoreFeathers' (0.6989 s): wave 2
    (0xfe). 'Unlock' (2.1237 s) ends the mana lock and the cast (build: 64 / 65 ticks; E3-E5).
  - **Feathers:** each plays CD_Xayah19_SpellMis from its place in a fan behind her
    (ComputeFeatherStartLocations: 90 + i x 200 / 15 degrees from her facing; 100 units out for wave 1, 250 for
    wave 2; wave 2 in reverse order) to her attack target. The chrono's first active group picks the missile:
    wave 1 (no tag) waits 0.88 s, wave 2 (MissileSelector.1) 0.4 s, then 3200 units/s (TFTFixedSpeedMovement).
    The waits are the projectile modules' Delay, build data since 2026-11-18 (ledger B36; typed in before).
    Flight = straight line from the feather's place to the target (G4).
  - **Damage:** on reaching the target, GE_Xayah19_InitialDamage = PhysicalDamageCalc1 = FeatherDamage x AD +
    FeatherDamageAP x AP (E2): physical, on-spell, Damage.CritCondition.RollIfCanSpellCrit (crits with Precision,
    e.g. Infinity Edge). The feather then flies 300 / 400 units on behind the target (MissileSelector.2) and hits
    whoever it crosses with GE_Xayah19_SecondaryDamage (Tanks: _SecondaryDamageTank) = PhysicalDamageCalc2 / 3 =
    RetractionDamage x AD = 0: nothing (both effects sit in an OLD folder).
  - **Not modelled:** GE_Xayah19_ArmorReduction (Armor - ArmorReduction, flat, until combat ends; one per feather).
    Flat armor reduction is not modelled (owner policy), so later feathers do a little less than in game.
  - **Gu Feng** (owner, 2026-11-18: realistically only the (2) is relevant): ledger B35.
