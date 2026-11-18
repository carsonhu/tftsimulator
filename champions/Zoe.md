# Zoe (1-cost MagicCaster) · `DA_Zoe19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Beach Pop, Arcanist
- **HP** 500 / 900 / 1620 · **AD** 30 / 45 / 67.5 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 15 / 90

### Ability: Paddle Ball

> Fire a paddle ball backwards and redirect it towards the farthest enemy, dealing 450/675/1000 × AP magic damage to the first enemy hit. If they die, the ball ricochets, dealing excess damage to the next enemy hit.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| SpellDamageAP | 450 | 675 | 1000 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 450/675/1000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Zoe19_Attack`: launch 0.3387 s (10.16 ticks); animation length 2.1333 s (64 ticks); release at base AS 0.3387 s (10.16 ticks)
- Attack projectile: DA_Zoe19_AutoAttackProjectile, speed 1900 units/s
- Spell `GA_Zoe19_Spell` (chrono `CD_Zoe19_CastAnim`): cast ends 1.8333 s (55 ticks), next attack can start 1.8667 s (56 ticks), mana lock removed 1.8333 s (55 ticks); ended by `FinishCasting via OnEventBegin:CD_Zoe19_CastAnim:Unlock`
  - notes: projectile (hit time depends on travel) ×6

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Zoe19_Attack` | Chronos | 2.1333 | LaunchAttackVariant1 0.3387, LaunchAttackVariant2 0.3387, Unlock 0.8533 |
| `CD_Zoe19_CastAnim` | Chronos | 1.8492 | LaunchProjectile 0.2884, Splash 0.6738, RedirectProjectile 1.3167, Unlock 1.8147 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Zoe19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Zoe19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Zoe19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3387 s (10.16 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1900 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1.8667 s (56 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.8333 s (55 ticks) | predicted | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
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

