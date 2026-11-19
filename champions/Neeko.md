# Neeko (1-cost MagicCaster) · `DA_Neeko19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5986094.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5986094.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 1, pool 30; traits: K/DA, Encore, Prodigy
- **HP** 500 / 900 / 1620 · **AD** 30 / 45 / 67.5 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 0 / 40

### Ability: K/DA Fan Club

> Convene the K/DA fan club, throwing 3 confetti streams at target that each deal 75/115/175 × AP magic damage. If they kill, permanently gain 1% Ability Power.
> 
> Current Bonus: ⟨live⟩ Ability Power

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| APGain | 0.01 | 0.01 | 0.01 |
| DamageAP | 75 | 115 | 175 |
| NumProjectiles | 3 | 3 | 3 |
| KillBuffer | 0.2 | 0.2 | 0.2 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 75/115/175 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Neeko19_Attack`: launch 0.4219 s (12.66 ticks), variants 0.4219, 0.4443; animation length 3.1 s (93 ticks); release at base AS 0.4219 s (12.66 ticks)
- Attack projectile: DA_Neeko19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Neeko19_SpellUsingVFX` (chrono `CD_Neeko19_CastAnimWithClone`): cast ends 0.8 s (24 ticks), next attack can start 0.8333 s (25 ticks), mana lock removed 0.8 s (24 ticks); ended by `FinishCasting via OnEventBegin:CD_Neeko19_CastAnimWithClone:Unlock`
  - notes: curve CT_Encore19.RecastEffectiveness input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast), used star 2 ×1; projectile (hit time depends on travel) ×18

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Neeko19_Attack` | Chronos | 3.1 | LaunchAttack 0.4219, LaunchAttack 0.4443, Unlock 1.24 |
| `CD_Neeko19_CastAnimWithClone` | Chronos | 1.3712 | Throw1 0.2331, Throw2 0.3467, Throw3 0.46, Throw4 0.5733, Throw5 0.6867, Throw6 0.8, Unlock 0.8 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayChronoOnTraitActivation`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_Neeko19_SpellUsingVFX`, `GA_ShopEvents`, `GA_Neeko19_PassiveKillTracker`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Neeko19_SpellUsingVFX.txt
- `GE_ManaLock`: applies mana lock: GA_Neeko19_SpellUsingVFX.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-17); open: Q5, Q6 (arc), Q8, Q10, Q13 (no damage evidence yet)
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | **confirmed** (1★) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster: 7 / attack, 2 / s; T3 default for ranged: attack start | **7 / attack and 2 / s confirmed; paid at the release** (the T3 default, corrected 2026-11-17) | E2, E3, E4 |
| Q3 | First attack at combat start: when does it land? | G3: a fresh attack at combat start, released 13 ticks in | **consistent** (mana at +14 frames from the combat banner ending) | E4 |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.4219 s (12.66 → 13 ticks) | **consistent, indirect**: E3 and E4 both fit a 13-tick windup with mana at the release | E3, E4 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted: attack 2000 (13 ticks at 4 hexes). Spell missiles also 2000 but arc (height 400); engine assumes straight-line time (G4), ~20 ticks if speed is along the arc | build (P7) |
| Q7 | Cast time: cast start to the next attack starting | 0.8333 s (25 ticks) | **consistent, indirect**: next attack's mana at +38/39 frames = 25 + 13-tick windup | E3 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted (only base AS seen) | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.8 s (24 ticks) | **consistent**: lock ended between +22.5 and +30 frames | E6 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted (only base AS seen) | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | **0 for role mana** (no +7 at or after the cast until the next attack) | E3 |
| Q12 | Does the cast cancel or reset an attack in progress? | yes (script cancels `Combat.Attacking`) | **consistent**; now from data: the spell cancels `Combat.Attacking` (T4, `cancels_attack`), so the attack in its windup never releases. E7 can't separate cancel from "released during the cast" (mana is blocked during the cast lock either way); a damage number would | E7, T4 |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted, implemented from the script: 6 throws (CD_Neeko19_CastAnimWithClone Throw1-6); 1, 2, 4 = Popper missiles at full damage, 3, 5, 6 = Encore missiles × CT_Encore19 RecastEffectiveness (0 / 25% / 50%); each applies GE_Neeko19_Damage on arrival = DamageAP × AP × effectiveness, magic, no spell crit (RollIfCanSpellCrit) | script, build; D1 below |
| Q14 | Passives and other mechanics that need modelling | see ability text | kill passive (+1% AP per spell kill, KillBuffer 0.2 s): **not modelled**, dummies never die | D1 below |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-17 (`set19champs.Neeko`) | D1 below |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: `Outplayed/…PBE_11-17-2026_15-16-17-933.mp4` (owner's PBE recording, Tocker's Trials, recorded 2026-11-17 15:08-15:16; build
`rls-19.1.0.5973071` installed 13:28 and no newer build snapshotted), 1280x720 at 30 fps, so 1 frame ≈ 1 tick. Neeko 1★, no
items, no active traits (Encore 1/2, Prodigy 1/2, K/DA 1★/3★), round 1-1. Mana read every frame from the
inspection panel's bar with `tools/vod_panel.py` (panel shows whole mana; the reading matched the panel's numbers
to within 0.3 mana at 9 checked frames).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | 106.5 s (f3195) | 30 | inspection panel stats | HP 500/500 at full, mana max 40, AD 30, AS 0.70, armor 25, MR 25, crit 25% | matches the build (and the owner's base crit) | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | 100.5-116 s (f3015-3480) | 30 | mana steps | 8 attack steps of exactly +7; between them +1 every 15 frames (f3095, 3110, 3125, … exact 15-frame spacing) | 7 / attack; 2 / s (display rounds down, so 0.5 per 0.25 s and 1 per 0.5 s look the same) | Q2, G17 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | cast f3246 → next +7 at f3285 | 30 | cast start (bar 39 → 0) to the next attack's mana | +39 frames | mana at attack start would be +25 (cast lock); at the release +25 + 13 = +38; on the hit later still (flight ≈ 13 more). **Release fits.** | Q2, Q4, Q7, Q11 |
| E4 | 2026-11-17 | rls-19.1.0.5973071 | combat start f3068 (round timer flips 0 → 30, "Combat" banner gone; minions move at f3070) → first +7 at f3082 | 30 | first attack's mana | +14 frames | release of a fresh attack at combat start = 13 ticks ✓; mana at the start would be +0 | Q2, Q3, Q4 |
| E5 | 2026-11-17 | rls-19.1.0.5973071 | +7 steps at f3082, 3126, 3169, 3212; 3285, 3329, 3371, 3414 | 30 | attack period | gaps 44, 43, 43; 44, 42, 43 (mean 43.2) | 1 / 0.7 = 42.86 ticks with the fraction carried (T2) ✓ | Q4, T2 |
| E6 | 2026-11-17 | rls-19.1.0.5973071 | cast f3246; next +1 at f3283, then every 15 | 30 | mana lock end | regen steps fall on a 7.5-frame grid (…3238.5, 3246, 3253.5, …); the first visible +1 at 3283.5 needs two paid steps, so the lock ended after 3268.5 and by 3276 | lock end in (+22.5, +30] frames; predicted +24 ✓ | Q9 |
| E7 | 2026-11-17 | rls-19.1.0.5973071 | casts at f3246 and f3448 | 30 | what filled the bar; the attack in progress | both casts on the frame regen reached 40 (39 → 0 directly, no frame at 40); the next attack had started ~4 frames earlier (release-based schedule: 3212 + 43 - 13 = 3242; 3414 + 43 - 13 = 3444) and never paid | a bar filled by regen casts **on the same tick** (T4 predicts the next tick; display-level evidence, n = 2); the attack in progress is cancelled | Q12, T4 |
| E8 | 2026-11-17 | rls-19.1.0.5973071 | regen grid vs combat start f3068 | 30 | regen phase | grid steps at 3072.5, 3080, … : first step ~4.5 frames after combat start, not 7.5; phase unchanged through both casts | the 0.25 s regen grid is not aligned to combat start | G17 |

## Decisions and notes

- 2026-11-17: Neeko pays attack mana at the **release** (E3, E4). That is now the T3 default for ranged units
  (Draven and Varus seen on screen; Set 18's "Hold" event was the release), so she needs no override.
  The idea that "spell cancels attacks" marks release-payers is withdrawn: every Set 19 spell checked has
  that flag.
- Still open: Q5/Q8/Q10 need a fight at clearly higher attack speed; Q13 (implemented from the script, D1) needs damage numbers (the inspection
  panel doesn't show them; a damage recap or the dummy HP bar is needed).
- D1 2026-11-17: implemented as `set19champs.Neeko` (tests: `test_neeko.py`, local). Script
  `GA_Neeko19_SpellUsingVFX` (build ga_scripts.zip): the cast chrono's `Throw1`-`Throw6` events each play a
  projectile chrono (switch at 0x18e3): Throw1/2/4 -> `CD_Neeko19_Projectile1/2/4` ('Popper', effectiveness 1),
  Throw3/5/6 -> `..._Encore` ('Encore', effectiveness `RecastEffectiveness` at the Encore level, read at
  activation, 0x4423). Damage on each missile's `OnArrived` (0x329, 0x76c, 0xc9d, 0x10e4, 0x3d71, 0x3f27):
  `GE_Neeko19_Damage` = MagicDamageCalc1 × SetByCaller `Set19.Trait.Encore.Effectiveness` (MultiplyAdditive), magic.
  Throws fire at ticks 7, 11, 14, 18, 21, 24 after the cast; each lands 13 ticks later at range 4 (G4).
  Assumptions made here: one damage per throw (each projectile chrono holds two identical 'Popper' modules; the text
  says "3 confetti streams that each deal"); arc travel time (G4); the Encore tier from the Encore trait buff (B11).
  Checked in tests against the VOD: attack mana every 43 ticks from tick 13 (E4, E5), the next attack's mana 38
  ticks after a cast (E3: 39 frames).
- Known gap vs the VOD: the engine's first cast is at tick 174 from combat start; the VOD's at ~177-178 frames.
  Attacks and the cast lock match, so the difference is the regen grid's phase (G17: the engine pays regen from
  tick 0, the VOD's grid started ~4.5 frames after the banner). Left open until more units show the phase.
- 2026-11-17: without Encore the engine skips the three Encore missiles. The game still fires them (the script plays
  the Encore projectile chronos on every cast) and applies `GE_Neeko19_Damage` at effectiveness 0, i.e. three 0-damage
  hits. Same damage either way; it would matter only for an effect that counts spell hits regardless of size. If one
  is implemented, deal the 0 hits instead of skipping them (and see E20).
- 2026-11-17, second VOD (`…PBE_11-17-2026_16-35-16-966.mp4`, 60 fps, rls-19.1.0.5973071), f20438: Neeko with
  Guinsoo's + Blue Buff showed max mana **36**. Source (owner): the K/DA trait, whose tiers count the members' total
  star level; (3) POP/STARS = "0.1 reduced max Mana" (`CT` row `ManaReduction` 0.1): 40 x 0.9 = 36 exactly. K/DA is
  not implemented yet; when it is, this is its first check.
