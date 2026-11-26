# Tristana (2-cost AttackCaster) · `DA_Tristana19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6037882.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6037882.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Hyperpop, Hitmaker
- **HP** 550 / 990 / 1782 · **AD** 45 / 67.5 / 101.25 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 55
- **Unlock**: Get 5 kills with Hyperpop active.

### Ability: Head Banger

> Throw bombs at 3 nearby enemies and detonate them, each dealing 125/190/285 × AD + 15/20/30 × AP physical damage. The final blast deals 2 × PhysicalDamageCalc1 damage instead.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 45 | 67.5 | 101.25 |
| ADDamage | 125 | 190 | 285 |
| APDamage | 15 | 20 | 30 |
| FinalShotPercentOfNormalShot | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 125/190/285 × AD + 15/20/30 × AP
- `PhysicalDamageCalc2` = 2 × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Tristana19_Attack`: launch 0.2217 s (6.65 ticks); animation length 1.8333 s (55 ticks); release at base AS 0.2217 s (6.65 ticks)
- Attack projectile: DA_Tristana19_AutoAttackProjectile, speed 2250 units/s
- Spell `GA_Tristana19_Spell` (chrono `CD_Tristana19_CastAnim_Part1`): cast ends 1.2333 s (37 ticks), next attack can start 1.2667 s (38 ticks), mana lock removed 1.2333 s (37 ticks); ended by `FinishCasting via OnEventBegin:CD_Tristana19_CastAnim_FinalShot:Unlock`
  - notes: projectile (hit time depends on travel) ×15; rate from unresolved switch(Temp_int_Variable_2){0: Temp_real_Variable_3; 1: Temp_real_Variable_2; 2: Temp_real_Variable_1; 3: Temp_real_Variable; default: K2Node_Select_Default_2} ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Tristana19_Attack` | Chronos/Default | 1.7986 | LaunchAttack 0.2217, Unlock 0.7333 |
| `CD_Tristana19_HyperpopHypemeter_Intro` | Chronos/Default | 1 | StartHype 0.95 |
| `CD_Tristana19_HyperpopHypemeter_Outro` | Chronos/Default | 1.0006 | EndOutro 0.95 |
| `CD_Tristana19_CastAnim_FinalShot` | Chronos/Spell | 0.6571 | Unlock 0.6386 |
| `CD_Tristana19_CastAnim_Part1` | Chronos/Spell | 0.5531 | Fire 0.1549, Fire2 0.1738, Fire3 0.1906, Unlock 0.5454 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Tristana19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Tristana19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Tristana19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Tristana19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Tristana19_Spell.txt

### Changed since `rls-19.1.0.6028987.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Tristana`, D1); the cast's length (three shots) checked
  on VOD6 to a tick (E2)
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has her at 2-3)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | mana 55, 2/s confirmed; HP 1025 at 2 stars vs 990 (+35 from a source not identified) | E2 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster: 7 per attack, 2/s | confirmed (+7 steps, +1 every 0.5 s) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2217 s (6.65 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2250 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | Part1 + 3 shots: 70 ticks (the build's 38 follows one shot) | consistent (the mana lock, Q9) | E2 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 69 ticks (EndSpell after the third shot) | confirmed: the banked overflow shows 70 / 70.5 / 70 ticks after the bar empties (69 + the tick after the fill) | E2 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 1 GE_SimulateLaunchAttack at the last detonation | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | 3 bombs, ADDamage x AD + APDamage x AP each, the last x2 | predicted | D1 |
| Q14 | Passives and other mechanics that need modelling | none | not applicable | |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18, 60 fps; client rls-19.1.0.5986652, not exported: the simulator's newest is 5986094). Round 2-3:
Tristana 2 stars. Mana from `tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f39142-40289 (round 2-3) | 60 | mana and Health text | 1025/1025, x/55, +7 steps, +1 every 0.5 s; casts f39433 (52 + 7 = 59), f39741 (51 + 7 = 58), f40016 (50 + 7 = 57); the overflow 4 / 3 / 2 shows at f39573, f39882, f40156: +140, +141, +140 frames | the mana lock 69 ticks + the tick after the fill: Part1 and three shots (1.25, 1.25, 1) | Q1, Q2, Q7, Q9 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Tristana`):
  - **Cast (GA_Tristana19_Spell):** mana lock (0x2b49); CD_Tristana19_CastAnim_Part1 at the targets' average spot.
    'Fire' / 'Fire2' / 'Fire3' (0.1549 / 0.1738 / 0.1906 s): a bomb each (the first _BIGProjectile) at the nearest
    enemy not yet bombed (GetTargets: N nearest by row distance, minus ActorsAlreadyCastedOn; her target when none
    is left).
  - **Detonations (KnockThemDown):** after Part1's 'Unlock' (0.5454 s), CD_Tristana19_CastAnim_FinalShot at small
    bomb 1's enemy (rate 1.25), small bomb 2's (1.25), then the big bomb's (1): a 'SmallBomb' / 'MainBomb' (spawned
    0.1549 s / rate, 1800 units/s); arrival: GE_Tristana19_Damage (PhysicalDamageCalc1), the last
    GE_Tristana19_DamageBig (PhysicalDamageCalc2 = 2 x Calc1) and GE_SimulateLaunchAttack. Each shot's 'Unlock'
    (0.6386 s / rate) starts the next; after the third, EndSpell (lock off, FinishCasting).
  - **Simulated:** big bomb on her target, small ones on the next nearest (the target again if none); chronos
    chained on whole ticks.
