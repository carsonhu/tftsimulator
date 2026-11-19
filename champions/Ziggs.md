# Ziggs (1-cost MagicMarksman) · `DA_Ziggs19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5986094.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5986094.Set19.Shipping.pbe`

- **Role** MagicMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Hyperpop, Arcanist, Swiftstriker
- **HP** 500 / 900 / 1620 · **AD** 10 / 15 / 22.5 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 0 / 50

### Ability: GlitterBOM3S

> Passive: Attacks deal 40/60/90 × AP bonus magic damage.
> 
> Active: Throw a bomb at the target that deals 155/235/355 × AP magic damage to them and 70/105/160 × AP magic damage to adjacent enemies.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 10 | 15 | 22.5 |
| InitialDamage | 155 | 235 | 355 |
| AADamageAP | 40 | 60 | 90 |
| SecondaryDamageAP | 70 | 105 | 160 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 155/235/355 × AP
- `MagicDamageCalc2` = 70/105/160 × AP
- `MagicDamageCalc3` = 40/60/90 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Ziggs19_Attack`: launch 0.4 s (12 ticks); animation length 1.001 s (30.03 ticks); release at base AS 0.5709 s (17.13 ticks)
- Attack projectile: DA_Ziggs19_AutoAttackProjectile (TFTFixedSpeedWithHeightMovement)
- Spell `GA_Ziggs19_Spell` (chrono `CD_Ziggs19_CastAnim`): cast ends 0.8 s (24 ticks), next attack can start 0.8333 s (25 ticks), mana lock removed 0.8 s (24 ticks); **script reads attack speed**; ended by `FinishCasting via OnEventBegin:CD_Ziggs19_CastAnim:Unlock`
  - notes: rate from unresolved CallFunc_PlayChronoWithTargetActor_Speed_ImplicitCast ×1; projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Ziggs19_Attack` | CD_Ziggs19_Attack | 1.001 | LaunchAttackVariant1 0.4, LaunchAttackVariant2 0.4, Unlock 0.7 |
| `CD_Ziggs19_CastAnim` | CD_Ziggs19_CastAnim | 0.8002 | Unlock 0.779 |
| `CD_Ziggs19_HyperpopHypemeter_Intro` | CD_Ziggs19_HyperpopHypemeter_Intro | 1 | StartHype 0.95 |
| `CD_Ziggs19_HyperpopHypemeter_Outro` | CD_Ziggs19_HyperpopHypemeter_Outro | 1.0312 | EndOutro 0.9791 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_Ziggs19_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Ziggs19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Ziggs19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Ziggs19_LaunchProjectileAttack.txt, GA_Ziggs19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Ziggs19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: GA_Ziggs19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Ziggs19_Spell.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

- row InitialDamage: 180 / 270 / 405 -> 155 / 235 / 355
- row SecondaryDamageAP: 80 / 120 / 180 -> 70 / 105 / 160
- ability text changed

<!-- AUTO END -->

## Status

- Worksheet status: **implemented 2026-11-17** (`set19champs.Ziggs`, D1; tests `test_ziggs.py`)
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | **consistent**: 500 HP, 0/50 mana, AD 10, AS 0.70, armor/MR 25, range 4 Hex | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicMarksman | **consistent**: +10 per release, no regen | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | VOD6: released 16 ticks after combat start (Guinsoo's first stack 1 s in marks it), engine 15 (T10's +1) | E2, E4 |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.4 s (12 ticks) | **consistent**: 18 ticks at base AS (0.4 s stretched to the 1.43 s period, G2), in the cast-to-release gap | E2 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | **confirmed** G20 (T = 0.7, shrinks above AS 1.43): 8 ticks after a cast at AS 2.0-2.3, not 12; attacks 12 ticks apart at AS 2.4 | E4 |
| Q6 | Projectile travel time (ranged only) | not fixed speed | attacks: not measured (minion targets moved, flights 13-24 frames); bomb: lands ~10 frames after it is first seen, target ~2 hexes away | E2, E3 |
| Q7 | Cast time: cast start to the next attack starting | 0.8333 s (25 ticks) | **consistent**: cast to next release 44 ticks = 25 + 18 + T10's tick | E2 |
| Q8 | Does the cast time scale with attack speed? | script reads AS | **confirmed**, with the 2x cap: cast to next release 28 / 23 / 22 ticks at AS 1.23 / 2.02 / 2.31, engine 28 / 22 / 22 (unscaled 38 / 34 / 33; uncapped 19 / 17); G5's tick after the cast end doesn't scale (D2) | E4, D2 |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.8 s (24 ticks) | **consistent** (the panel shows 0 through the lock; the next mana is the next release) | E2 |
| Q10 | Does the mana lock scale with attack speed? | script reads AS | predicted: same rate as the cast (D1); the panel shows 0 until the next release, so not seen | script |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | one simulated attack when the bomb fires (D1): on-attack items hear it (Titan's Resolve stack, G11); role mana falls inside the mana lock | G11 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | cancels Combat.Attacking (T4); the rhythm restarts with a fresh attack after the lock | E2 |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | **confirmed**: attack 9 physical + 36 magic on the same hit, bomb 163 on the target + 72 on an adjacent minion (all four fit 10, 40, 180, 80 against minion armor = MR = 10, shown rounded down) | E3 |
| Q14 | Passives and other mechanics that need modelling | see ability text | passive implemented (D1); Arcanist implemented (B16); Hyperpop's AS (B23; Hype doesn't change combat stats) | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-17 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 0:16 (planning, round 1-1) | 60 | inspection panel | 1★, no items, 500 HP, 0/50 mana, AD 10, AS 0.70, armor/MR 25, 4 Hex; Arcanist, Hyperpop, Swiftstriker 1/2 (inactive) | as built | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 f1133-1963 (`tools/vod_text_changes.py`, mana) | 60 | releases (+10 mana) and the cast | 10, 20, 30, 40 at f1133, 1217, 1301, 1378; 0/50 (cast) at f1476; 10, 20, 30, 40 at f1564, 1648, 1734, 1820 (44, 86, 129, 172 ticks after the cast). Before the cast the attacks' hits are regular (f1314, 1402, 1488: 88, 86 frames) but the mana steps aren't (84, 84, 77, ~98): the minion target moves, so flight times differ; left out | after the cast the engine gives 43, 86, 129, 172: the first is T10's open tick, the rest exact | Q2, Q4, Q7, Q9, Q12 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 f1300-1520 (board, every 4-8 frames) | 60 | damage numbers | each attack 9 (orange) + 36 (blue) on one hit; the bomb (seen above him at f1500, on the target at f1512) 163 on the target and 72 on the minion next to it at f1516 | minion armor = MR = 10, numbers rounded down: 10 x 100/110 = 9.1, 40 -> 36.4, 180 -> 163.6, 80 -> 72.7 | Q6, Q13 |
| E4 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f18780-19900 (round 1-7; VOD6 = `…PBE_11-18-2026_18-40-41-766.mp4`), mana and AS text | 60 | releases (+10), casts (bar to 0), AS | 1 star with two Guinsoo's Rageblades: AS 0.84, then +0.098 every 60 frames from f18845 (0.70 x (1.2 + 0.14 n)), to 2.51; combat start f18785 (the first stack 1 s in). Releases (ticks after combat start) 16, 50, 81, 110, 136 (fills: cast), 164, 187, 209, 229, 249.5 (cast), 299.5 (a 50-tick pause), ..., 378.5 (cast), 401.5, ..., 456.5 (cast), 478.5, 491.5, 503.5, 515.5, 527.5 (cast) | from the filling release to the next: 28 / 23 / 22 ticks at AS 1.23 / 2.02 / 2.31; engine (D2) 28 / 22 / 22; the first release 16 (engine 15) | Q3, Q5, Q8 |

## Decisions and notes

- 2026-11-17, D1 (implemented, `set19champs.Ziggs`):
  - **Passive (GE_Ziggs19_AutoAttack):** every attack applies two damages on the same hit: BasicAttackDamage
    physical (attack crit) and MagicDamageCalc3 = AADamageAP x AP magic (AppliesOnSpell; crits only with
    Precision).
  - **Spell (GA_Ziggs19_Spell):** CD_Ziggs19_CastAnim plays at rate FClamp(AttackSpeed / base AttackSpeed, 1, 2)
    (0x4c1-0x689), so the cast lock (0.8333 s), mana lock (0.8 s) and the MainBomb spawn (0.3183 s) all divide by
    it (`Timing.lock_speed_clamp`). The bomb (1900 units/s) applies MagicDamageCalc1 (InitialDamage x AP) to the
    target and MagicDamageCalc2 (SecondaryDamageAP x AP) to the other enemies within 1 hex of it on arrival.
  - **Simulated attack:** the bomb's first OnFired applies GE_SimulateLaunchAttack, which sends
    Combat.Event.LaunchAttack.SimulateTriggersOnly (GA_SimulateLaunchAttack). Not modelled: no listed item reacts
    to attacks, and role mana from it (if the native mana handler hears it) would fall inside the mana lock.
  - **Assumed:** the bomb flies his attack range (4 hexes); the splash hits the enemies next to the target on the
    dummy layout (`layout.py`, default one). MiniBombs / FindMiniBombTargets in the script are never called.
- 2026-11-18, Day 1 PBE patch notes, confirmed in the client build rls-19.1.0.5986094 (read from an FModel raw export, B34; it replaced the patch-notes stand-in, B33): InitialDamage 180/270/405 -> 155/235/355, SecondaryDamageAP 80/120/180 -> 70/105/160. Its timing is unchanged from rls-19.1.0.5973071.

- 2026-11-18, D2 (VOD6 E4): the cast chrono plays at FClamp(AS / base AS, 1, 2) as D1 says, and its end (0.8 s)
  is what scales: the cast lock = 0.8 s / rate + G5's one tick (the next attack starts the tick after the cast
  ends), not 0.8333 s / rate (`Timing.scaled_locks`). At 2x: 13 ticks, not 12. The mana lock 0.8 s / rate.
