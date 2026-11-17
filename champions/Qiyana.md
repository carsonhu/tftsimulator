# Qiyana (2-cost AttackFighter) · `DA_Qiyana19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive ⟨computed in game: TFTStageMagnitude⟩; MovementSpeed + 200; ManaMax at least 10)
- **Cost** 2, pool 25; traits: True Damage, Renegade
- **HP** 750 / 1350 / 2430 · **AD** 45 / 67.5 / 101.25 · **AS** 0.8 · **Range** 1 · **Armor** 40 · **MR** 40 · **Mana** 0 / 40

### Ability: Shuffled Playlist

> Passive: Qiyana's ring changes color periodically, giving her Ability bonus effects.
> 
> Active: Dash to strike enemies in a line, dealing 30/45/70 × AP + 195/290/440 × AD physical damage to the target and 0.5 × PhysicalDamageCalc1 to other enemies hit.
> 
> Red: Deal 20% bonus damage.
> Green: Heal for 20% of damage dealt.
> Blue: Refund 10 Mana.
> Gold: Gain 1 gold and randomly use another effect. (Gold Gained: ⟨live⟩)

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 45 | 67.5 | 101.25 |
| GreenHealPercent | 0.2 | 0.2 | 0.2 |
| BlueManaRefund | 10 | 10 | 10 |
| GoldAmount | 1 | 1 | 1 |
| RedBonusDamagePercent | 0.2 | 0.2 | 0.2 |
| DamageAD | 195 | 290 | 440 |
| DamageAP | 30 | 45 | 70 |
| SecondaryDamagePercent | 0.5 | 0.5 | 0.5 |
| RedWeight | 1 | 1 | 1 |
| GreenWeight | 1 | 1 | 1 |
| BlueWeight | 1 | 1 | 1 |
| GoldChanceIndependent | 0.1 | 0.1 | 0.2 |
| TimeRingChange | 1.5 | 1.5 | 1.5 |
| WaveNumHexesBehindTarget | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 30/45/70 × AP + 195/290/440 × AD
- `PhysicalDamageCalc2` = 0.5 × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Qiyana19_Attack`: launch 0.2992 s (8.98 ticks), variants 0.2992, 0.3067, 0.307; animation length 2.1 s (63 ticks); release at base AS 0.2992 s (8.98 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Qiyana19_Spell` (chrono `–`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Qiyana19_Attack` | Chronos | 1.9667 | LaunchAttack 0.2992, LaunchAttack 0.3067, LaunchAttack 0.307, Unlock 0.5867, Unlock 0.7867, Unlock 0.84 |
| `CD_Qiyana19_CastAnimMove` | Chronos | 1.5006 | MovementEnd 0.4004, Fire 0.7299, PrintGold 0.7784, ManaUnlock 1.2495, Unlock 1.4916 |
| `CD_Qiyana19_CastAnimNoMove` | Chronos | 1.1016 | Fire 0.3498, PrintGold 0.3779, ManaUnlock 0.8491, Unlock 1.0912 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Qiyana19_Spell`, `GA_ShopEvents`, `GA_TrueDamage19_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Qiyana19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Qiyana19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Qiyana19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Qiyana19_Spell.txt

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2992 s (8.98 ticks) | predicted | |
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

