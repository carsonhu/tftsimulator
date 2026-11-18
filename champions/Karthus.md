# Karthus (2-cost MagicCaster) · `DA_Karthus19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Pentakill, Arcanist
- **HP** 550 / 990 / 1782 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 10 / 50

### Ability: Requiem

> After a brief delay, deal 440/660/930 × AP magic damage to the current target. If they die, recast this ability at 70% effectiveness.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| APDamage | 440 | 660 | 930 |
| PercentDamageOfPreviousCast | 0.7 | 0.7 | 0.7 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 440/660/930 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Karthus19_Attack`: launch 0.4582 s (13.75 ticks); animation length 1.8333 s (55 ticks); release at base AS 0.4582 s (13.75 ticks)
- Attack projectile: DA_Karthus19_AutoAttackProjectile, speed 1200 units/s
- Spell `GA_Karthus19_Spell` (chrono `CD_Karthus19_CastAnim`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Karthus19_Attack` | Chronos | 1.8333 | LaunchAttack 0.4582, Unlock 0.7332 |
| `CD_Karthus19_CastAnim` | Chronos | 1.8764 | Damage 1.1269, Unlock 1.337 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Karthus19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Karthus19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Karthus19_Spell.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Karthus`, D1); mana, locks and rhythm checked against VOD3
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (1★, no items: 550 HP, 10/50, AD 30, AS 0.75, armor/MR 30) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster | confirmed: 7 per attack, 2/s | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.4582 s (13.75 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1200 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | Unlock 1.337 s: cast lock 42 ticks | confirmed: the next attack pays 57 ticks after the bar fills (1 + 42 + 14), as the engine | E2 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | Unlock 1.337 s: 41 ticks | consistent: mana shown again 42 ticks after the filling attack | E2 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | predicted: 0 (no GE_SimulateLaunchAttack in GA_Karthus19_Spell) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read: D1); no damage number read yet | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | the recast on a kill: not modelled (dummies never die); Pentakill (B25), Arcanist (B16) implemented | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD3 (`…PBE_11-17-2026_17-13-37-283.mp4`, 60 fps), the owner's PBE recording, build
`rls-19.1.0.5973071`; Karthus 1★, no items, round 1-5, panel open f21643-22544.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 6:02 | 60 | inspection panel | 550/550, 10/50, 2/s; AD 30, AS 0.75, armor/MR 30, crit 25%; no items | as built | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 f21643-22148 (`tools/vod_text_changes.py`, mana) | 60 | mana text | 10, 18, 20, 27, 28, 29, 30, 37, 38, 47, 48, cast (f22034), 7 (f22118), 15 (f22148): attacks +7 at f21712, 21793, 21873, 21954, 22034 (40 ticks apart), regen 0.5 a step | the bar fills at f22034; mana again +42 ticks (lock 41 + T4); next attack +57 ticks: engine 57. A second "cast" at f22469 comes as the round ends (left out) | Q2, Q7, Q9 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Karthus`):
  - **Spell (GA_Karthus19_Spell):** mana lock; CD_Karthus19_CastAnim at his target; at Damage (1.1269 s)
    MagicDamageCalc1 (APDamage x AP) x Max(0.7 ^ recasts, minimum), magic spell damage, crit only with Precision; at
    Unlock (1.337 s) a recast if the target died, else the cast ends. The build's timeline has no lock: mana lock =
    the Unlock tick (41), cast lock 42, as for Lux.
  - **Not modelled:** the recast at 70% on a kill (dummies never die).

