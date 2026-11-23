# Malzahar (3-cost MagicCaster) · `DA_Malzahar19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6018196.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6018196.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 3, pool 18; traits: Composer, Prodigy
- **HP** 800 / 1440 / 2592 · **AD** 35 / 52.5 / 78.75 · **AS** 0.8 · **Range** 4 · **Armor** 35 · **MR** 35 · **Mana** 0 / 50

### Ability: Forbidden Cacophony

> Fire a beam at the target for 2 seconds, dealing 260/390/625 × AP magic damage. The energy rhythmically explodes 4 times, 30% Shredding enemies in a 1 hex area for 4 seconds, and dealing 36/54/86 × AP magic damage each time.
> 
> Shred: reduce Magic Resist

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 35 | 52.5 | 78.75 |
| SecondaryDamageAP | 36 | 54 | 86 |
| DamageOverSecondsDONTCHANGE | 2 | 2 | 2 |
| ShredPercent | 30 | 30 | 30 |
| ShredDuration | 4 | 4 | 4 |
| UniqueTrait_GLP_NumShops | 10 | 10 | 10 |
| UniqueTrait_GLP_NumInstruments | 2 | 2 | 2 |
| UniqueTrait_DamageDealt_TOOLTIPONLYEDITUNLOCKCONDITION | 60000 | 60000 | 60000 |
| DamageAP | 260 | 390 | 625 |
| PrimaryTickRate | 0.25 | 0.25 | 0.25 |
| AOEHexRange | 1 | 1 | 1 |
| UniqueTrait_APPerInstrument | 0.03 | 0.03 | 0.03 |
| UniqueTrait_MalzaharBonusAPPercent | 1 | 1 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 260/390/625 × AP
- `MagicDamageCalc2` = 36/54/86 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Malzahar19_Attack`: launch 0.445 s (13.35 ticks); animation length 1 s (30 ticks); release at base AS 0.5563 s (16.69 ticks)
- Attack projectile: DA_Malzahar19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Malzahar19_SpellNew` (chrono `CD_Malzahar19_CastAnim_new`): cast ends 2.5 s (75 ticks), next attack can start 2.5333 s (76 ticks), mana lock removed 2.5 s (75 ticks); ended by `FinishCasting via OnEventBegin:CD_Malzahar19_CastAnim_new:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Malzahar19_Attack` | Chronos | 1 | LaunchAttack 0.445, Unlock 0.925 |
| `CD_Malzahar19_CastAnim_new` | Chronos | 2.5007 | BeginBeam 0.3523, Burst 0.9923, Burst 1.6323, Burst 2.2723, Unlock 2.4688 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Malzahar19_SpellNew`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Malzahar19_SpellNew.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Malzahar19_SpellNew.txt

### Changed since `rls-19.1.0.6011486.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Malzahar`, D1); mana and mana lock checked against VOD3; cast lock against VOD5
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed with his items (1★) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster | confirmed: 7 per attack and 2/s (+5 / +1 Shojin) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.445 s (13.35 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 2.5333 s (76 ticks) | confirmed: VOD5's next attack paid 90.5 ticks after the filling attack, engine 91 (1 + 76 + windup) | E3, E5, E6 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2.5 s (75 ticks) | consistent: overflow shown 75.5 ticks after the filling attack (VOD3, VOD5), mana again 75 ticks after a regen-filled cast (VOD5) | E3, E5, E6 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | predicted: 0 (no GE_SimulateLaunchAttack in GA_Malzahar19_SpellNew) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read: D1); no damage number read yet | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | the shred (D1); Composer (B26) and Prodigy (B24) implemented | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD3 (`…PBE_11-17-2026_17-13-37-283.mp4`, 60 fps), the owner's PBE recording, build
`rls-19.1.0.5973071`; Malzahar 1★, round 1-7, panel open f24365-24895.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 6:51 (owner's screenshot) | 60 | inspection panel | 950/950, 0/50, 3/s; AD 53 (+50%), AP 15%, AS 0.88, crit 80%, armor/MR 35; Striker's Flail, Infinity Edge, Spear of Shojin | 800 + 150 HP, 0.8 x 1.1 AS, crit 25 + 35 + 20, AD +35 +15%, AP +15%, regen 2 + 1: as built | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 f24365-24595 (`tools/vod_text_changes.py`, mana) | 60 | mana text | 0, 1, 13, 14, 15, 16, 28, 29, 30, 31, 32, 44, 45, 46, 47, cast: regen 0.75 a step, attacks +12, 34 ticks apart (f24391, 24459, 24527, 24595) | the floor of 0.75k + 12n; period 1 / 0.88 = 34.1 ticks | Q2 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 f24595-24869 (mana text; board every 16 frames) | 60 | the cast | overflow 9 shown at f24746 (+151 frames), then 10, 11, 12, 13, 25 (attack at f24833, +119 ticks); the first target died mid-beam (the beam moved to a far enemy) and he walked after the cast | mana lock 75 ticks + T4: lifted 76 after the filling attack, shown at 75.5; the attack after the cast includes a walk, so the cast lock is unmeasured | Q7, Q9 |

VOD5 rows: `…PBE_11-18-2026_0-57-11-500.mp4` (session folder 0-33-59-673), 60 fps, the owner's PBE recording in the
score mode, build `rls-19.1.0.5973071` (no newer snapshot before the recording); Malzahar 1★, round 1-6, panel open
f21000-22000. Ticks below count from combat start, f21295 (Quicksilver's first +3% at f21355 is 1 s after it).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E4 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 5:53 | 60 | inspection panel | 800/800, 0/50, 8/s; AD 40, AS 0.92, crit 45%, armor 50, MR 70; Blue Buff, Quicksilver; Composer 1/1, Bodyguard (2) from the board | 0.8 x 1.15 AS, 25 + 20 crit, 2 + 6 regen: as built | Q1 |
| E5 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 f21316-21998 (`tools/vod_text_changes.py`, mana and as) | 60 | mana text, AS | 12 (tick 10.5), 14, 21, 23, 25, 27, 29, 36, 38, 40, 42, 44, cast (tick 80); 1 (155.5), 3, 5, 12 (170.5), ... 48, cast (253.5, filled by regen); 2 (328.5), 4, 11 (342.5). Regen +2 every 7.5 ticks at 14, 21.5, 29, ...; attacks +7 at 16, 48, 80, 170.5, 199.5, 226.5, 342.5; AS +0.024 every 60 frames from f21355 | engine (Blue Buff, Quicksilver): attacks 15, 48, 79, 170, 199, 227; mana lock and cast lock as built. The engine pays a regen step at tick 0 (T7) that the clip doesn't show (first step ~6.5 ticks after the start, G17), so it has 2 mana more at each fill and its regen-filled second cast comes at 249, the clip's at 253.5 | Q2, Q7, Q9 |

VOD7 rows: `…PBE_11-20-2026_22-23-46-350.mp4` (session folder 21-47-56-118), 60 fps, the owner's full PBE game on client
rls-19.1.0.6011486 (not exported; Malzahar's data unchanged 5973071-6005555); Malzahar 1★, round 2-1, no items, Prodigy (3).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E6 | 2026-11-20 | rls-19.1.0.6011486 | VOD7 f11796-12509 (3:16-3:28; panel at f11900) | 60 | mana text, panel | 800/800, 0/50, 6/s (2 + Prodigy 3 + 1), AS 0.80; cast f11797 filled by an attack (46 + 7: overflow 3 shown f11948, +151 frames); attacks +7 at f11984, 12060, 12134, 12407, 12483 (74-76 frames apart); second cast f12194 filled by regen (first mana f12358) | mana lock: +151 frames = 75.5 ticks, as VOD3 and VOD5. Engine (Prodigy (3), no items): attacks 37-38 ticks apart (clip 38), next attack 94 ticks after the filling attack (clip 93.5); regen-filled lock end bounded (12344, 12358], engine 75 | Q2, Q7, Q9 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Malzahar`):
  - **Spell (GA_Malzahar19_SpellNew):** mana lock at activation; CD_Malzahar19_CastAnim_new at his attack target.
    BeginBeam (0.3523 s): a burst, and the beam: RepeatAction(PrimaryTickRate 0.25, 9), first tick at once, each
    MagicDamageCalc1 / 9 (SetByCaller NumTicks) to the target, magic, DOT. Burst (0.9923, 1.6323, 2.2723 s): 4 bursts
    in all, each GE_MRShred (30%, 4 s) then MagicDamageCalc2 on the enemies within AOEHexRange (1) of the target,
    target included. Unlock (2.4688 s) ends it (build: mana lock 75, cast lock 76 ticks). Crits only with Precision.
  - **Shred:** the shared GE_MRShred, one "Shred" per target whoever applies it (Void Staff's too: the later end and
    the higher level win). The burst shreds before it damages, so it amplifies itself.
  - **Not modelled:** the beam's retarget when its target dies (dummies never die).
- 2026-11-18, Day 1 PBE patch notes, confirmed in the client build rls-19.1.0.5986094 (read from an FModel raw export, B34; it replaced the patch-notes stand-in, B33): DamageAP 380/570/960 -> 355/530/850. Its timing is unchanged from rls-19.1.0.5973071.
