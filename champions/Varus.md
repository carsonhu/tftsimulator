# Varus (1-cost AttackCaster) · `DA_Varus19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Rock, Encore
- **HP** 500 / 900 / 1620 · **AD** 35 / 67.5 / 101.25 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 30 / 70

### Ability: One Thousand Arrows

> Fire a hail of arrows, dealing 30/45/70 × AP + 230/345/520 × AD physical damage to the target and 0.5 × PhysicalDamageCalc1 damage to adjacent enemies. 20% Slow them for 4 seconds.
> 
> Slow: Reduce Attack Speed

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 35 | 67.5 | 101.25 |
| DamageAD | 230 | 345 | 520 |
| SlowLevel | 20 | 20 | 20 |
| DamageAP | 30 | 45 | 70 |
| AOEDamagePercent | 0.5 | 0.5 | 0.5 |
| SlowDuration | 4 | 4 | 4 |
| AOEHexRange | 1 | 1 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 30/45/70 × AP + 230/345/520 × AD
- `PhysicalDamageCalc2` = 0.5 × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Varus19_Attack`: launch 0.425 s (12.75 ticks); animation length 2.5 s (75 ticks); release at base AS 0.425 s (12.75 ticks)
- Attack projectile: DA_Varus19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Varus19_Spell` (chrono `CD_Varus19_CastAnim`): cast ends 1 s (30 ticks), next attack can start 1.0333 s (31 ticks), mana lock removed 1 s (30 ticks); ended by `FinishCasting via OnEventBegin:CD_Varus19_CastAnim:Unlock`
  - notes: curve CT_Encore19.RecastEffectiveness input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_3), used star 2 ×1; projectile (hit time depends on travel) ×6

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Varus19_Attack` | CD_Varus19_Attack | 2.5 | LaunchAttack 0.425, Unlock 1 |
| `CD_Varus19_CastAnim` | CD_Varus19_CastAnim | 1.0153 | Fire 0.4278, Encore 0.6286, Unlock 1.0005 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Varus19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Varus19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Varus19_Spell.txt

<!-- AUTO END -->

## Status

- Worksheet status: **in progress (first VOD read 2026-11-17)**
- Keep in the simulator: **undecided** (remove if it can't be simulated realistically; give the reason)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | predicted | |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster | **paid at the release** (7 / attack seen; regen 2 / s) | E2, E4 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.425 s (12.75 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.0333 s (31 ticks) | **refuted?** next arrow released +37 frames after the cast; predicted cast lock 31 + windup 13 = 44. Needs more casts | E4 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1 s (30 ticks) | **confirmed**: banked overflow appeared +31 frames after the cast (predicted mana lock 30) | E3 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | the filling attack released ~1 frame before the cast, so no attack was in progress | E2 |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted | |
| Q14 | Passives and other mechanics that need modelling | see ability text | open | |
| Q15 | Can this unit be simulated realistically? | | open | |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: `Outplayed/…PBE_11-17-2026_15-16-17-933.mp4` (owner's PBE recording, Tocker's Trials, 2026-11-17 15:08-15:16; build `rls-19.1.0.5973071`), 1280x720 at 30 fps (1 frame ≈ 1 tick). Mana from `tools/vod_panel.py`; attack frames read from zoomed frame tiles of the white-ringed unit.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | 167.9 s (f5036), 174.1 s (f5222) | 30 | inspection panel | 1 star; Guinsoo's Rageblade (AS 0.77 at combat start → 1.06 at f5222); Rock 1/3 and Encore 1/2 inactive | AS changes through the fight (attack gaps 39 → 24 frames) | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | f5194-5241 (zoomed) | 30 | the attack before the cast | arrow streak leaves f5198-5200; bar 67.8 → 0 at f5200, the +7 never displayed | the filling attack paid at its **release**; the cast followed the next frame (T4) | Q2, Q12, T4 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | cast f5200; +6.1 at f5231 | 30 | mana lock, overflow | overflow appears at +31 | mana lock ≈ 30 as predicted; overflow banked (G10) | Q9, G10 |
| E4 | 2026-11-17 | rls-19.1.0.5973071 | f5226-5238 (zoomed); +7 at f5237 | 30 | first attack after the cast | bow drawn from ~f5224-5226; arrow leaves f5236-5237 with the +7; spell arrow fired f5213-5214 (= the cast timeline's Fire at 0.4278 s, 13 ticks) | mana at the **release**. The release at +37 is 7 frames earlier than predicted (+44): the cast lock looks like ~24, not 31, although the mana lock (30) held | Q2, Q7 |

## Decisions and notes

- 2026-11-17: Varus pays at the release (E2, E4, seen on screen). Open: his cast lock (E4 suggests ~24 ticks
  against a predicted 31, while the mana lock matched its prediction): needs more casts, ideally at base AS.
