# Aurora (4-cost MagicCaster) · `DA_Aurora19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Ionic Spark, Renegade
- **HP** 850 / 1530 / 2754 · **AD** 35 / 67.5 / 101.25 · **AS** 0.75 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 0 / 60

### Ability: Between Worlds Apart

> Blink away and fire a blast through the best line. The blast deals 300/450/2000 × AP magic damage to the 2 highest Health enemies, and 90/135/1500 × AP magic damage to the rest. Then, blink back.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 35 | 67.5 | 101.25 |
| PrimaryDamageAP | 300 | 450 | 2000 |
| AOEDamageAP | 90 | 135 | 1500 |
| MaximumHexMove | 10 | 10 | 10 |
| MinimumHexMove | 0 | 0 | 0 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 90/135/1500 × AP
- `MagicDamageCalc2` = 300/450/2000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Aurora19_Attack`: launch 0.3348 s (10.04 ticks), variants 0.3348, 0.3365; animation length 2.6 s (78 ticks); release at base AS 0.3348 s (10.04 ticks)
- Attack projectile: DA_Aurora19_AutoAttackProjectile, speed 1250 units/s
- Spell `GA_Aurora19_Spell` (chrono `CD_Aurora19_CastAnim`): cast ends 2.0333 s (61 ticks), next attack can start 2.0667 s (62 ticks), mana lock removed 2.0333 s (61 ticks); ended by `FinishCasting via OnEventBegin:CD_Aurora19_CastAnim:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Aurora19_Attack` | CD_Aurora19_Attack | 2.6 | LaunchAttack 0.3348, LaunchAttack 0.3365, Unlock 1.04 |
| `CD_Aurora19_CastAnim` | CD_Aurora19_CastAnim | 2.0739 | Default 0, Untargetable1 0.4358, FadeOut 0.4985, Retargetable1 0.5545, Mark 0.6919, Damage 1.0738, ResetChronoTarget 1.3784, Untargetable2 1.6633, BackHome 1.7619, Retargetable2 1.7711, Unlock 2.0323 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Aurora19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Aurora19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Aurora19_Spell.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-21, `set19champs.Aurora`, D1); stats, attack rhythm, the cast, the mana
  lock and the next attack checked on VOD8 at 5-6 (E1-E3)
- Keep in the simulator: **yes** (owner, 2026-11-21: VOD8 recorded for her)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (850 / 850, 0 / 60, AD 35, 4 hexes; AS 0.79 = 0.75 x 1.06 with Aphelios's Heartsteel bonus; armor / MR 48 from the board's other bonuses) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster: 7 per attack, 2 / s | confirmed (+7 steps 37-38 ticks apart; 2 / s on the panel) | E2 |
| Q3 | First attack at combat start: when does it land? | G3: released on tick 10 | engine 1 tick early (VOD 11 ticks after the timer's flip: T10's +1) | E2 |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3348 s (10.04 ticks); SequentialAttack's two modules 0.3348 / 0.3365 s, the same tick | consistent | E2 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 (bUseRateScalingThreshold, no threshold) | not seen (AS 0.795 the whole fight) | E2 |
| Q6 | Projectile travel time (ranged only) | speed 1250 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 'Unlock' 2.0323 s -> tick 61, + 1 = 62 ticks | confirmed to T10 (filling attack to next attack 74.5 and 73.5 ticks; engine 73) | E3 |
| Q8 | Does the cast time scale with attack speed? | no (CastAnim at speed 1) | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | the Unlock tick: 61 ticks | confirmed (the banked 5 shows 62.5 ticks after the filling attack; engine unlocks 62 after it) | E3 |
| Q10 | Does the mana lock scale with attack speed? | no | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 (no GE_SimulateLaunchAttack) | predicted | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | PrimaryDamage (MagicDamageCalc2) on the first 2 targets, once on a lone one (owner, 2026-11-21); AOEDamage (MagicDamageCalc1) on the rest; at 'Damage' 1.0738 s | timing consistent (omnivamp heals at the predicted tick, E3); amounts predicted | D1, E3 |
| Q14 | Passives and other mechanics that need modelling | blink (untargetable, deprioritised): nothing against dummies | not applicable | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-21 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD8 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-21-2026_12-18-17-802/` `…PBE_11-21-2026_13-2-9-650.mp4`
(owner's game, 2026-11-21, 60 fps). Client rls-19.1.0.6013636 (not exported; owner: only a Graves crash fix), so
6011486 is assumed. Aurora 1 star, no items; Heartsteel (3) on the board (Aphelios fielded: AS x 1.06), Ionic Spark
and Renegade inactive (1 member each). Mana and AS from `tools/vod_text_changes.py --field mana` / `--field as`.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 30:46-30:54 (5-6 planning) | 60 | inspection panel, ability tooltip | 850 / 850, 0 / 60, 2 / s, Back, 4 Hex; AD 35, bonus AD 0%, AP 0%, armor 48, MR 48, AS 0.79, crit 25%, 23% (red fang: omnivamp, from the board); tooltip Damage 300, Secondary 90 (300 / 450 / 2000, 90 / 135 / 1500) | engine with Heartsteel (3), Aphelios ticked: AS 0.795 (float32 0.79499996 shows 0.79); AP 1.0 (`test_vod8_5_6_panel`) | Q1, Q13 |
| E2 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 f112267-112754 (5-6) | 60 | round timer, mana text | timer flips to 30 at f112267; +7 at f112289, 112363, 112439, 112528, 112602, 112678, 112754 (11, 48, 86, 130.5, 167.5, 205.5, 243.5 ticks in; the 86 -> 130.5 gap a target change); regen +1 steps between; AS 0.79 throughout | engine (`test_vod8_5_6_casts`): releases at 10, 48, 85, then 37-38 apart; VOD's first 1 tick later (T10). First displayed regen +1 13 ticks in (G17: first step ~5.5 ticks) | Q2-Q5 |
| E3 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 f112742-113687 (5-6) | 60 | mana text, HP text | cast 1: 58 -> 0 at f112754 (+7 fills: 65, 5 banked); 5 shows at f112879 (lock end); +7 at f112903; cast 2: 53 -> 0 at f113280 (exactly 60, nothing banked); +7 at f113427; HP jumps +94 at f112823 and +63 at f113347 (omnivamp on her blast, 23%) | engine (`test_vod8_5_6_casts`, `test_blast_lands_at_damage`): cast the tick after the filling attack; unlocked 62 ticks after it (VOD 62.5); next release 73 after (VOD 74.5, 73.5: T10); 'Damage' 33 ticks after the cast = 68 frames after the fill (VOD heals at +69 and +67 frames) | Q7, Q9, Q13 |

## Decisions and notes

- 2026-11-21, D1 (implemented, `set19champs.Aurora`; its docstring cites the script):
  - **Attack:** CD_Aurora19_Attack's AttackGroup plays SequentialAttack (two modules, LaunchAttack 0.3348 / 0.3365 s,
    both 2.6 s with bUseRateScalingThreshold and no threshold: G2); the snapshot's attack_launch 0.3348 is the first,
    and the two release on the same tick (checked against the FModel export: no P14 / P15 gap).
  - **Cast (GA_Aurora19_Spell):** blink hex = the first of the safest hexes within MaximumHexMove (10) whose best line
    (LineLength 2600 x LineWidth 440, script defaults typed: P15 b) holds the most enemies; CD_Aurora19_CastAnim there,
    mana lock. 'Mark' 0.6919 s: the enemies in the line (her target when none) sorted by Health, highest first:
    PrimaryTarget the first, HighestHP the next, or PrimaryTarget again when alone. 'Damage' 1.0738 s:
    GE_Aurora19_PrimaryDamage (MagicDamageCalc2 = PrimaryDamageAP x AP) on PrimaryTarget and on HighestHP, so twice on
    a lone enemy; GE_Aurora19_AOEDamage (MagicDamageCalc1 = AOEDamageAP x AP) on every other enemy in the line. Both
    magic, AppliesOnSpell, AOE, crit only with Precision (FModel export). 'Unlock' 2.0323 s: mana lock removed,
    FinishCasting; cast lock = the Unlock tick + 1 (as Yasuo, Lux).
  - **Simulated:** the line from her own hex; LineWidth 440 holds every page target (the target's neighbours stand
    186 units off a hex axis through it), so no blink hex does better.
  - **Owner's ruling (2026-11-21), over the script reading above:** the first 2 targets (placement order, the target
    first) take PrimaryDamage and the rest AOEDamage; a lone enemy takes PrimaryDamage once, not twice. No Health sort:
    the dummies track no Health. Targets default to 4 (`TARGETS_DEFAULT`).
  - **Not simulated:** the blink's untargetability and Combat.Status.DeprioritizedForAttacks (dummies never attack).
  - Renegade (her trait) gives Precision, so her blast crits with it (traits/renegade.py); Ionic Spark's letters and
    gift as the trait already does.
  - Open questions: docs/OPEN-QUESTIONS.md 7ac.
