# Lee Sin (5-cost AttackFighter) · `DA_LeeSin19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Gu Feng
- **HP** 1200 / 2160 / 3888 · **AD** 60 / 90 / 135 · **AS** 0.85 · **Range** 1 · **Armor** 70 · **MR** 70 · **Mana** 0 / 50
- **Unlock**: Deal 40 player damage while fielding Xayah.

### Ability: Celestial Combo To Impress The Heavens

> Unleash a devastating 2/2/99-part combo attack, starting from Dragon Slam and performing moves in sequence. Subsequent casts increase the length of the combo.
> 
> Dragon Slam: Deal 175/280/9900 × AD + 15/20/660 × AP physical damage to the target. Other enemies within 2 hexes take 40% of the damage.
> 
> Tempest Spin: Deal 1.35 × PhysicalDamageCalc1 physical damage to the target, knocking them up for 1/1/10 second. Other enemies within 1 hex take 50% of the damage.
> 
> Celestial Punch: Deal 2.5 × PhysicalDamageCalc1 physical damage to the target and mark them. If they are already marked, the punch strikes their core, dealing 400% bonus true damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 60 | 90 | 135 |
| SlamDamageAD | 175 | 280 | 9900 |
| SlamDamageAP | 15 | 20 | 660 |
| SpinDamagePercent | 1.35 | 1.35 | 1.35 |
| PunchDamagePercent | 2.5 | 2.5 | 2.5 |
| BaseComboMoves | 2 | 2 | 99 |
| ExtraMovesPerCast | 1 | 1 | 1 |
| SpinDamageSplitOverNHits | 3 | 3 | 3 |
| SlamHexRange | 2 | 2 | 2 |
| SlamAOEPercent | 0.4 | 0.4 | 0.4 |
| SpinHexRange | 1 | 1 | 1 |
| SpinAOEPercent | 0.5 | 0.5 | 0.5 |
| SpinKnockupDuration | 1 | 1 | 10 |
| PunchBonusPercent | 4 | 4 | 4 |
| PunchesForBonus | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 175/280/9900 × AD + 15/20/660 × AP
- `PhysicalDamageCalc2` = 1.35 × PhysicalDamageCalc1
- `GenericCalc1` = 1 × PhysicalDamageCalc2 + 3
- `PhysicalDamageCalc3` = 2.5 × PhysicalDamageCalc1
- `GenericCalc2` = 2/2/99

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_LeeSin19_Attack`: launch 0.33 s (9.9 ticks); animation length 1.7666 s (53 ticks); release at base AS 0.33 s (9.9 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_LeeSin19_Spell` (chrono `–`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_LeeSin19_MoveToLocation` | Chronos/3Star | 59.9705 | Arrive 59.9705 |
| `CD_LeeSin19_Attack` | Chronos/Basic | 1.3 | LaunchAttack 0.33, Unlock 0.52, Unlock 0.64, Unlock 0.7067 |
| `CD_LeeSin19_Celebration` | Chronos/Basic | 8.7747 | Default 0, Loop 1.7704 |
| `CD_LeeSin19_Dash` | Chronos/Spell | 0.5512 | Arrived 0.5512 |
| `CD_LeeSin19_Punch` | Chronos/Spell | 1.1461 | PunchDamage 0.382, ContinueChain 0.7159, Unlock 1.1297 |
| `CD_LeeSin19_Slam` | Chronos/Spell | 1 | SlamDamage 0.2635, Next 0.6734 |
| `CD_LeeSin19_Spin` | Chronos/Spell | 1.1 | Knockup 0.1612, SpinDamage 0.1612, SpinDamage 0.3532, SpinDamage 0.5389, Next 0.7794 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Play3Star5CostCamera`, `GA_GainDamageReductionAt3Star`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_LeeSin19_Spell`, `GA_ShopEvents`, `GA_PlayAdditionalChronoOnStarUp`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_LeeSin19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_LeeSin19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.33 s (9.9 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | – | open | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | open | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | open | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | open | |
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

