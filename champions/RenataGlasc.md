# Renata Glasc (2-cost MagicCaster) · `DA_RenataGlasc19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6037882.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6037882.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Classical, Choreographer
- **HP** 550 / 990 / 1782 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 45

### Ability: Hostile Measures

> Fire a musical bar at the target, applying 2 stacks of Toxin. Toxin stacks deal 160/240/580 × AP magic damage over 15 seconds. Additionally, apply 1 stack of Toxin to 2 nearby enemies, prioritizing unpoisoned enemies. 
> 
> Enemies are Captivated for 3 seconds upon Toxin application, increased to 6 seconds if their star level is less than Renata's.
> 
> Captivated enemies grant bonuses to Classical champions.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| SecondaryTargetSpellDamage | 0 | 0 | 0 |
| PrimaryTargetSpellDamage | 0 | 0 | 0 |
| StunDuration | 0 | 0 | 0 |
| NumSecondaryTargets | 2 | 2 | 2 |
| PrimaryTargetStacks | 2 | 2 | 2 |
| SecondaryTargetStacks | 1 | 1 | 1 |
| ToxinDamageAP | 160 | 240 | 580 |
| TickRate | 0.25 | 0.25 | 0.25 |
| ToxinDuration | 15 | 15 | 15 |
| CaptivateDurationShort | 3 | 3 | 3 |
| CaptivateDurationLong | 6 | 6 | 6 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 0 × AP
- `MagicDamageCalc2` = 0 × AP
- `MagicDamageCalc3` = 160/240/580 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_RenataGlasc19_Attack`: launch 0.3307 s (9.92 ticks); animation length 2.3333 s (70 ticks); release at base AS 0.3307 s (9.92 ticks)
- Attack projectile: DA_RenataGlasc19_AutoAttackProjectile, speed 1800 units/s
- Spell `GA_RenataGlasc19_Spell` (chrono `CD_RenataGlasc19_Spell`): cast ends 3.6667 s (110 ticks), next attack can start 3.7 s (111 ticks), mana lock removed 3.6667 s (110 ticks); ended by `FinishCasting via OnEventBegin:CD_RenataGlasc19_SpellEnd:Unlock`
  - notes: curve CT_RenataGlasc19.NumSecondaryTargets input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.ToxinDuration input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.StunDuration input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.PrimaryTargetStacks input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.SecondaryTargetStacks input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.CaptivateDurationShort input unresolved (self.RenataStarLevel), used star 2 ×1; curve CT_RenataGlasc19.CaptivateDurationLong input unresolved (self.RenataStarLevel), used star 2 ×1; projectile (hit time depends on travel) ×6

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_RenataGlasc19_Attack` | CD_RenataGlasc19_Attack | 2.3333 | LaunchAttack 0.3307, Unlock 0.9333 |
| `CD_RenataGlasc19_Spell` | CD_RenataGlasc19_Spell | 1.2021 | Default 0, LaunchChains 0.1974, Waiting 0.9328 |
| `CD_RenataGlasc19_SpellEnd` | CD_RenataGlasc19_SpellEnd | 0.6804 | Unlock 0.6578 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_RenataGlasc19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_RenataGlasc19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_RenataGlasc19_Spell.txt

### Changed since `rls-19.1.0.6028987.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.RenataGlasc`, D1); panel and the cast's locks checked
  against VOD2
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed with her items (1★) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster | confirmed: 7 per attack, 2/s (+6 Blue Buff) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3307 s (9.92 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1800 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 3.7 s (111 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 3.6667 s (110 ticks) | **refuted** (the build's 3.67 s is the 3 s fallback): the chain's hit + SpellEnd's Unlock, 41 ticks at 4 hexes; VOD2's overflow at 42 and 41.5 after the filling regen step (engine 42) | E2, D1 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | predicted: 0 (no GE_SimulateLaunchAttack) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read: D1); the DOT spread over its 15 s: owner 2026-11-18 (the tooltip is right) | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | her Captivates feed Classical (B28); Choreographer (B30) implemented | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD2 (`…PBE_11-17-2026_16-35-16-966.mp4`, 60 fps), the owner's PBE recording, build
`rls-19.1.0.5973071`; Renata Glasc 1★, round 1-9, combat start f22888 (Blue Buff's +10).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5973071 | VOD2 6:21 (f22880), ability tooltip | 60 | inspection panel | 550/550, 0/45, 8/s; AD 35, AP 25%, AS 0.83, crit 25%, range 4; Guinsoo's Rageblade, Blue Buff; Classical and Choreographer 1/2 (inactive). Tooltip: Toxin 200 = 160 x 1.25 AP over 15 s | as built | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5973071 | VOD2 f22888-23387 (`tools/vod_text_changes.py`, mana) | 60 | mana text | 10 at combat start; +2 regen steps from 2 ticks in (G17's phase), +7 attacks; two casts filled by regen (f23043, f23298); the overflow 1 shown 84 and 83 frames later (42, 41.5 ticks); the next attack's mana 53.5 ticks after the fill | engine (Guinsoo's, Blue Buff): lock 41 from the cast = 42 after the fill; the next attack 53 after it | Q2, Q9 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.RenataGlasc`):
  - **Spell (GA_RenataGlasc19_Spell):** mana lock; at LaunchChains (0.1974 s) the chain (1800 units/s) to her target
    and a missile (spline, 1800) to each of 2 other enemies, the unpoisoned first. The chain's hit: 2 Toxin
    applications and a Captivate (6 s if the enemy's star level <= hers, else 3 s); CD_RenataGlasc19_SpellEnd, whose
    Unlock (0.6578 s) ends the cast and the mana lock. A missile's hit: 1 Toxin and a Captivate. The build's 3.67 s
    spell timeline is the 3 s WaitDelay fallback for a chain that never lands.
  - **Toxin (GE_RenataGlasc19_ToxinDamage):** its own 15 s instance per application, a tick every 0.25 s; the GE
    applies MagicDamageCalc3 (160/240/580 x AP) each period, which would be 60x the tooltip; the tooltip is right (owner,
    2026-11-18): 160 x AP spread over the 60 ticks. The first tick on application (open). Magic, DOT, on-spell, crit only
    with Precision.
- 2026-11-18, Day 1 PBE patch notes, confirmed in the client build rls-19.1.0.5986094 (read from an FModel raw export, B34; it replaced the patch-notes stand-in, B33): CaptivateDurationLong 6 -> 9, and the long Captivate now needs a target below her star level (was: at or below; GA_RenataGlasc19_Spell LessEqual_IntInt -> Less_IntInt at 0x183c and 0x256a in 5986094): a 1-star Renata on the 1-star dummies now Captivates for the short 3 s. Its timing is unchanged from rls-19.1.0.5973071.
