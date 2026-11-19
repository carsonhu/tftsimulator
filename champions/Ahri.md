# Ahri (4-cost MagicCaster) · `DA_Ahri19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5986094.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5986094.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: K/DA, Choreographer
- **HP** 850 / 1530 / 2754 · **AD** 30 / 45 / 67.5 · **AS** 0.8 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 0 / 30

### Ability: Burn it Down

> Passive: Start combat with 6 fox-fires and gain 2/2/4 after casting, up to 14. Then enter a flow state, moving faster and empowering subsequent casts.
> 
> Active: Launch all fox-fires at the target, each dealing 28/42/400 × AP magic damage. If in the flow, instead launch a heart at the target that deals 235/350/2000 × AP magic damage and split the fox-fires among all enemies within 2 hexes of them.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| APDamage | 28 | 42 | 400 |
| HexRangeAroundTarget | 2 | 2 | 2 |
| APDamage_Secondary | 235 | 350 | 2000 |
| FoxFiresPerCast | 2 | 2 | 4 |
| BaseFoxFires | 6 | 6 | 6 |
| APAtMaxFire | 0 | 0 | 0 |
| MaxFoxFires | 14 | 14 | 14 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 28/42/400 × AP
- `MagicDamageCalc2` = 235/350/2000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_19_Ahri_Attack`: launch 0.3067 s (9.2 ticks), variants 0.3067, 0.3874; animation length 3.2 s (96 ticks); release at base AS 0.3067 s (9.2 ticks)
- Attack projectile: DA_Ahri19_AutoAttackProjectile, speed 1750 units/s
- Spell `GA_19_Ahri_Spell` (chrono `CD_19_Ahri_CastAnim_Empowered`): cast ends 0.9667 s (29 ticks), next attack can start 1 s (30 ticks), mana lock removed 0.9667 s (29 ticks); ended by `FinishCasting via OnEventBegin:CD_19_Ahri_CastAnim_Empowered:Unlock`
  - notes: projectile (hit time depends on travel) ×6

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_19_Ahri_Attack` | Chronos/Default | 3.2 | LaunchAttack 0.3067, LaunchAttack 0.3874, Unlock 1.2, Unlock 1.28 |
| `CD_Ahri19_DashMove` | Chronos/Default | 0.3002 | Arrived 0.3002 |
| `CD_19_Ahri_CastAnim_Empowered` | Chronos/Spell/Empowered | 1.8155 | Fire 0.5157, Unlock 0.9443 |
| `CD_19_Ahri_SpiritRushActivationPose` | Chronos/Spell/Empowered | 0.7667 | PowerUp 0.2009, Unlock 0.7512 |
| `CD_19_Ahri_CastAnim_Basic` | Chronos/Spell/Standard | 1.1568 | StartMissiles 0.1398, Unlock 0.9981 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_19_Ahri_SunglassesOn`, `GA_PlayChronoOnTraitActivation`, `GA_Ahri19_MoveToTarget`, `GA_Death`, `GA_Celebration`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_19_Ahri_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_19_Ahri_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_19_Ahri_Spell.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

- nothing in this unit's data

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3067 s (9.2 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1750 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1 s (30 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.9667 s (29 ticks) | predicted | |
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

