# Yunara (1-cost AttackMarksman) · `DA_Yunara19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Ionic Spark, Swiftstriker
- **HP** 500 / 900 / 1620 · **AD** 50 / 75 / 112.5 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 50 / 80

### Ability: Cultivation of Teen Spirit

> For the rest of combat, attacks fire an additional orb that deals 13/20/30 × AD + 3/5/7 × AP physical damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 50 | 75 | 112.5 |
| APDamage | 3 | 5 | 7 |
| NumOrbsToAdd | 1 | 1 | 1 |
| ADDamage | 13 | 20 | 30 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 13/20/30 × AD + 3/5/7 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Yunara19_AttackNew`: launch 0.2667 s (8 ticks); animation length 2.5666 s (77 ticks); release at base AS 0.2667 s (8 ticks)
- Attack projectile: DA_Yunara19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Yunara19_Spell` (chrono `CD_Yunara19_Empower`): cast ends 0 s (0 ticks), next attack can start 0.0333 s (1 ticks), mana lock removed –; ended by `FinishCasting via activate`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Yunara19_AttackNew` | Chronos | 2.5666 | LaunchAttackVariant1 0.2667, Unlock 1.12 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_ForceSequentialAttack`, `GA_PlayChronoOnTraitActivation`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Yunara19_Spell`, `GA_ShopEvents`, `GA_Yunara19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Yunara19_Passive.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Yunara19_Passive.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented 2026-11-17** (`set19champs.Yunara`, D1; tests `test_yunara.py`)
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | **consistent**: 500 HP, 50 AD, 50/80 mana, AS 0.77 = 0.7 x Swiftstriker's 10% (armor 33 vs 25: another trait) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid? | AttackMarksman | **consistent**: +10 per release, no regen | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | not measurable here: she walked into range first (first release 21.5 ticks after combat start) | E2 |
| Q4 | Attack windup at base AS | 0.2667 s (8 ticks), 2 sequential animations with the same launch | predicted |  |
| Q5 | Windup at higher AS | G2 | **consistent**: releases within a tick through AS 0.77-0.945 | E2 |
| Q6 | Projectile travel time (ranged only) | attack 2000, orbs 1850 | predicted |  |
| Q7 | Cast time: cast start to the next attack starting | 0.0333 s (1 tick) | **consistent**: the cast doesn't interrupt the rhythm (T12) | E2 |
| Q9 | Mana lock | none (no GE_ManaLock): the cast lock, 1 tick | predicted |  |
| Q12 | Does the cast cancel or reset an attack in progress? | no Combat.Attacking cancel | **no**: rhythm unbroken through the cast (T12) | E2 |
| Q13 | Ability damage: formula, targets, hit count | see above | implemented from the script (D1): Stack orbs per attack after the first cast, Calc1 each; damage not yet checked | script |
| Q14 | Passives and other mechanics | see ability text | Swiftstriker (B15); Ionic Spark letters and gift (B22) | B15, B22 |
| Q15 | Can this unit be simulated realistically? |  | **yes**, implemented 2026-11-17 | D1 |
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | predicted | |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackMarksman | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2667 s (8 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 0.0333 s (1 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | predicted | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted | |
| Q14 | Passives and other mechanics that need modelling | see ability text | open | |
| Q15 | Can this unit be simulated realistically? | | open | |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 1:44 (planning) | 60 | inspection panel | 1★, no items, 500 HP, 50/80 mana, AD 50, AS 0.77, armor/MR 33; Swiftstriker (2) | Team AS 10% shown in planning | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | VOD2 f6492-7140 (`tools/vod_text_changes.py`, mana and AS) | 60 | releases and AS | AS 0.80/0.84/0.87/0.91/0.94 at f6612, 6732, 6852, 6972, 7092 (Swiftstriker stacks every 2 s from 2 s: combat start f6492); mana 60, 70, 0 (cast), 10, 20, 40, 50, 60 at 21.5, 61, 98.5, 136, 172, 242, 275, 308 ticks | with her walk-in as a 14-tick delay the engine is within a tick at every release and the cast (99 vs 98.5); the cast keeps the rhythm (T12) | Q2, Q5, Q7, Q12, B15 |

## Decisions and notes

- 2026-11-17, D1 (implemented, `set19champs.Yunara`):
  - **Spell (GA_Yunara19_Spell):** GE_Yunara19_EmpoweredAttack adds NumOrbsToAdd (1) to her Stack attribute for the
    rest of combat; it finishes on activation (T12).
  - **Passive (GA_Yunara19_Passive):** each attack launch with Stack >= 1 plays CD_Yunara19_OrbMis at her target,
    fitted to 0.5 / AttackSpeed s, with MissileSelector tags 1..min(Stack, 11); each orb flies at 1850 units/s and
    deals Calc1 = 13/20/30 x AD + 3/5/7 x AP (past 11 stacks the extra damage is spread over the 11 visible orbs:
    Stack x Calc1 in total). Physical; crits only with Precision.
  - **Assumed:** orb i spawns at the chrono's i-th projectile time (MissileSelector.i -> i-th module); orbs fly her
    attack range (4 hexes).
