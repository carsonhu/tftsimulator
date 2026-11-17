# Kayle (4-cost MagicMarksman) · `DA_Kayle19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

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
| `CD_Kayle19_LaunchAllSwords` | Chrono | 4.5077 | SwordsGoUp 0.3386, BigHit 1.048, Unlock 1.4532 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_Kayle19_RangedAttack_new`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Kayle19_Spell_new`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Kayle19_Spell_new.txt
- `LaunchAttack`: launches or listens for attacks: GA_Kayle19_RangedAttack_new.txt, GA_Kayle19_Spell_new.txt
- `AttackSpeed`: reads or changes attack speed: GA_Kayle19_Spell_new.txt
- `GE_ManaLock`: applies mana lock: GA_Kayle19_Spell_new.txt

<!-- AUTO END -->

## Status

- Worksheet status: **not started**
- Keep in the simulator: **undecided** (remove if it can't be simulated realistically; give the reason)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | predicted | |
| Q2 | Mana per attack and per second follow the role | MagicMarksman | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3979 s (11.94 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 0.5333 s (16 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script reads AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | predicted | |
| Q10 | Does the mana lock scale with attack speed? | script reads AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted | |
| Q14 | Passives and other mechanics that need modelling | see ability text | open | |
| Q15 | Can this unit be simulated realistically? | | open | |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| Date | Build | Source (VOD URL @ time) | fps | Measured | Frames / values | Result | Question |
|---|---|---|---|---|---|---|---|

## Decisions and notes

