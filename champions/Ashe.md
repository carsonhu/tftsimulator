# Ashe (2-cost AttackMarksman) · `DA_Ashe19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Beach Pop, Swiftstriker
- **HP** 550 / 990 / 1782 · **AD** 50 / 75 / 112.5 · **AS** 0.75 · **Range** 5 · **Armor** 30 · **MR** 30 · **Mana** 20 / 60
- **Unlock**: A Beach Pop Champion with 2 items.

### Ability: Feelin' Shot Shot Shot

> The next 6 attacks have 0.3 + 0.2 × AP Attack Speed and are replaced with flurries of 3 arrows. Each arrow deals 33/50/75 × AD physical damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 50 | 75 | 112.5 |
| SpellASBase | 0.3 | 0.3 | 0.3 |
| NumFlurryAttacks | 6 | 6 | 6 |
| ArrowsPerFlurry | 3 | 3 | 3 |
| ArrowDamageAD | 33 | 50 | 75 |
| SpellASAP | 0.2 | 0.2 | 0.2 |
| OnHitEffectivenessPerFlurryArrow | 0.6 | 0.6 | 0.6 |

Formulas (as stored; AD and AP are multipliers):

- `AttackSpeedCalc1` = 0.3 + 0.2 × AP
- `PhysicalDamageCalc1` = 33/50/75 × AD

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Ashe19_Attack_new`: launch 0.2971 s (8.91 ticks); animation length 2.1333 s (64 ticks); release at base AS 0.2971 s (8.91 ticks)
- Attack projectile: DA_Ashe19_AutoAttackProjectile, speed 2500 units/s
- Spell `GA_Ashe19_Spell` (chrono `CD_Ashe19_CastAnim`): cast ends 0.3333 s (10 ticks), next attack can start 0.3667 s (11 ticks), mana lock removed –; **script reads attack speed**; ended by `FinishCasting via OnChronoStopped:CD_Ashe19_CastAnim:None`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Ashe19_Attack_new` | Chronos | 2.1333 | CustomLaunchAttack1 0, LaunchAttack 0.2971, Unlock 0.4, Unlock 0.5 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Ashe19_Spell`, `GA_ShopEvents`, `GA_Ashe19_EmpoweredAttack`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Ashe19_Spell.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: Abilities/GA_Ashe19_EmpoweredAttack.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Ashe19_EmpoweredAttack.txt, Abilities/GA_Ashe19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Ashe19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Ashe19_Spell.txt

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Ashe`, D1); panel, mana and the first cast's rhythm checked
  against VOD5. Beach Pop is not implemented yet (it comes with Zoe).
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed with her items (1★) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackMarksman | confirmed: 10 per attack (no role regen; Tear's 1/s) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2971 s (8.91 ticks) | refuted at her AS: her modules have PlayRateScalingThreshold 1.0 and play at the attack period (G20): first attack 5.5 ticks after combat start at AS 0.86, engine 5 | E2 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | shortened (G20) | E2 |
| Q6 | Projectile travel time (ranged only) | speed 2500 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 0.3667 s (11 ticks) | consistent: the 6 flurries' lock lifts 123.5 ticks after the filling attack (engine 125) | E2 |
| Q8 | Does the cast time scale with attack speed? | script reads AS | predicted: CT_Ashe19_ASToCastSpeed at her AS (0.3333 s up to 1 AS, 0.15 s at 5 AS), not the G7 ratio | D1 |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | the tick after the 6th flurry (script); the first cast consistent (1.5 ticks), the second 13.5 ticks longer in the clip than the engine (open) | E2 |
| Q10 | Does the mana lock scale with attack speed? | script reads AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | predicted: 0; the 6 flurries are attack launches (LaunchAttack.Custom.1) whose mana the lock eats | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read: D1); no damage number read yet | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | the arrows' on-hit effects at 0.6 (I11); Swiftstriker implemented; Beach Pop not yet | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD5 (`…PBE_11-18-2026_0-57-11-500.mp4`, session folder 0-33-59-673, 60 fps), the owner's
PBE recording in the score mode, build `rls-19.1.0.5973071`; Ashe 1★, round 1-4, combat start f13727 (Quicksilver's first
+3% at f13787; her regen display also steps at exactly 1, 2, 3 s, consistent with T7). Ticks count from combat start.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 3:52 (f13920) | 60 | inspection panel | 550/550, 53/60, 1/s; AD 50, AS 0.93 (3 Quicksilver stacks), crit 45%, armor 30, MR 50, range 5; Tear of the Goddess, Quicksilver; Beach Pop 2/3 and Swiftstriker 1/2 inactive | 0.75 x (1.15 + 0.09), 25 + 20 crit, 30 + 20 MR: as built | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 f13738-15020 (`tools/vod_text_changes.py`, mana and as) | 60 | mana text, AS | +10 at 5.5, 41, 74.5, 108 (fills; AS 0.93 -> 1.30 on the same frame: the empower, +50%); 3 (the overflow) at 231.5 with AS back to 1.02 on the same frame (the empower and the lock end together); +10 at 257, 285, 313.5, 341.5, 368.5, 395 (fills; AS 1.15 -> 1.53); overflow 9 at 517.5 (122.5 after the fill), +10 at 539.5, 563.5, 587 | engine (Quicksilver, Tear's regen): attacks 5, 40, 73, 106; flurries 119 ... 230 (cast lock 11, then ~22 ticks apart), lock lifted 125 after the fill; the first normal attack 148 after it (clip 149), the next 30 (28); 6 more attacks to the second fill, as the clip. The second empowered phase: engine 109 ticks to the lift (flurries ~19 apart at AS 1.53-1.60, which the panel showed too), the clip 122.5: open, perhaps a retarget (enemies die in this mode) | Q2, Q4, Q5, Q7, Q9 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Ashe`):
  - **Cast (GA_Ashe19_Spell):** CD_Ashe19_CastAnim for a fixed duration, CT_Ashe19_ASToCastSpeed ASToCastTime at her
    AS when the cast starts (read before the empower); cast lock = that + 1 tick (G7's AS ratio is not applied: the
    script reads AS only through the curve). Mana lock and GE_Ashe19_Empowered (CustomAttack.1 tag, AttackSpeed
    MultiplyAdditive 0.3 + 0.2 x AP, a +50% bonus at AP 1 as VOD5 shows). After the 6th Custom.1 launch, one tick
    later, both end.
  - **Attacks:** her modules play at the attack period (PlayRateScalingThreshold 1.0, G20): normal attacks release
    at 0.2971 s of 2.1333 s, flurries at 0 s. A flurry fires no attack projectile: 3 arrows (CD_Ashe19_EmpoweredMis:
    OnHitArrow at 0 s, NoOnHitArrow at 0.075 and 0.15 s, 2100 units/s), each 33/50/75 x AD physical, on-hit and
    on-spell (the first also IsAttack), crit only with Precision, on-hit effects at 0.6 (I11).
  - The build's champion entries now carry the other curve tables of the champion's folder (`tables`;
    `tools/import_build.py`), read with `BuildChampion.table_value`.

