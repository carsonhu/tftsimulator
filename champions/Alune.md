# Alune (4-cost MagicCaster) · `DA_Alune19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Heartsteel, Manager, Prodigy
- **HP** 800 / 1440 / 2592 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 20 / 65
- **Unlock**: 4 unique Heartsteel or Prodigy champions.

### Ability: Spotlight

> Call down a spotlight on the target, dealing 315/475/2250 × AP magic damage. All enemies within 2 hexes of them split 340/510/2500 × AP magic damage. If the target dies, split excess damage between the 2 nearest enemies.
> 
> Heartsteel Upgrade: Fire 5 blasts at target that deal 30/45/72 × AP30/45/72 × AP magic damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| Damage | 315 | 475 | 2250 |
| HexRadius | 2 | 2 | 2 |
| MinimumDamage | 0.2 | 0.2 | 0.2 |
| HeartsteelStan_NumMissiles | 5 | 5 | 5 |
| HeartsteelStan_APDamage | 30 | 45 | 72 |
| AOESplitDamage | 340 | 510 | 2500 |
| OverkillNumTargets | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 315/475/2250 × AP
- `MagicDamageCalc2` = 30/45/72 × AP
- `MagicDamageCalc3` = 340/510/2500 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Alune19_Attack`: launch 0.3667 s (11 ticks); animation length 1.6667 s (50 ticks); release at base AS 0.3667 s (11 ticks)
- Attack projectile: DA_Alune19_AutoAttackProjectile, speed 1750 units/s
- Spell `GA_Alune19_Spell` (chrono `CD_Alune19_CastAnim`): cast ends 1.3 s (39 ticks), next attack can start 1.3333 s (40 ticks), mana lock removed 1.3 s (39 ticks); ended by `FinishCasting via OnEventBegin:CD_Alune19_CastAnim:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Alune19_Attack` | Chronos | 1.3004 | LaunchAttack 0.3667, Unlock 0.6667 |
| `CD_Alune19_CastAnim` | Chronos/Spell | 1.3068 | FireHeartsteelMissiles 0.9616, Damage 1.0606, Unlock 1.2952 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Alune19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Alune19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Alune19_Spell.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-20, `set19champs.Alune`, D1); mana, mana lock and cast lock checked on VOD7
- Keep in the simulator: **yes** (owner, 2026-11-20: her panel shows up a lot in VOD7)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed: 800 HP, 20 / 65 mana, AS 0.75, armor/MR 63 (Bodyguard 2) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster | confirmed: +7 per attack every 40 ticks; regen 8/s at Prodigy (4) (2 + 5 + 1), 9/s at (5) (2 + 6 + 1); Nashor's +2 per attack and +2 per critical attack on landing | E1-E5 |
| Q3 | First attack at combat start: when does it land? | G3 | open: both VOD7 fights put the first attack's mana 6-7.5 ticks after the first regen step (39 frames after the HUD's combat bar starts); the engine 3 ticks (regen phase T7 / G17) | E2, E3 |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3667 s (11 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | consistent at AS 0.83: the cast-to-attack gap stays 52 ticks (engine 52) | E5 |
| Q6 | Projectile travel time (ranged only) | speed 1750 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.3333 s (40 ticks) | confirmed: the next attack's mana 104-105 frames (52 ticks) after every fill, attack- or regen-filled (engine 52: cast at fill + 1, lock 40, windup 11) | E2-E5 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.3 s (39 ticks) | confirmed: banked overflow (1, 3, 6) shown 80-81 frames after the filling mana = 39 + T4 | E2-E5 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script + GEs, D1): target Calc3 / (N + 1) + Calc1, each other enemy within 2 hexes Calc3 / (N + 1) | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | Heartsteel Bias blasts modelled; overkill not (dummies never die) | D1 |
| Q15 | Can this unit be simulated realistically? | | yes | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD7 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-20-2026_21-47-56-118/`
`…PBE_11-20-2026_22-23-46-350.mp4` (owner's full PBE game, 1280x720, 60 fps, client rls-19.1.0.6011486). Alune 1★,
no items. Mana from `tools/vod_text_changes.py --field mana` (crops read by eye); HUD phases from
tftVision/runs/s19_vod7/phases.json.

| # | Date | Build | Source (VOD time / frames) | fps | Measured | Frames / values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-20 | rls-19.1.0.6011486 | VOD7 13:31 (f48700, round 3-3) | 60 | inspection panel | 800/800, 52/65, 8/s; AD 30, AP 10%, armor/MR 63, AS 0.75; Heartsteel 3, Prodigy 4, Bodyguard 2 on the board | as built (AP 10% from the board, not identified) | Q1, Q2 |
| E2 | 2026-11-20 | rls-19.1.0.6011486 | VOD7 f48572-50598 (3-3; HUD combat bar from f48545) | 60 | mana text | regen +2 every 15 frames; attacks +7 at f48584, 48664, 48744, 48848, 48929, 49009, 49089, 49201, ... (80 frames apart); casts f48744 (58 + 7, exact), f49097 (64 + 2: overflow 1 shown f49177, +80), f49442 (56 + 7 + 2, exact), f49802 (overflow 1 at f49883, +81), f50147, f50508 (overflow 1 at f50588, +80); next attack's mana after each fill +104 / +104 / +104 / +105 / +104 frames | mana lock 39 + T4 = 40 ticks after the fill; next attack 52 ticks after the fill (lock 40 + windup 11 + 1) | Q2, Q3, Q7, Q9 |
| E3 | 2026-11-20 | rls-19.1.0.6011486 | VOD7 f55226-56442 (3-5, 9/s; HUD combat bar from f55266) | 60 | mana text | panel 20/65 before combat; first regen f55290, first attack f55305; casts f55466 (61 + 7: overflow 3 at f55546, +80), f55810 (64 + 7: overflow 6 at f55891, +81), f56133 (regen fill); next attack's mana after each fill +104, +105, +104 | as E2 at 9/s | Q2, Q3, Q7, Q9 |
| E4 | 2026-11-20 | rls-19.1.0.6011486 | VOD7 f59982-61202 (3-6, 9/s; HUD combat bar from f59953) | 60 | mana text | casts f60162 (overflow 5 at f60242, +80), f60506 (64 + 7: overflow 6 at f60587, +81), f60827 (regen fill), f61202; next attack's mana +104, +104, +104 frames after the fill; one gap of 138 frames between attacks (f60931-61069: a new target) | as E2 | Q2, Q7, Q9 |
| E5 | 2026-11-20 | rls-19.1.0.6011486 | VOD7 f66849-68600 (4-1; panel at f66900) | 60 | panel, mana and AS text | items Nashor's Tooth + 2 Jeweled Gauntlet (icons matched 0.88 / 0.97 / 0.92); 950 HP, AP 95%, crit 100%, AS 0.83 all fight (no AS change on cast), 9/s. Attacks +9 every 72-76 frames; +2 off the regen grid after an attack (f67021 release -> f67054, 16.5 ticks); a cycle (f67357 -> 67431, 67431 -> 67503) gains 22-23 mana = 9 + 2 + 10.8 regen. Next attack's mana after the fill +104 (f66917), +104 (f67253), +105 (f67532). At f67202-67253 the bar stood full (65/65) 25 ticks before the cast (she had just taken a hit: 950 -> 817) | AS 0.75 x 1.1, Nashor's ManaPerAttack 2 with the role mana at release and +2 when a critical attack lands (I6; engine: 15 ticks for 4 hexes); 52 ticks after the fill at AS 0.83 as at 0.75 (engine 52). The 25-tick wait: open | Q2, Q5, Q7, Q12 |

## Decisions and notes

- **D1 (2026-11-20, `set19champs.Alune`):** from GA_Alune19_Spell and its GEs (FModel export of 6011486). The cast
  applies the mana lock and plays CD_Alune19_CastAnim at her attack target. 'Damage' (1.0606 s): the enemies within
  HexRadius (2) of the target, the target left out (N), split = 1 / (N + 1); GE_Alune19_AOESecondaryTargetDamage =
  MagicDamageCalc3 x split on each of them, GE_Alune19_TargetDamage = MagicDamageCalc3 x split + MagicDamageCalc1 on
  the target (terms in order, I5; the tooltip's reading). MinimumDamage is read but unused. 'Unlock' (1.2952 s) ends
  the cast. Heartsteel Bias: 'FireHeartsteelMissiles' (0.9616 s) fires HeartsteelStan_NumMissiles blasts 0.04 s
  apart at her target (MagicDamageCalc2 each). Overkill (excess damage to the 2 nearest when the target dies) is not
  simulated: dummies never die.

