# Kayn (1-cost AttackFighter) · `DA_Kayn19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Heartsteel, Slayer
- **HP** 650 / 1170 / 2106 · **AD** 42 / 63 / 94.5 · **AS** 0.75 · **Range** 1 · **Armor** 35 · **MR** 35 · **Mana** 0 / 30

### Ability: Shadow of the Night

> Dash and swipe, dealing 115/175/270 × AD + 15/25/45 × AP physical damage to enemies in a 2 hex line.
> 
> Heartsteel Upgrade: At 70% Health, turn into the Shadow Assassin, briefly becoming untargetable and dealing 35% bonus magic damage for the rest of combat.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 42 | 63 | 94.5 |
| SpellMagicDamage | 15 | 25 | 45 |
| SpellPhysicalDamage | 115 | 175 | 270 |
| SpellWidth | 100 | 100 | 100 |
| SpellLength | 429 | 429 | 429 |
| SpellHexLength | 2 | 2 | 2 |
| ExtraDashRangeAboveAttackRange | 1 | 1 | 1 |
| HeartsteelStan_PercentHealthTrigger | 0.7 | 0.7 | 0.7 |
| HeartsteelStan_MagicDamagePostTransform | 0.35 | 0.35 | 0.35 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 115/175/270 × AD + 15/25/45 × AP
- `GenericCalc1` = 115/175/270 × AD
- `GenericCalc2` = 15/25/45 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Kayn19_Attack`: launch 0.3273 s (9.82 ticks); animation length 2.6 s (78 ticks); release at base AS 0.3273 s (9.82 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Kayn19_Spell` (chrono `CD_Kayn19_Spell`): cast ends 0.7333 s (22 ticks), next attack can start 0.7667 s (23 ticks), mana lock removed 0.7333 s (22 ticks); ended by `FinishCasting via OnChronoStopped:CD_Kayn19_Spell:None`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Kayn19_Attack` | ChronoDefs | 2.6 | LaunchAttack 0.3273, Unlock 1.04 |
| `CD_Kayn19_Dash` | ChronoDefs | 1.1094 | Default 0, Loop 0.4624, FinishJump 0.4816 |
| `CD_Kayn19_Heartsteel_BecomeShadowAssassin` | ChronoDefs | 89.9497 | Default 0, Loop 0.012 |
| `CD_Kayn19_Spell` | ChronoDefs | 0.7304 | DealDamage 0.4591 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Kayn19_Heartsteel_Passive`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Kayn19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Kayn19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Kayn19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3273 s (9.82 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 0.7667 s (23 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.7333 s (22 ticks) | predicted | |
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

