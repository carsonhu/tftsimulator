# Mel (4-cost MagicCaster) · `DA_Mel19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6018196.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6018196.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: R&B, Arcanist
- **HP** 850 / 1530 / 2754 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 0 / 40

### Ability: Chain of Blues

> Fire 30/30/60 missiles split between the 3 closest enemies that each deal 19/29/200 × AP magic damage and apply a stack of Blues. For every 3 stacks of Blues, enemies take 5% more damage from this Ability.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| NumEnemies | 3 | 3 | 3 |
| NumMissiles | 30 | 30 | 60 |
| APDamage | 19 | 29 | 200 |
| PercentDamageOnCurrentTarget | 0.6 | 0.6 | 0.6 |
| RadianceStacksForNegativeDR | 3 | 3 | 3 |
| NegativeDRForRadianceBundle | 0.05 | 0.05 | 0.05 |
| AoeRangeAroundTarget | 10 | 10 | 10 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 19/29/200 × AP
- `GenericCalc1` = 0.05 ÷ 3

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Mel19_Attack_New`: launch 0.365 s (10.95 ticks); animation length 2.6667 s (80 ticks); release at base AS 0.365 s (10.95 ticks)
- Attack projectile: DA_Mel19_AutoAttackProjectile, speed 1600 units/s
- Spell `GA_Mel19_Spell` (chrono `CD_Mel19_CastAnim`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Mel19_Attack_New` | Chronos | 2.1667 | LaunchAttack 0.365, Unlock 0.8664 |
| `CD_Mel19_CastAnim` | Chronos/Spell | 2.1785 | Fire 0.5076 |
| `CD_Mel19_CastAnimOut` | Chronos/Spell | 0.3473 | Unlock 0.3214 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Mel19_Spell`, `GA_ShopEvents`, `GA_Mel19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Mel19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Mel19_Spell.txt

### Changed since `rls-19.1.0.6011486.Set19.Shipping.pbe`

- row APDamage: 18 / 28 / 200 -> 19 / 29 / 200
- ability text changed

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Mel`, D1); the cast's length checked on VOD6 to a tick
  (E2), which set ledger T15
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has her at 2-5)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | mana 40 confirmed; HP 1025 vs 850 and 3 regen, +12 per attack (items and traits not identified) | E2 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster: 7 per attack, 2/s | consistent (+12 = 7 + 5, e.g. Spear of Shojin; 3/s) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.365 s (10.95 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1600 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 63 ticks | consistent (Q9) | E2 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 'Fire' + 30 x 0.04 s + CastAnimOut 'Unlock' = 62 ticks (T15) | confirmed: the banked overflow shows 63 ticks after the bar empties, four times | E2 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 (no GE_SimulateLaunchAttack) | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | 30 missiles APDamage x AP, 3 of 5 on the target | predicted | D1 |
| Q14 | Passives and other mechanics that need modelling | Blues stacks: +5% damage from her ability per 3 stacks | modelled, pro rata (GenericCalc1 = 0.05 / 3 per stack) | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18, 60 fps; client rls-19.1.0.5986652, not exported: the simulator's newest is 5986094). Round 2-5:
Mel with items. Mana from `tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f51335-52255 (round 2-5) | 60 | mana and Health text | 1025/1025, x/40, 3/s, +12 per attack; casts f51478 (32 + 12 = 44), f51704 (33 + 12 = 45), f51911 (34 + 12 = 46), f52129 (34 + 12 = 46); the overflow shows at f51604, f51830, f52037, f52255: +126 frames each | the mana lock 62 ticks + the tick after the fill: OnFinished one interval after the 30th missile (T15) | Q1, Q2, Q9 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Mel`):
  - **Cast (GA_Mel19_Spell):** mana lock (0x21c4); CD_Mel19_CastAnim at the targets' average spot. 'Fire'
    (0.5076 s): RepeatAction(TimeBetweenMissiles 0.04 s, NumMissiles), first at once. Missile n goes to her target
    when n mod (1 / (1 - PercentDamageOnCurrentTarget)) <= 1 (3 of 5), else to the next secondary target (the
    NumEnemies nearest by row distance; her target if none). CD_Mel19_SpellMissile: selectors 1-4 (n mod 4) are
    the fixed-speed splines (2100 units/s). Arrival: GE_Mel19_TargetDamage = MagicDamageCalc1 (APDamage x AP),
    magic, on-spell, RollIfCanSpellCrit; then a GE_Mel19_RadianceDRReduction stack (infinite, AggregateByTarget).
    OnFinished (T15): CD_Mel19_CastAnimOut; 'Unlock' (0.3214 s) lifts the lock and ends the cast.
  - **Passive (GA_Mel19_Passive):** her on-spell damage (WaitForDealDamage AppliesOnSpell) to an enemy with stacks
    carries GE_Mel19_RadianceDRReductionForDamageInstanceOnly: IncomingDamageMultiplier MultiplyCompound
    (GenericCalc1 x stacks + 1), GenericCalc1 = NegativeDRForRadianceBundle / RadianceStacksForNegativeDR (the
    build's text shows "0.05 + 3": set_dump read the string op DivideAdditive as +, fixed 2026-11-18).
  - **Simulated:** the passive on her missiles; a missile's own stack after its damage; stacks for the rest of
    combat.
