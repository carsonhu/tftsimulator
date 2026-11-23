# Bard (3-cost MagicMarksman) · `DA_Bard19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6018196.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6018196.Set19.Shipping.pbe`

- **Role** MagicMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 3, pool 18; traits: Jazz, Swiftstriker
- **HP** 650 / 1170 / 2106 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 35 · **MR** 35 · **Mana** 20 / 80

### Ability: Come Chime With Me

> Passive: Gain the Horn of the Traveler. While equipped, casts generate XP and attacks grant bonus Mana.
> 
> Active: Summon a wave of meeps that deal 245/365/590 × AP magic damage to enemies hit, reduced by 30% for each one it passes through (minimum 30%).

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| Meeps Damage | 245 | 365 | 590 |
| ManaPerAttack | 2 | 7 | 20 |
| MaxMeeps | 9999 | 9999 | 9999 |
| FalloffPerUnit | 0.3 | 0.3 | 0.3 |
| MeepXP | 1 | 1 | 1 |
| MinimumDamagePercent | 0.3 | 0.3 | 0.3 |

Formulas (as stored; AD and AP are multipliers):

- `ManaCalc1` = 2/7/20 × AP
- `MagicDamageCalc1` = 245/365/590 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Bard19_Attack`: launch 0.29 s (8.7 ticks), variants 0.29, 0.35; animation length 2.0351 s (61.05 ticks); release at base AS 0.29 s (8.7 ticks)
- Attack projectile: DA_Bard19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Bard19_Spell` (chrono `CD_Bard19_CastAnim`): cast ends 1.0667 s (32 ticks), next attack can start 1.1 s (33 ticks), mana lock removed 1.0667 s (32 ticks); ended by `FinishCasting via OnEventBegin:CD_Bard19_CastAnim:Unlock`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Bard19_Attack` | Chronos | 2.0351 | LaunchAttack 0.29, LaunchAttack 0.35, Unlock 0.7708, Unlock 0.8141 |
| `CD_Bard19_CastAnim` | Chronos | 1.0963 | Unlock 1.0552 |
| `CD_Bard19_CastAnimMeeps` | Chronos | 0.8497 | FireMeeps 0.4381, Unlock 0.8402 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Bard19_Spell`, `GA_ShopEvents`, `GA_Bard19_PopHornOff`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Bard19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Bard19_Spell.txt

### Changed since `rls-19.1.0.6011486.Set19.Shipping.pbe`

- row Meeps Damage: 210 / 315 / 505 -> 245 / 365 / 590
- ability text changed

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Bard`, D1); predicted from the script, stats and
  tooltip checked on VOD1's panel (E1); no cast timed yet
- Keep in the simulator: **yes** (owner, 2026-11-18: add Bard; the Horn of the Traveler is not active)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed for HP, AD, mana, range | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicMarksman: 10 per attack | predicted; the horn's bonus mana per attack (ManaPerAttack row) not simulated | D1 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2 s (6 ticks); a second variant at 0.35 s | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G19 (release scales with the period: the build's flag) | predicted | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 0.9 s (27 ticks): CD_Bard19_CastAnimMeeps Unlock + 1 tick (the AUTO block's 1.1 s follows the horn's cast) | predicted | D1 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.8667 s (26 ticks) | predicted | D1 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 (the script applies no GE_SimulateLaunchAttack) | predicted | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | 210/315/505 x AP per enemy, x0.7 for each one before it (at least x0.2), two halves 0.1 s apart | predicted (script and effect read); tooltip 231 = 210 x 1.10 AP | D1, E1 |
| Q14 | Passives and other mechanics that need modelling | the Horn of the Traveler | not applicable: not simulated (owner) | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |
| Q16 | Where the wave starts (the board's edge behind Bard) and so when it reaches the target | half a hex behind him: 29 ticks after FireMeeps at 4 hexes | open (a VOD of the wave's damage numbers) | D1 |
| Q17 | Which enemies the wave meets | the page's number of targets (default 2), all next to the target and within its 600 width, and the enemy 2 hexes behind the target (in the line) | decided (owner, 2026-11-18; G22) | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5973071 | VOD1 (`…PBE_11-17-2026_15-16-17-933.mp4`) 4:44, owner's screenshot | 30 | inspection panel, ability tooltip (round 1-6, planning) | 650/650, 20/80; AD 30, AP 10%, AS 0.90, crit 25%, range 4 hex, armor 58, MR 58; one item (red blade); Jazz, Swiftstriker. Tooltip: Damage 231 (210/315/505) | HP, mana, AD, range as built; 231 = 210 x 1.10 AP. Armor/MR 58 and AS 0.90 come from the board and item, not checked | Q1, Q13 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Bard`):
  - **Horn of the Traveler not simulated** (owner): GA_Bard19_UniqueItem's horn gives casts XP (GA_Bard19_Spell's
    SpawnMeep path, CD_Bard19_CastAnim, taken only with Set19.Unit.Bard.SpecialCast) and bonus mana per attack (the
    ManaPerAttack row, ManaCalc1 2/7/20 x AP) and max mana (GE_Bard19_UniqueItem_Stats). Every cast is the wave.
    The build's predicted spell timing (AUTO block) followed the horn path; Bard's locks come from
    CD_Bard19_CastAnimMeeps instead (Unlock 0.8402 s).
  - **Wave (WaveCast):** mana lock; at FireMeeps (0.4381 s) a 2000 x 600 rectangle from Bard turned to hit the most
    enemies with his attack target among them (FindRectangleRotationFromLocationToHitActorsWithRequired;
    `layout.line_hits`); CD_Bard19_MeepProjectile's MeepHitbox (1000 units/s) runs from the board's edge behind him
    along it. Each enemy it overlaps: GE_Bard19_MeepWaveDamage (client asset: HasDuration 0.2 s, Period 0.1 s,
    bDoTotalDamageOverDuration) = MagicDamageCalc1 x SetByCaller Falloff, magic, AOE, on-spell, crit only with
    Precision; then Falloff = max(Falloff x 0.7, 0.2). Two halves 3 ticks apart, the first on application (as
    Renata's Toxin).
  - **Assumed:** the wave starts half a hex behind Bard (back row) (Q16); it meets the page's number of targets (owner: default 2; G22), all next to the target, and the enemy 2 hexes behind it, nearest Bard first (Q17): 1 + 0.7 +
    0.49 = 2.19 x one hit by default.
