# Senna (3-cost AttackCaster) · `DA_Senna19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6037882.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6037882.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 3, pool 18; traits: True Damage, Hitmaker
- **HP** 650 / 1170 / 2106 · **AD** 55 / 82.5 / 123.75 · **AS** 0.75 · **Range** 4 · **Armor** 35 · **MR** 35 · **Mana** 0 / 20

### Ability: Reverberation Devastation

> Blast the target, dealing 175/265/450 × AD + 25/35/60 × AP physical damage and marking them. If they are marked, detonate it instead, dealing 1.5 × PhysicalDamageCalc1 damage.
> 
> On detonation or killing a marked enemy, gain 8% Damage Amp until the end of combat.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 55 | 82.5 | 123.75 |
| SpellAD | 175 | 265 | 450 |
| BonusDA | 0.08 | 0.08 | 0.08 |
| SpellAP | 25 | 35 | 60 |
| Duration | 10 | 10 | 10 |
| AOERange | 1 | 1 | 1 |
| MarkerPercentOfSpellAD | 1.5 | 1.5 | 1.5 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 175/265/450 × AD + 25/35/60 × AP
- `PhysicalDamageCalc2` = 1.5 × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Senna19_Attack`: launch 0.531 s (15.93 ticks), variants 0.531, 0.6364; animation length 3.3 s (99 ticks); release at base AS 0.531 s (15.93 ticks)
- Attack projectile: DA_Senna19_AutoAttackProjectile, speed 4000 units/s
- Spell `GA_Senna19_Spell` (chrono `CD_Senna19_CastAnim1`): cast ends 1.2 s (36 ticks), next attack can start 1.2333 s (37 ticks), mana lock removed 1.2 s (36 ticks); ended by `FinishCasting via OnEventBegin:CD_Senna19_CastAnim1:Unlock`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Senna19_Attack` | Chronos | 3.3 | LaunchAttack 0.531, LaunchAttack 0.6364, Unlock 1.2, Unlock 1.32 |
| `CD_Senna19_CastAnim1` | Chronos | 1.2546 | Unlock 1.1984 |
| `CD_Senna19_CastAnim2` | Chronos | 1.0002 | Damage 0.2851, Unlock 0.9864 |
| `CD_Senna19_Celebration` | Chronos | 6.4419 | Default 0, Loop 1.9631 |
| `CD_Senna19_FastYoink` | Chronos | 0.7728 | Lock 0, Unlock 0.5056 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_TrueDamage19_PlayChronoOnTraitActivation`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Senna19_Spell`, `GA_ShopEvents`, `GA_Senna19_MarkDeathTracker`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Senna19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Senna19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Senna19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Senna19_Spell.txt

### Changed since `rls-19.1.0.6028987.Set19.Shipping.pbe`

- row SpellAD: 175 / 265 / 420 -> 175 / 265 / 450
- ability text changed

<!-- AUTO END -->

## Status

- Worksheet status: **implemented 2026-11-17** (`set19champs.Senna`, D1; tests `test_senna.py`)
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | **consistent**: 650 HP, 0/20 mana, AS 0.75 base, range 4 Hex (1★ with three items in the fight) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.531 s (15.93 ticks) | 0.531 s normal, 0.6364 s when the attack crits (CritAttack group, B17); the engine weights the two by crit chance; not measured | P13, B17 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 4000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.2333 s (37 ticks) | blast (CastAnim1) 37 ticks, detonation (CastAnim2) 31 ticks, each from its own Unlock event (D1) | D1 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.2 s (36 ticks) | **consistent**: two lock lengths appear in the fight, ~74-77 and ~59-64 frames to the first mana after the cast (36 and 30 ticks = 72 and 60 frames, then up to one 0.25 s regen step) | E2 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | the blast (not the detonation) applies one simulated attack at cast start: on-attack items hear it (G11); role mana falls inside the mana lock | G11 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | cancels Combat.Attacking (T4) | script |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | implemented from the script (D1): blast Calc1 + mark, detonation 1.5 x Calc1 + 8% damage amp; damage not yet checked | script |
| Q14 | Passives and other mechanics that need modelling | see ability text | mark/detonate alternation and the stacking amp (D1); Hitmaker (B18) and True Damage A-Side (B19) implemented | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-17 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 f25700 (planning, round 1-10) | 60 | inspection panel | 1★, three items: AD 63 (15%), AP 25%, AS 0.94, crit 45%, armor 50, MR 70, 0/20 mana, 8/s regen; True Damage 2/3, Hitmaker 1/2 | base stats as built (items not all modelled) | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 f25637-28024 (`tools/vod_text_changes.py`, mana) | 60 | the 0 shown at each cast and the first mana after it | casts at f26197, 26332, 26474, 26611, 26737, 26873, 26995, 27115, 27216, 27314, 27424, 27520, 27639, 27743; first mana after: +77, 74, 62, 74, 62, 76, 62, 59, 62, 74, 64, 86, 74, 76 frames | two lock lengths, as the two casts predict (36 and 30 ticks); not a strict alternation because a real fight changes target. Attack releases not separable from the 8/s regen with the detector (it misses some +2 steps); crit vs normal windup not measured | Q9 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | VOD4 (19-0-51-650) 11:37-11:41 (round 1-4, board every 8 frames) | 60 | damage numbers, True Damage (3) A-Side | 1★ with Quicksilver and Guinsoo's (AS 0.94, crit 45%, AP 10%, MR 55); every physical number followed by a true one: 30 -> 5, 22 -> 4, 18 -> 3, 12 -> 2, 35 -> 6, 25 -> 4, magic 7 -> 1 | true = 18% of the damage dealt, rounded down (B19) | Q14 |

## Decisions and notes

- 2026-11-17, D1 (implemented, `set19champs.Senna`):
  - **Cast choice (GA_Senna19_Spell 0xf25):** if her attack target has no GE_Senna19_Marker she fires the blast
    (CD_Senna19_CastAnim1): the SennaMis missile (0.7859 s, 4000 units/s) applies the marker and
    PhysicalDamageCalc1 = SpellAD x AD + SpellAP x AP. Otherwise she detonates (CD_Senna19_CastAnim2): at its
    Damage event (0.2851 s) the marker is removed and PhysicalDamageCalc2 = 1.5 x Calc1 applied; the SoulRip
    projectile's return gives GE_Senna19_Cast2Buff, OutgoingDamageMultiplier + BonusDA (8%), infinite and
    stacking. Both damages are physical spell damage (crit only with Precision).
  - **Marker:** infinite (the 10 s Duration row is unused), so against dummies the casts alternate.
  - **Locks:** each cast's own Unlock: blast cast lock 37 ticks / mana lock 36, detonation 31 / 30.
  - **Attacks:** crits play CritAttack (launch 0.6364 s) instead of the normal 0.531 s; weighted by crit chance
    (B17).
  - **Assumed:** the +8% is applied at the detonation instead of the SoulRip's return (TFTFixedTimeSplineMovement,
    flight time not in the data). Nothing of hers lands in between (the cast cancels her attack and lasts until
    after the return), so the damage is the same. The blast's simulated attack is not modelled (mana lock, G11).
