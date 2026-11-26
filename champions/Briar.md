# Briar (3-cost AttackAssassin) · `DA_Briar19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6037882.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6037882.Set19.Shipping.pbe`

- **Role** AttackAssassin: "Attacks grant 10 Mana. Take 15% less damage from all enemies except the current target." (ManaPerAttack + 10; ManaMax at least 10; MovementSpeed + 200; Threat + -10)
- **Cost** 3, pool 18; traits: Ionic Spark, Slayer
- **HP** 850 / 1530 / 2754 · **AD** 50 / 75 / 112.5 · **AS** 0.8 · **Range** 1 · **Armor** 45 · **MR** 45 · **Mana** 0 / 30

### Ability: Snack Attack

> Heal 80/120/160 × AP and kick a snack at the furthest enemy within 3 hexes. Dash toward it, dealing 95/145/230 × AD physical damage in a 1 hex area.
> 
> Then chow down, gaining 200% Attack Speed for the next 3 attacks and replacing them with slashes that deal 80/120/190 × AD physical damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 50 | 75 | 112.5 |
| DamageAOE_AD | 95 | 145 | 230 |
| HexRangeAOE | 1 | 1 | 1 |
| NumFrenzyAttacks | 3 | 3 | 3 |
| DamageFrenzyAD | 80 | 120 | 190 |
| HealFrenzyAP | 80 | 120 | 160 |
| HexRangeSnack | 3 | 3 | 3 |
| FrenzyAS | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 95/145/230 × AD
- `PhysicalDamageCalc2` = 80/120/190 × AD
- `HealthCalc1` = 80/120/160 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Briar19_Attack`: launch 0.3289 s (9.87 ticks); animation length 2.7667 s (83 ticks); release at base AS 0.3289 s (9.87 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Briar19_Spell` (chrono `CD_Briar19_Windup`): cast ends 1 s (30 ticks), next attack can start 1.0333 s (31 ticks), mana lock removed –; ended by `FinishCasting via OnEventBegin:CD_Briar19_CastAnim_Short:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Briar19_Attack` | CD_Briar19_Attack | 2.6333 | LaunchAttack 0.3289, CustomLaunchAttack1 0.4853, CustomLaunchAttack1 0.5099, Unlock 0.64, Unlock 1.0533, Unlock 1.1067 |
| `CD_Briar19_CastAnim_Long` | CD_Briar19_CastAnim_Long | 0.9585 | Default 0, Boom 0.31, Land 0.6731, SlideBack 0.7706, AtNewHex 0.9422, Unlock 0.9422 |
| `CD_Briar19_CastAnim_Short` | CD_Briar19_CastAnim_Short | 0.8166 | Default 0, Boom 0.31, Land 0.5311, SlideBack 0.6286, AtNewHex 0.8003, Unlock 0.8003 |
| `CD_Briar19_Windup` | CD_Briar19_Windup | 0.5013 | HealOverWindup 0, Kick 0.191 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Briar19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Briar19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Briar19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Briar19_Spell.txt

### Changed since `rls-19.1.0.6028987.Set19.Shipping.pbe`

- stat Armor: 50 -> 45
- stat MagicResist: 50 -> 45
- row HealFrenzyAP: 100 / 150 / 200 -> 80 / 120 / 160
- ability text changed

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Briar`, D1); predicted from the script, the panel
  checked on VOD5 (E1); no cast timed yet
- Keep in the simulator: **yes** (owner, 2026-11-18)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed for HP, mana, range | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackAssassin: 10 per attack, on the hit (melee) | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3289 s (10 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 (bUseRateScalingThreshold set, no threshold: G20) | open; matters for the frenzy (AS x3: period 12.5 ticks, slash windup 15) | D1 |
| Q6 | Projectile travel time (ranged only) | – | not applicable | |
| Q7 | Cast time: cast start to the next attack starting | 36 ticks (Long dash: the enemy 2 hexes behind the target is 3 from her, G22): Kick 6 + Unlock 29 + 1; 31 with the Short dash (Unlock 24) | predicted | D1 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | the tick after the 3rd slash | predicted | D1 |
| Q10 | Does the mana lock scale with attack speed? | ends with the slashes, so it shortens with AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0; the 3 slashes are attacks (custom launches) with on-hit effects | predicted | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | dash AOE 100/150/240 x AD on the targets; 3 slashes of 100/150/240 x AD on her target | predicted (script and effects read) | D1 |
| Q14 | Passives and other mechanics that need modelling | the heal and the role's damage reduction: nothing against dummies; full health assumed | not applicable | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 (`…PBE_11-18-2026_0-57-11-500.mp4`) 8:20, owner's screenshot | 60 | inspection panel in combat (round 1-9) | 850/850, 0/30; AD 58, AP 15%, AS 2.92, crit 45%, armor 65, MR 85, range 1 hex, Front; 2 items; Ionic Spark, Slayer, Collab | HP, mana, range as built; AS 2.92 = 0.8 x 3.65 fits the frenzy's +200% with +65% from items and traits (not itemised) | Q1, Q13 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Briar`):
  - **Cast (GA_Briar19_Spell):** mana lock; CD_Briar19_Windup at the snack target (the farthest enemy within 3
    hexes; her target when none); 'Kick' (0.191 s) starts the dash, Short under 2.5 hexes, else Long. The dash
    chronos run three phases whose starts fire 'Boom' and 'Land' (the build lacked these until the snapshot fix,
    2026-11-18): Boom (0.31 s) +200% AS and the frenzy tag; Land (Short 0.5311 / Long 0.6731 s) the AOE; Unlock
    (0.8003 / 0.9422 s) ends the cast.
  - **Frenzy:** 3 custom attacks (CustomLaunchAttack1 at 0.4853, 0.4853, 0.5099 s of 2.6333, 2.6333, 2.7667 s),
    each a slash (GE_Briar19_DamageSlash, on-hit) instead of the attack; the buff ends at the 3rd, the mana lock the
    tick after.
  - **Assumed (owner, 2026-11-18):** full health. The AOE hits the page's number of targets (G22: the target and
    the enemies next to it), not the snack target's neighbours; the snack target only sets the dash's length.
