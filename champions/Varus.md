# Varus (1-cost AttackCaster) · `DA_Varus19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6018196.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6018196.Set19.Shipping.pbe`

- **Role** AttackCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Rock, Encore
- **HP** 500 / 900 / 1620 · **AD** 35 / 67.5 / 101.25 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 30 / 70

### Ability: One Thousand Arrows

> Fire a hail of arrows, dealing 30/45/70 × AP + 245/370/590 × AD physical damage to the target and 0.5 × PhysicalDamageCalc1 damage to adjacent enemies. 20% Slow them for 4 seconds.
> 
> Slow: Reduce Attack Speed

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 35 | 67.5 | 101.25 |
| DamageAD | 245 | 370 | 590 |
| SlowLevel | 20 | 20 | 20 |
| DamageAP | 30 | 45 | 70 |
| AOEDamagePercent | 0.5 | 0.5 | 0.5 |
| SlowDuration | 4 | 4 | 4 |
| AOEHexRange | 1 | 1 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 30/45/70 × AP + 245/370/590 × AD
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

### Changed since `rls-19.1.0.6011486.Set19.Shipping.pbe`

- row DamageAD: 245 / 370 / 550 -> 245 / 370 / 590
- ability text changed

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-17); open: T10 (+1 tick on fresh attacks), damage numbers
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | **consistent**: panel 500 HP, mana 30/70 before combat (ManaStarting 30), AS 0.77 with Guinsoo's base 10% (0.70 x 1.1) | E5 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackCaster | **7 / attack, paid at the release; regen 2 / s** (8 / s with Blue Buff's 6) | E2, E4, E5, E6 |
| Q3 | First attack at combat start: when does it land? | G3 | first attack's mana 8 ticks after combat start; engine 7 (G19 windup from a fresh attack at tick 0); the +1 is T10 (open) | E5, E6 |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.425 s (12.75 ticks) | **refuted for the unscaled launch**: release ~7-8 ticks, not 13. His attack modules lack `bUseRateScalingThreshold` (only Varus and Yorick among shop units), so the animation plays at the attack period: 0.425 x period / 2.5 (G19) | E6 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | **shortened with AS** (G19): consistent at AS 0.77 (combat start), 0.87 and 1.11 (after casts), each within 1-1.5 ticks | E6, E7 |
| Q6 | Projectile travel time (ranged only) | speed 2000 | spell missiles 1800 (arc 400), attack 2000; travel not measured. Owner (2026-11-17): travel depends on the target's distance, 4 hexes for most ranged fights; a VOD can estimate the landing (G4) |  |
| Q7 | Cast time: cast start to the next attack starting | 1.0333 s (31 ticks) | **consistent** with cast lock 31 + G19 windup (+1 tick, T10): after-cast +7 at 38 and 37.5 ticks (predicted 37, 36); the first VOD's +37 frames fits 31 + 5 (+1) | E4, E7 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1 s (30 ticks) | **confirmed**: overflow shown +31 ticks after casts (first VOD +31 frames at 30 fps; second VOD +62/63 frames at 60 fps) | E3, E7 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | the filling attack released ~1 frame before the cast, so no attack was in progress | E2 |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | implemented from the script (D1): HailMain at Fire 0.4278 s, primary to the target + secondary (AOEDamagePercent) to adjacent; EncoreHailMain at 0.6286 s x Encore effectiveness; physical, spell crit with Precision. No damage evidence yet | script, build |
| Q14 | Passives and other mechanics that need modelling | see ability text | slow (20% AS, 4 s): not modelled, dummies never attack | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-17 | D1 |

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
| E5 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 f15340-15390 | 60 | mana text at combat start (Blue Buff + Guinsoo's) | 30/70 until f15364; 40 at f15365 (Blue Buff: combat start); 42 f15373 (regen); 49 f15381 (attack +7); 51 f15387 | first attack mana +16 frames = 8 ticks; first regen +8 frames = 4 ticks (G17) | Q1, Q2, Q3 |
| E6 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 f15362-15385 (zoomed, every frame) | 60 | the first attack | idle to f15366; bow raised f15366-15373; arrow streak leaves the bow f15381-15382 with the +7 | release ~8 ticks after combat start at AS 0.77 (unscaled prediction 13; G19 7) | Q3, Q4, Q5 |
| E7 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 casts f15477, f15808, f16121 | 60 | mana text after casts | overflow shows +62/63 frames (31 ticks); first attack +7 at +76 frames (38 ticks, AS 0.87) and +75 (37.5, AS 1.11) | mana lock 31 (30 + display lag); cast lock 31 + G19 windup 6 / 5, +1 (T10) | Q7, Q9 |
| E8 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 casts at combat-start-relative ticks 56, 221.5, 378 | 60 | cast rhythm with Blue Buff + Guinsoo's | gaps 165.5, 156.5 ticks | engine (test_varus.py): 54, 219, 376, gaps 165, 157: match to half a tick; the ~2-tick offset is T10 + G17 | all |

## Decisions and notes

- 2026-11-17: Varus pays at the release (E2, E4, seen on screen). Open: his cast lock (E4 suggests ~24 ticks
  against a predicted 31, while the mana lock matched its prediction): needs more casts, ideally at base AS.
- 2026-11-17, second VOD (`…PBE_11-17-2026_16-35-16-966.mp4`, 60 fps, rls-19.1.0.5973071): Varus 1★ with Blue Buff
  and Guinsoo's (AS 0.77 at combat start). Combat start f15365 (mana text 30 → 40, Blue Buff); his first attack's
  +7 shows at f15381 = **8 ticks** after combat start; the client predicts 13 (LaunchAttack 0.425, not stretched
  at period 1.30 s < attack length 2.5). With the first VOD's post-cast arrow (E4: ~7 ticks earlier than predicted)
  that is two sightings of his release coming ~5-7 ticks before LaunchAttack. A release scaled to the attack period
  (0.425 x 1.30 / 2.5 = 0.22 s ≈ 7 ticks) would fit both, but Neeko's attacks fit the unscaled 13 ticks (Neeko E3,
  E4), so no rule is changed. Resolved the same day: the zoom (E6) shows the arrow at ~8 ticks; the
  attack-module flag explains it (G19, D1).
- D1 2026-11-17: implemented as `set19champs.Varus` (tests `test_varus.py`, local). Script `GA_Varus19_Spell`: the
  cast chrono spawns `HailMain` at its Fire point (0.4278 s) and, in its Encore group (Encore tag only),
  `EncoreHailMain` at 0.6286 s (spawn times in the build, P7); `Hail` missiles are visual. Arrival of HailMain
  (0x111b -> 0x960) applies `GE_Varus19_PrimaryDamage` (PhysicalDamageCalc1 = DamageAP x AP + DamageAD x AD) to the
  target and `GE_Varus19_SecondaryDamage` (Calc2 = AOEDamagePercent x Calc1) to enemies within AOEHexRange 1;
  EncoreHailMain (0x121f -> 0x2e4) the same x RecastEffectiveness. Physical, RollIfCanSpellCrit. AD in the calc
  is the AttackDamage attribute (1.0 + bonus AD, like AP), not his 35 attack damage: owner, 2026-11-17 ("the AD in
  his damage formula is only bonus AD": items' AD scales it, his base attack damage doesn't); the splash hits the enemies within AOEHexRange (1) of
  the target on the dummy layout (`layout.py`, default one); straight-line missile flight (G4). The slow is not modelled (dummies never attack).
