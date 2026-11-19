# Lux (2-cost MagicCaster) · `DA_Lux19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5995286.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5995286.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Ionic Spark, Prodigy
- **HP** 550 / 990 / 1782 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 30 · **MR** 30 · **Mana** 0 / 40

### Ability: Lux Lux Beam!

> Toss a prism into the air, then blast it with a beam of light. The beam splits, dealing 300/450/675 × AP magic damage to the target, and 160/240/360 × AP to another nearby enemy. For each one that dies, gain 8 Mana.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| NumSecondaryTargets | 1 | 1 | 1 |
| PrimaryDamageAP | 300 | 450 | 675 |
| SecondaryDamageAP | 160 | 240 | 360 |
| ManaRefundOnKill | 8 | 8 | 8 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 300/450/675 × AP
- `MagicDamageCalc2` = 160/240/360 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Lux19_Attack`: launch 0.24 s (7.2 ticks); animation length 0.9667 s (29 ticks); release at base AS 0.331 s (9.93 ticks)
- Attack projectile: DA_Lux19_AutoAttackProjectile, speed 1600 units/s
- Spell `GA_Lux19_Spell` (chrono `–`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Lux19_Attack` | Chronos | 0.9667 | LaunchAttack 0.24, Unlock 0.3867 |
| `CD_Lux19_Spell_new` | Chronos | 1.601 | Prism 0.3137, DamageAndBeam 1.0416, Unlock 1.5625 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayChronoOnTraitActivation`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Lux19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Lux19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Lux19_Spell.txt

### Changed since `rls-19.1.0.5986094.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-17, `set19champs.Lux`, D1); mana and cast rhythm checked against VOD3
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (AD, AS, armor, MR, mana; HP 650 = 550 + 100 from an unidentified board effect) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster | confirmed: 7 per attack, 2/s, with Shojin's +5 / +1 and Adaptive Helm's +3 and x1.15 | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open (VOD3: she walked first) | E2 |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.24 s (7.2 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1600 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | Unlock 1.5625 s: cast lock 48 ticks | consistent: the next attack's mana 59 ticks after the filling attack (VOD3 59.5, 56.5, 59) | E3 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | Unlock 1.5625 s: 47 ticks | consistent: overflow shown 48.5 and 45.5 ticks after the filling attack | E3 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | predicted: 0 (no GE_SimulateLaunchAttack in GA_Lux19_Spell) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read: D1); no damage numbers read yet | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | mana refund on kill: not modelled (dummies never die); Prodigy implemented (B24) | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-17 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD3 (`…PBE_11-17-2026_17-13-37-283.mp4`, 60 fps), the owner's PBE recording, build `rls-19.1.0.5973071`; Lux 1★ with Spear of
Shojin and Adaptive Helm, round 1-9, panel open f28459-29741 and later.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 f28990 (combat start) | 60 | inspection panel | 1★: 650/650 HP, 0/40 mana, 7/s regen; AD 38, AP 25%, AS 0.75, armor 30, MR 50, crit 25%; items Adaptive Helm, Spear of Shojin; Prodigy 1/2 and Ionic Spark inactive | AD 30 x 1.25 (Shojin 15% + Helm 10%), AP 1.25, MR 30 + 20: as built; HP +100 from something on the board (not Lux's) | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 f28998-29741 (`tools/vod_text_changes.py`, mana) | 60 | mana text, every change | regen steps of 1.725 every ~15 frames ((2 + 1 + 3) x 1.15 = 6.9/s, shown 7/s); attacks +13.8 ((7 + 5) x 1.15); values 1, 3, 5, 18, 20, 22, 24, 25, 27, cast at f29116; first regen ~8 frames after combat start; first attack f29034 after walking in | every shown value is the floor of the engine's | Q2, Q3 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 casts filled at f29116, 29319, 29512 | 60 | mana lock and next attack | overflow (1.4, 1.075) shown +97 and +91 frames after the filling attack; next attack's mana +119, +113, +118 frames; casts 203 + 193 frames apart | engine (`test_lux.py`): lock ends +48 ticks, next attack +59, casts 99 + 99 ticks apart (VOD 101.5 + 96.5); cast 2's '0' probably shows ~3 ticks late (a missed text change just before it) | Q7, Q9 |

## Decisions and notes

- 2026-11-17, D1 (implemented, `set19champs.Lux`):
  - **Spell (GA_Lux19_Spell):** mana lock at activation; CD_Lux19_Spell_new at her target's hex. At DamageAndBeam
    (1.0416 s) MagicDamageCalc1 (PrimaryDamageAP x AP) on her attack target and MagicDamageCalc2 (SecondaryDamageAP
    x AP) on the NumSecondaryTargets (1) enemies nearest **her**, the target left out (TR_Add_N_NearestEnemiesWithoutTags,
    SortByRowDistance; the target again when nobody else is left). Both magic spell damage, crit only with Precision
    (RollIfCanSpellCrit). The beams' chronos are visual: the damage is applied at the event.
  - **Locks:** the build's spell timeline has none; read from the chrono as for Senna: mana lock = Unlock (1.5625 s,
    47 ticks), cast lock 48. The spell cancels an attack in progress (CancelAbilitiesWithTag Combat.Attacking).
  - **Assumed:** which dummy the secondary beam hits comes from the dummy layout (nearest Lux; on the default layout
    the one behind the target). SortByRowDistance's tie rule is not decoded; among identical dummies it changes
    nothing but debuffs.
  - **Not modelled:** ManaRefundOnKill (8 per beam target that dies: dummies never die).
- 2026-11-18, Day 1 PBE patch notes, confirmed in the client build rls-19.1.0.5986094 (read from an FModel raw export, B34; it replaced the patch-notes stand-in, B33): PrimaryDamageAP 330/500/800 -> 300/450/675, SecondaryDamageAP 170/255/425 -> 160/240/360. Its timing is unchanged from rls-19.1.0.5973071.
