# Katarina (1-cost MagicFighter) · `DA_Katarina19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive ⟨computed in game: TFTStageMagnitude⟩; MovementSpeed + 200; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Classical, Slayer
- **HP** 650 / 1170 / 2106 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 1 · **Armor** 35 · **MR** 35 · **Mana** 0 / 40

### Ability: Blade Sonata

> Twirl, slashing adjacent enemies for 120/180/285 × AP magic damage. Then, eviscerate the current target, dealing 240/360/575 × AP magic damage to them. Enemies hit are Captivated for 5 seconds. 
> 
> Captivated enemies grant bonuses to Classical champions.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| AoEDamageAp | 120 | 180 | 285 |
| CaptivateDuration | 5 | 5 | 5 |
| AoERadius | 1 | 1 | 1 |
| TargetDamageAP | 240 | 360 | 575 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 120/180/285 × AP
- `MagicDamageCalc2` = 240/360/575 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Katarina19_Attack`: launch 0.2918 s (8.75 ticks), variants 0.2918, 0.2985; animation length 1.5 s (45 ticks); release at base AS 0.2918 s (8.75 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Katarina19_Spell` (chrono `CD_Katarina19_CastAnimCombined`): cast ends 1.3 s (39 ticks), next attack can start 1.3333 s (40 ticks), mana lock removed 1.3 s (39 ticks); ended by `FinishCasting via OnEventBegin:CD_Katarina19_CastAnimCombined:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Katarina19_Attack` | CD_Katarina19_Attack | 1.4667 | LaunchAttack 0.2918, LaunchAttack 0.2985, Unlock 0.5867, Unlock 0.6 |
| `CD_Katarina19_CastAnimCombined` | CD_Katarina19_CastAnimCombined | 0.2995 | Spin 0, Unlock 0.2039, Eviscerate 0.2098, CheckIfMove 0.2484, Eviscerate 0.2673, Unlock 0.286 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Katarina19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Katarina19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Katarina19_Spell.txt

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2918 s (8.75 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 1.3333 s (40 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.3 s (39 ticks) | predicted | |
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

