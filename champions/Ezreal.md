# Ezreal (2-cost AttackCaster) · `DA_Ezreal19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Heartsteel, Encore
- **HP** 550 / 990 / 1782 · **AD** 40 / 60 / 90 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 35

### Ability: Bite the Bullet

> Fire a missile that marks the target, then fire a second blast that detonates it. The explosion deals 190/285/430 × AD + 30/45/70 × AP physical damage to the target and 0.33 × PhysicalDamageCalc1 physical damage to enemies within 1 hex.
> 
> Heartsteel Upgrade: Detonation deals 0.25 more damage. Every 3rd cast hits enemies in a 2 hex radius instead.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 40 | 60 | 90 |
| ADDamage | 190 | 285 | 430 |
| APDamage | 30 | 45 | 70 |
| AoEPercentDamage | 0.33 | 0.33 | 0.33 |
| HeartsteelStan_PercentIncreasedAbilityDamage | 0.25 | 0.25 | 0.25 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 190/285/430 × AD + 30/45/70 × AP
- `PhysicalDamageCalc2` = 0.33 × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Ezreal19_Attack`: launch 0.3371 s (10.11 ticks); animation length 2.7333 s (82 ticks); release at base AS 0.3371 s (10.11 ticks)
- Attack projectile: DA_Ezreal19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Ezreal19_Spell` (chrono `CD_Ezreal19_CastAnim`): cast ends 1.1667 s (35 ticks), next attack can start 1.2 s (36 ticks), mana lock removed 1.1667 s (35 ticks); ended by `FinishCasting via OnEventBegin:CD_Ezreal19_CastAnim2:Unlock`
  - notes: curve CT_Encore19.RecastEffectiveness input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_1), used star 2 ×1; projectile (hit time depends on travel) ×6

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Ezreal19_Attack` | Chrono | 2.7333 | LaunchAttack 0.3371, Unlock 1.0932 |
| `CD_Ezreal19_CastAnim` | Chrono | 0.7984 | Unlock 0.6663 |
| `CD_Ezreal19_CastAnim2` | Chrono | 0.4837 | Unlock 0.4781 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Ezreal19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Ezreal19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Ezreal19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Ezreal19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Ezreal19_Spell.txt

<!-- AUTO END -->

## Status

- Worksheet status: **implemented 2026-11-17** (`set19champs.Ezreal`, D1; tests `test_ezreal.py`)
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | **consistent**: 650 HP 1★ (1,165 2★), 0/35 mana, 2/s regen, range 4 Hex; AS 0.90 at combat start = 0.75 x (1 + Guinsoo 10% + Titan's 10%) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster | **consistent**: +7 per release, 2/s regen (shown +1 every 30 frames) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | **consistent** with T10: first release 12 ticks after combat start (engine 11: 0.3371 s windup) | E2 |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3371 s (10.11 ticks) | **consistent**: releases within a tick before the first cast (12, 44, 75 vs engine 11, 44, 76) | E2 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.2 s (36 ticks) | **open**: from the release that fills the bar to the next release 46 and 44 ticks in the VOD, engine 48 (cast a tick after the fill, 36-tick lock, 11-tick windup); also 56.5 and 48 (retargeting) | E2 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.1667 s (35 ticks) | predicted | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | **confirmed**: two simulated attacks per cast, at the cast and at stage 2: two Titan's Resolve stacks (docs/ITEMS.md); role mana falls inside the mana lock | G11 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | cancels Combat.Attacking (T4) | script |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | **consistent**: the second cast's detonation dealt 327 (a crit vs a frontliner), so FirstCastHit resets each cast (D1); the exact value is not checkable (Titan's stacks, unknown armor) | E3 |
| Q14 | Passives and other mechanics that need modelling | see ability text | two-stage cast and the Encore second missile (D1); Heartsteel upgrade not implemented | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-17 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | VOD4 (19-0-51-650) 20:52-21:04 (planning and combat start, round 2-2) | 60 | inspection panel, item tooltips | 1★, Titan's Resolve, Infinity Edge, Guinsoo's Rageblade (hovered); at combat start AD 56 (40%), AP 10%, AS 0.90, crit 70%, armor 50, MR 30, 0/35 mana, 2/s; Heartsteel 1, Encore 1/2 (inactive); the 5% AD beyond Infinity Edge's 35% is Illbeats (2)'s team share (owner; B20) | as built plus the items and Illbeats | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | VOD4 (19-0-51-650) f75600-78000 (`tools/vod_text_changes.py`, mana and AS) | 60 | releases, casts | AS steps every 60 frames from f76024 (Guinsoo, +1.000 s: combat start f75964). Mana: +7 at f75988, 76052, 76114 (12, 44, 75 ticks); 0/35 (cast) at f76174 (105); then releases f76266, 76319, 76369 (151, 177.5, 202.5); cast f76447 (241.5); release f76535 (285.5); casts f76717, 76980 | engine (IE, Guinsoo, +10% AS for Titan's): 11, 44, 76, cast 107, 154, 180, 204: within a tick before the cast, 2-3 ticks slow around it (Q7) | Q2-Q4, Q7 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | VOD4 (19-0-51-650) f76450-76546 (board, every 4 frames) | 60 | 2nd cast | stage-2 beams from ~+26 ticks (20 + 6 predicted); a 327 detonation number on the target at ~+41 ticks (target ~5 hexes away) | the second cast deals damage: FirstCastHit is per cast | Q13 |

## Decisions and notes

- 2026-11-17, D1 (implemented, `set19champs.Ezreal`):
  - **Stage 1 (GA_Ezreal19_Spell 0x1247):** CD_Ezreal19_CastAnim fires SpellMis (the mark, no damage); its Unlock
    (0.6663 s) calls FireAtTarget (0x16ba).
  - **Stage 2:** CD_Ezreal19_CastAnim2 fires SpellMis at 0.1729 s (2200 units/s); its arrival (0x66 -> 0x382)
    applies PhysicalDamageCalc1 to the target and PhysicalDamageCalc2 (0.33 x Calc1) to the other enemies within 1
    hex. CastAnim2's Unlock ends the spell (cast lock 36 ticks, mana lock 35).
  - **Encore:** with the Set19.Trait.Encore tag the chrono's SecondCast group fires a second SpellMis at 0.319 s.
    FirstCastHit (set by the cast's first detonation, reset every cast: E3) makes it deal x RecastEffectiveness.
  - **Not modelled:** the Heartsteel upgrade (+25%, 2-hex radius every 3rd cast; Heartsteel is not implemented); the
    stage-1 simulated attack (mana lock, G11). The script's W/Q chrono speed variables are never read.
  - **Assumed:** the detonating missile flies his attack range (4 hexes); adjacent enemies hit = targets - 1.
