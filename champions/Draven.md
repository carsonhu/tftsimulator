# Draven (3-cost AttackCaster) · `DA_Draven19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 3, pool 18; traits: Illbeats, Trickshot
- **HP** 650 / 1170 / 2106 · **AD** 45 / 67.5 / 101.25 · **AS** 0.75 · **Range** 4 · **Armor** 35 · **MR** 35 · **Mana** 0 / 60

### Ability: You Spin Me Round (Like An Axe)

> Throw a massive spinning record at the target, dealing 140/210/340 × AD physical damage. The record leaves behind a vortex that lasts 3 seconds and deals 1 × GenericCalc2 + 1 × GenericCalc1 physical damage per second split amongst enemies within 1 hex.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 45 | 67.5 | 101.25 |
| BladeDamage | 140 | 210 | 340 |
| BladeRiftPerSecondAD | 100 | 150 | 250 |
| BladeRiftPerSecondAP | 15 | 25 | 35 |
| Duration | 3 | 3 | 3 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 140/210/340 × AD
- `GenericCalc1` = 100/150/250 × AD
- `GenericCalc2` = 15/25/35 × AP
- `PhysicalDamageCalc2` = 1 × GenericCalc2 + 1 × GenericCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Draven19_Attack`: launch 0.2587 s (7.76 ticks); animation length 1.4667 s (44 ticks); release at base AS 0.2587 s (7.76 ticks)
- Attack projectile: DA_Draven19_AutoAttackProjectile, speed 1600 units/s
- Spell `GA_Draven19_Spell` (chrono `CD_Draven19_Spell`): cast ends 1.6667 s (50 ticks), next attack can start 1.7 s (51 ticks), mana lock removed 1.6667 s (50 ticks); ended by `FinishCasting via OnChronoStopped:CD_Draven19_Spell:None`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Draven19_Attack` | Chronos | 1.4667 | LaunchAttackVariant1 0.2587, LaunchAttackVariant2 0.2587, Unlock 1.1733 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Trickshot19_HandleAutoAttackBounce`, `GA_AutoAttack`, `GA_LaunchProjectileAttack_Trickshot19`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Draven19_Spell`, `GA_ShopEvents`, `GA_Draven19_TrickshotHandler`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Draven19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Draven19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster | role 7 / attack not checkable here (items add mana: +9 per attack, extra regen); **paid at the release** | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2587 s (7.76 ticks) | **consistent**: attack start ~f13409, release f13416-13417 (≈ 8 frames; predicted 8) | E2 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1600 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.7 s (51 ticks) | **consistent**: next attack started +50 frames after the cast (predicted 51), released +58 (predicted 59) | E2, E3 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.6667 s (50 ticks) | **confirmed**: banked overflow appeared +51 frames after the cast (predicted mana lock 50; the panel shows it the frame after) | E3 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted | |
| Q14 | Passives and other mechanics that need modelling | see ability text | open | |
| Q15 | Can this unit be simulated realistically? | | open | |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: `Outplayed/…PBE_11-17-2026_15-16-17-933.mp4` (owner's PBE recording, Tocker's Trials, 2026-11-17 15:08-15:16; build `rls-19.1.0.5973071`), 1280x720 at 30 fps (1 frame ≈ 1 tick). Mana from `tools/vod_panel.py`; attack frames read from zoomed frame tiles of the white-ringed unit.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | 446.8 s (f13405) | 30 | inspection panel | 1 star, 3 items, AS 1.16, crit 80%; Illbeats 1/2, Trickshot 2/3 | itemised: mana per attack and regen here are not the role's alone | Q1 (not usable) |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | f13404-13427 (zoomed) and the mana series | 30 | first attack after the cast at f13359 | idle f13404-13408; attack animation from ~f13409; axe leaves f13416-13417; +9 mana at f13417 | mana at the **release**; windup ≈ 8 | Q2, Q4, Q7 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | cast f13359 (bar 53.25 → 0); +2.25 at f13410 | 30 | mana lock, overflow | the filling attack (+9) was never displayed; +2.25 appears at +51 = 53.25 + 9 - 60 exactly | overflow is **banked** (G10); the panel shows 0 during the lock and the overflow when it ends | Q9, G10 |

## Decisions and notes

- 2026-11-17: Draven pays attack mana at the release (E2, seen on screen). His items change his mana per attack
  and regen, so Q2's role numbers need an itemless fight.
