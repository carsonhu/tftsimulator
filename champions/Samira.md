# Samira (2-cost AttackCaster) · `DA_Samira19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6005555.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6005555.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Classical, Renegade, Trickshot
- **HP** 550 / 990 / 1782 · **AD** 42 / 63 / 94.5 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 55
- **Unlock**: 2 items on a Classical, Renegade, or Trickshot champion.

### Ability: Bullets N' Roses

> Passive: When Samira critically strikes an enemy, they become Captivated for 3 seconds.
> 
> Active: Fire 10 bullets at the current target, each dealing 4/6/9 × AP + 38/42/86 × AD damage.
> 
> Captivated enemies grant bonuses to Classical champions.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 42 | 63 | 94.5 |
| NumBullets | 10 | 10 | 10 |
| DamageAP | 4 | 6 | 9 |
| DamageAD | 38 | 42 | 86 |
| CaptivateDuration | 3 | 3 | 3 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 4/6/9 × AP + 38/42/86 × AD

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Samira19_Attack`: launch 0.2669 s (8.01 ticks), variants 0.2669, 0.267, 0.2693; animation length 2.9 s (87 ticks); release at base AS 0.2669 s (8.01 ticks)
- Attack projectile: DA_Samira19_AutoAttackProjectile, speed 2800 units/s
- Spell `GA_Samira19_Spell` (chrono `CD_Samira19_CastAnim`): cast ends 1.3333 s (40 ticks), next attack can start 1.3667 s (41 ticks), mana lock removed 1.3333 s (40 ticks); ended by `FinishCasting via OnEventBegin:CD_Samira19_CastAnim:Unlock`
  - notes: curve CT_Trickshot19.RichochetDamage input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_2), used star 2 ×1; curve CT_Trickshot19.NumRichochets input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_1), used star 2 ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Samira19_Attack` | CD_Samira19_Attack | 2.9 | LaunchAttack 0.2669, LaunchAttack 0.267, LaunchAttack 0.2693, Unlock 1.0533, Unlock 1.1067, Unlock 1.16 |
| `CD_Samira19_CastAnim` | CD_Samira19_CastAnim | 1.3385 | BeginFire 0.1962, EndFire 0.5712, Unlock 1.3105 |
| `CD_Samira19_Celebration` | CD_Samira19_Celebration | 10.7918 | Default 0, Loop 2.9287 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Samira19_TrickshotHandler`, `GA_Trickshot19_HandleAutoAttackBounce`, `GA_AutoAttack`, `GA_LaunchProjectileAttack_Trickshot19`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Samira19_Spell`, `GA_ShopEvents`, `GA_Samira19_CaptivateCritTracker`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Samira19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Samira19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Samira19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Samira19_Spell.txt

### Changed since `rls-19.1.0.5995286.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Samira`, D1); panel, mana and rhythm checked against VOD3
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed with her items (1★) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster | confirmed: 7 per attack, 2/s | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2669 s (8.01 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2800 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.3667 s (41 ticks) | **open**: VOD3's attack after the cast paid 54.5 ticks after the filling attack, the engine 50 (she did not move) | E3 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.3333 s (40 ticks) | consistent: overflow shown 41.5 ticks after the filling attack | E3 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | predicted: one GE_SimulateLaunchAttack per cast, at the first bullet (a DoOnce; assumed to reset each cast) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read: D1); no bullet damage number read yet | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | Captivate on crits (D1); Renegade (B27), Classical (B28), Trickshot bullets implemented | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD3 (`…PBE_11-17-2026_17-13-37-283.mp4`, 60 fps), the owner's PBE recording, build
`rls-19.1.0.5973071`; Samira 1★, round 1-4 (second fight), panel open f19253-19772.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 5:23 (f19380) | 60 | inspection panel | 700/700, 0/60, 2/s; AD 85 (+103%), AS 0.83, crit 95%, armor/MR 30; Striker's Flail, Infinity Edge, Deathblade; Renegade (2) active, Classical, Trickshot, True Damage inactive | engine with those: HP 700, AD 85.47, AS 0.825, crit 0.95 | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 f19253-19772 (`tools/vod_text_changes.py`, mana) | 60 | mana text | 27, 28, 29, 36, 37, 38, 45, 46, 47, 48, 55, 56, 57, cast, 4, 5, 12, 13, 14, 21, 22, 23, 30, 31: regen 0.5 a step, attacks +7 at f19296, 19370, 19442, 19515 (cast), 19624, 19698, 19770 | attacks 37, 36 ticks apart (engine 36/37) | Q2 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 f19515-19630 (mana text; board every 8 frames) | 60 | the cast | overflow 4 shown +83 frames (41.5 ticks) after the filling attack; next attack's mana +109 frames (54.5 ticks); she stood still, the barrage flew at a target that stayed | mana lock as built (40 + T4); the attack after the cast 4.5 ticks later than the engine's 50 (n = 1) | Q7, Q9 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Samira`):
  - **Spell (GA_Samira19_Spell):** mana lock; CD_Samira19_CastAnim at her target; at BeginFire (0.1962 s)
    RepeatAction(TimeToShoot 0.374933 / NumBullets, NumBullets 10), the first at once, alternating CD_Samira19_Mis1 /
    Mis2 (1500). Each arrival: PhysicalDamageCalc1 (DamageAP x AP + DamageAD x AD), physical spell damage, crits
    only with Precision (Renegade or Infinity Edge give it), then the Trickshot bounce (CD_Samira19_MisBounce, 1500,
    x RichochetDamage^k). Unlock (1.3105 s) ends the cast (build: 40 / 41 ticks).
  - **Simulated attack:** GE_SimulateLaunchAttack on the first bullet's OnFired, behind a DoOnce. Assumed to reset
    every cast (one launch per cast for on-attack items); if the ability instance persisted it would fire on her first
    cast only.
  - **Captivate (GA_Samira19_CaptivateCritTracker):** any crit of hers Captivates the enemy for 3 s, if Classical is
    active. The engine's crits are averaged, so a Captivate comes with each CRIT event (I6).

