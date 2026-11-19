# Syndra (3-cost MagicCaster) · `DA_Syndra19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5986094.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5986094.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 3, pool 18; traits: Beach Pop, Choreographer
- **HP** 650 / 1170 / 2106 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 35 · **MR** 35 · **Mana** 0 / 30

### Ability: Serve's Up

> Spike a volleyball at target, dealing 300/450/720 × AP magic damage. It bounces to an enemy behind them with the least items, dealing 110/165/265 × AP magic damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| SecondaryDamageAP | 110 | 165 | 265 |
| ShredPercent | 20 | 20 | 20 |
| PrimaryDamageAP | 300 | 450 | 720 |
| ShredDuration | 0 | 0 | 0 |
| StartingBounceAngle | 120 | 120 | 120 |
| SearchAngleIncreasePerCheck | 30 | 30 | 30 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 300/450/720 × AP
- `MagicDamageCalc2` = 110/165/265 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Syndra19_Attack`: launch 0.1377 s (4.13 ticks), variants 0.1377, 0.27; animation length 2.4667 s (74 ticks); release at base AS 0.1377 s (4.13 ticks)
- Attack projectile: DA_Syndra19_AutoAttackProjectile, speed 1800 units/s
- Spell `GA_Syndra19_Spell` (chrono `CD_Syndra19_CastAnim`): cast ends 2 s (60 ticks), next attack can start 2.0333 s (61 ticks), mana lock removed 2 s (60 ticks); ended by `FinishCasting via OnEventBegin:CD_Syndra19_CastAnim:Unlock`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Syndra19_Attack` | CD_Syndra19_Attack | 2.4667 | LaunchAttackVariant1 0.1377, LaunchAttackVariant2 0.27, Unlock 0.8667, Unlock 0.9867 |
| `CD_Syndra19_CastAnim` | CD_Syndra19_CastAnim | 2 | Default 0, Windup 0.7749, LaunchProjectile 1.3116, FinishAnimation 1.7989, Unlock 1.99 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Syndra19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Syndra19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Syndra19_Spell.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Syndra`, D1); predicted from the script, the panel
  checked on VOD5 (E1); no cast timed yet
- Keep in the simulator: **yes** (owner, 2026-11-18)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed for HP, mana, range | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster: 7 per attack, 2/s | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.1377 s / 0.27 s (two animations) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1800 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 2.0333 s (61 ticks): the cast chrono's Unlock (1.99 s, its third phase) + 1 tick | predicted | D1 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2 s (60 ticks) | predicted | D1 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 (no GE_SimulateLaunchAttack) | predicted | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | 300/450/720 x AP on the target, 110/165/265 x AP on the bounce target | predicted (script and effects read) | D1 |
| Q14 | Passives and other mechanics that need modelling | the bounce's target choice; Shred rows unused | predicted | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |
| Q16 | When the volleyball and the bounce land | ball 40 + 11 ticks after the cast (4 hexes), bounce 7 ticks later (2 hexes, to the enemy 2 hexes behind, G22), 15 when bouncing in place | open (VOD5 11:35-12:30 has her fighting) | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 (`…PBE_11-18-2026_0-57-11-500.mp4`) 11:33, owner's screenshot | 60 | inspection panel (round 2-3, planning) | 650/650, 0/30, 14 mana/s; AD 39, AP 30%, AS 0.86, crit 45%, armor 58, MR 78, range 4 hex, Back; 3 items; Beach Pop, Choreographer | HP, mana, range as built; the other stats carry items and traits, not checked | Q1 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Syndra`):
  - **Cast (GA_Syndra19_Spell):** mana lock; CD_Syndra19_CastAnim runs three phases (Default 0.7749 s, Windup
    1.0240 s, FinishAnimation 0.2011 s). The build read it as one phase until the snapshot fix (2026-11-18:
    LaunchProjectile 0.4061 -> 1.3116 s, Unlock 0.7364 -> 1.99 s; the spell timing already had them). Volleyball
    spawns at 1.3085 s, 2400 units/s; Unlock (1.99 s) ends the cast and the mana lock.
  - **Bounce:** an expanding cone behind the target (120 degrees, +30 per check, 1800 units, away from Syndra), the
    farthest-back enemy found, ties to the nearest; 'Bounce' at 2000 units/s; nobody: in place on the target after
    the BounceInPlace chrono's 0.4999 s (G21). Each enemy's items are equal, so the fewest-items sort changes nothing.
  - **Not modelled:** ShredPercent / ShredDuration (0) are read but never applied.
