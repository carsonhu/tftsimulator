# Kayle (4-cost MagicMarksman) · `DA_Kayle19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** MagicMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Pentakill, Swiftstriker
- **HP** 850 / 1530 / 2754 · **AD** 10 / 15 / 22.5 · **AS** 0.8 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 0 / 50
- **Unlock**: 4 unique Pentakill or Swiftstriker Champions.

### Ability: Stairway to Hell

> Passive: Attacks deal 40/60/500 × AP bonus magic damage.
> 
> Active: For 4 seconds, gain 80% Attack Speed, infinite range, and summon a sword with each attack. Afterwards, rain swords on the target, dealing 180/270/2000 × AP to all enemies within 2 hexes, plus 37/55/400 × AP magic damage to the target for each sword.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 10 | 15 | 22.5 |
| APDamage | 40 | 60 | 500 |
| AscensionTwoWavePercent | 0 | 0 | 0 |
| SwordAPDamage | 37 | 55 | 400 |
| FirstAscensionEveryXAttacks | 999 | 999 | 999 |
| SecondAscensionEveryXAttacks | 999 | 999 | 999 |
| ThirdAscensionEveryXAttacks | 999 | 999 | 999 |
| ExtraCastsExtraSwords | 0 | 0 | 0 |
| AOEHexRange | 2 | 2 | 2 |
| AOEDamageAP | 180 | 270 | 2000 |
| BonusAttackSpeed | 0.8 | 0.8 | 0.8 |
| Duration | 4 | 4 | 4 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 40/60/500 × AP
- `MagicDamageCalc2` = 180/270/2000 × AP
- `MagicDamageCalc3` = 37/55/400 × AP
- `AttackSpeedCalc1` = 0.8 + 1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Kayle19_Attack`: launch 0.3979 s (11.94 ticks); animation length 2.1667 s (65 ticks); release at base AS 0.3979 s (11.94 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Kayle19_Spell_new` (chrono `CD_Kayle19_BeginCast`): cast ends 0.5 s (15 ticks), next attack can start 0.5333 s (16 ticks), mana lock removed –; **script reads attack speed**; ended by `FinishCasting via OnEventBegin:CD_Kayle19_BeginCast:Unlock`
  - notes: rate from unresolved CallFunc_PlayChronoWithTargetActor_Speed_ImplicitCast ×1; projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Kayle19_Attack` | Chrono | 2.1667 | LaunchAttack 0.3979, Unlock 0.8667 |
| `CD_Kayle19_BeginCast` | Chrono | 0.5 | Buff 0.1324, Unlock 0.4929 |
| `CD_Kayle19_Celebration` | Chrono | 4.5995 | Default 0, Loop 0.7328 |
| `CD_Kayle19_LaunchAllSwords` | Chrono | 4.5077 | SwordsGoUp 0.3386, BigHit 1.048, Unlock 1.4532 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_Kayle19_RangedAttack_new`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Kayle19_Spell_new`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Kayle19_Spell_new.txt
- `LaunchAttack`: launches or listens for attacks: GA_Kayle19_RangedAttack_new.txt, GA_Kayle19_Spell_new.txt
- `AttackSpeed`: reads or changes attack speed: GA_Kayle19_Spell_new.txt
- `GE_ManaLock`: applies mana lock: GA_Kayle19_Spell_new.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Kayle`, D1); panel, buff and the cast's mana lock
  checked against VOD5
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed with her items (1★) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicMarksman | confirmed: 10 per attack, no role regen (12/s from two Blue Buffs) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3979 s (11.94 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 0.5333 s (16 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script reads AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | consistent: until the finale's Unlock, 183.5 ticks after the filling attack (engine 181) | E2 |
| Q10 | Does the mana lock scale with attack speed? | script reads AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | predicted: 0 (no GE_SimulateLaunchAttack) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read: D1); no damage number read yet | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | the passive's magic on every attack (D1); Pentakill (B25), Swiftstriker implemented | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD5 (`…PBE_11-18-2026_0-57-11-500.mp4`, session folder 0-33-59-673, 60 fps), the owner's
PBE recording in the score mode, build `rls-19.1.0.5973071`; Kayle 1★, round 2-2. Ticks count from the attack that filled
her bar (f39606).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 10:59 (f39540) | 60 | inspection panel | 850/850, 26/50, 12/s; AD 16, AD 60%, AP 60%, AS 0.92, crit 45%, armor 63, MR 83, range 4; Quicksilver, two Blue Buffs; Pentakill (5), Bodyguard (2), Juggernaut (2) active | 0.8 x 1.15 AS, 2 x 6 regen, 10 x 1.6 AD: as built with Pentakill (5) | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 f39525-40104 (`tools/vod_text_changes.py`, mana and as) | 60 | mana text, AS | +10 at f39541 and f39606 (fills, 32.5 ticks apart); AS 0.94 -> 1.58 at +15 ticks (the buff, +80%; the panel may lag the 'Buff' event at +4) and back to 1.06 at +154.5; mana again (overflow) at +183.5; the next attack's mana 19.5 later, then 26.5 | engine (Quicksilver, two Blue Buffs): the lock lifts 181 ticks after the fill (cast +1, Buff 4, buff 4.375 s, finale 1.4532 s); the next attack 12 ticks after the lift, the clip 19.5 (open) | Q2, Q9 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Kayle`):
  - **Attacks:** her own projectile (DA_Kayle19_AutoAttackProjectile, 2250 units/s, read from the client asset: the
    snapshot doesn't read projectiles named in a champion's own attack script) and GE_Kayle19_PassiveDamage (40/60/500
    x AP magic, on-spell) on every hit.
  - **Cast (GA_Kayle19_Spell_new):** CD_Kayle19_BeginCast at S = FClamp(AS / (base AS x 1.8), 1, 2); mana lock. At
    Buff (0.1324 s / S): +80% AS for Duration (4 s) + 0.75 x the chrono's duration, taken as its length / S (VOD5 fits
    this: 181 vs 183.5 ticks; the chrono's 1.29 s animation end would give 198). Unlock (0.4929 s / S) ends the cast.
    Each real attack launch during the buff makes a sword. When the buff ends she stops, and
    CD_Kayle19_LaunchAllSwords plays at FClamp(sqrt(AS / (base x 1.8)), 1, 1.5): BigHit (1.048 s) 180/270/2000 x AP to
    every enemy within 2 hexes of the target, then one 37/55/400 x AP sword every 0.1 s on the target; Unlock (1.4532 s)
    lets her attack and lifts the mana lock.

