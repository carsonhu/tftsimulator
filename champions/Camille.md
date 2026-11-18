# Camille (2-cost AttackFighter) · `DA_Camille19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive ⟨computed in game: TFTStageMagnitude⟩ → FighterAttackSpeed curve; MovementSpeed + 200; ManaMax at least 10)
- **Cost** 2, pool 25; traits: Rock, Slayer
- **HP** 750 / 1350 / 2430 · **AD** 45 / 67.5 / 101.25 · **AS** 0.8 · **Range** 1 · **Armor** 45 · **MR** 45 · **Mana** 0 / 40

### Ability: Hookshot Through the Heart

> Passive: When the target dies, hookshot to the next one and deal 90/135/210 × AD physical damage to them.
> 
> Active: Do a sweeping kick, dealing 200/300/465 × AD + 60/90/135 × AP physical damage in a cone.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 45 | 67.5 | 101.25 |
| APDamage | 60 | 90 | 135 |
| PassiveDamage | 90 | 135 | 210 |
| ADDamage | 200 | 300 | 465 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 200/300/465 × AD + 60/90/135 × AP
- `PhysicalDamageCalc2` = 90/135/210 × AD

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Camille19_Attack`: launch 0.2702 s (8.11 ticks), variants 0.2702, 0.3385; animation length 2.3 s (69 ticks); release at base AS 0.2702 s (8.11 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Camille19_Spell` (chrono `CD_Camille19_Spell`): cast ends 0.9 s (27 ticks), next attack can start 0.9333 s (28 ticks), mana lock removed 0.9 s (27 ticks); ended by `FinishCasting via OnEventBegin:CD_Camille19_Spell:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Camille19_Attack` | Chronos | 2 | LaunchAttack 0.2702, LaunchAttack 0.3385, Unlock 0.8, Unlock 0.92 |
| `CD_Camille19_Spell` | Chronos | 0.9004 | DealDamage 0.5251, Unlock 0.8959 |
| `CD_Camille19_DashStart` | Chronos/Passive | 0.4978 | Fire 0.0922 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Camille19_Spell`, `GA_ShopEvents`, `GA_Camille19_PassiveNew`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Ability/GA_Camille19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Ability/GA_Camille19_PassiveNew.txt
- `GE_UnitStopAttackingMovingCasting`: stops the unit attacking/moving/casting: Ability/GA_Camille19_PassiveNew.txt
- `GE_ManaLock`: applies mana lock: Ability/GA_Camille19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2702 s (8.11 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 0.9333 s (28 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.9 s (27 ticks) | predicted | |
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

- 2026-11-18 (owner): Camille's movement is not modelled for now; she is assumed to stand next to her target.

