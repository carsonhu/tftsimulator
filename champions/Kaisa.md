# Kai'Sa (3-cost AttackMarksman) · `DA_Kaisa19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5983251.Set19.Shipping.pbe.notes; edits here are overwritten -->
## Client data: build `rls-19.1.0.5983251.Set19.Shipping.pbe.notes`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 3, pool 18; traits: K/DA, Trickshot
- **HP** 650 / 1170 / 2106 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 5 · **Armor** 35 · **MR** 35 · **Mana** 0 / 30

### Ability: Make it Rain

> Passive: Every 3 attacks, fire 3 missiles that deal 36/54/85 × AD + 6/9/15 × AP physical damage. 
> 
> Active: Gain 15% Attack Speed for the rest of combat.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| HexSearchRangeAroundCurrentTarget | 2 | 2 | 2 |
| NumAttacksForMissiles | 3 | 3 | 3 |
| NumMissiles | 3 | 3 | 3 |
| ADDamage | 33 | 50 | 80 |
| APDamage | 6 | 9 | 15 |
| ASOnCast | 0.15 | 0.15 | 0.15 |
| ASDuration | 60 | 60 | 60 |
| MaxSecondaryTargets | 2 | 2 | 2 |
| PercentMissilesOnCurrentTarget | 0.5 | 0.5 | 0.5 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 36/54/85 × AD + 6/9/15 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Kaisa19_Attack`: launch 0.1361 s (4.08 ticks), variants 0.1361, 0.169, 0.3219, 0.3255, 0.3425, 0.3578, 0.4242; animation length 2.8333 s (85 ticks); release at base AS 0.1361 s (4.08 ticks)
- Attack projectile: DA_Kaisa19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Kaisa19_Spell` (chrono `–`): cast ends 0 s (0 ticks), next attack can start 0.0333 s (1 ticks), mana lock removed –; ended by `FinishCasting via activate`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Kaisa19_Attack` | Chronos | 1.3955 | LaunchAttackVariant2 0.1361, LaunchAttackVariant1 0.169, LaunchAttackVariant1 0.3219, LaunchAttackVariant2 0.3255, LaunchAttackVariant2 0.3425, LaunchAttackVariant2 0.3578, LaunchAttackVariant1 0.4242, Unlock 0.56, Unlock 1.04, Unlock 1.1066, Unlock 1.1464 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Kaisa19_Passive`, `GA_Kaisa19_TrickshotHandler`, `GA_Trickshot19_HandleAutoAttackBounce`, `GA_PlayChronoOnTraitActivation`, `GA_AutoAttack`, `GA_LaunchProjectileAttack_Trickshot19`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Kaisa19_Spell`, `GA_ShopEvents`, `GA_ForceSequentialAttack`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Kaisa19_Passive.txt
- `AttackSpeed`: reads or changes attack speed: Abilities/GA_Kaisa19_Spell.txt

### Changed since `rls-19.1.0.5973071.Set19.Shipping.pbe`

- row ADDamage: 36 / 54 / 85 -> 33 / 50 / 80

<!-- AUTO END -->

## Status

- Worksheet status: **implemented 2026-11-17** (`set19champs.Kaisa`, D1; tests `test_kaisa.py`)
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | predicted | |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackMarksman | **consistent**: +10 per attack, no regen; the steps match the engine's releases | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.1361 s (4.08 ticks) | **refuted for the single launch**: 4 sequential animations, LowAS below 1.75 AS (0.3255/0.4242/0.3578/0.4242 s), fast from 1.75 (B13) | E2, P13 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | **consistent**: the 2.6-2.8 s animations never stretch at her periods; the fast set from 1.75 AS fits the 102-frame cycle after the 9th cast | E2 |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 0.0333 s (1 ticks) | **consistent**: the cast doesn't interrupt the rhythm (T12) | E2 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | predicted | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | **no** (no Combat.Attacking cancel; rhythm unbroken, T12) | E2 |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | spell **confirmed**: +15% AS per cast, stacking (panel 0.86 ... 2.10 = 0.75 x (1 + 0.15k)); missiles implemented from the script (D1), their damage not yet checked | E3, script |
| Q14 | Passives and other mechanics that need modelling | see ability text | missiles every 3 launches (D1); Trickshot ricochets (B12); K/DA (B14) | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-17 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 11:12 (f40506) | 60 | inspection panel | 1★, Infinity Edge + 2 Deathblades: AD 87, bonus AD 189%, AS 0.75, crit 60%, 811 HP, 0/30 mana; Trickshot (2), K/DA 1/3 (inactive) | stats as built (I5) | Q1 |
| E2 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 f40531-42287 (`tools/vod_text_changes.py`, mana) | 60 | attack releases (+10 mana each) | first gaps 88, 76 frames at 0.75 AS; 3-attack cycles shrink with each cast; f41895-41986 a 75-frame gap as her HP drops 811 -> 698 (likely CC; left out) | engine within 1 tick for 11 releases, then +4 by the 20th (T13); casts don't break the rhythm (T12) | Q2, Q4, Q5, Q7, Q12 |
| E3 | 2026-11-17 | rls-19.1.0.5973071 | VOD3 f40506-42261 (AS text) | 60 | AS after each cast | 0.75, 0.86, 0.97, 1.09, 1.20, 1.31, 1.42, 1.54, 1.65, 1.76, 1.88, 1.99, 2.10, changing on the cast frame | 0.75 x (1 + 0.15k): MultiplyAdditive, stacking | Q13 |

## Decisions and notes

- 2026-11-17, D1 (implemented, `set19champs.Kaisa`):
  - **Passive (GA_Kaisa19_Passive):** every NumAttacksForMissiles (3) attack launches, NumMissiles (3) missiles fire
    at once (CD_Kaisa19_SpellMissile, 1900 units/s), alternating by a running count between her target and up to 2
    enemies within 2 hexes of it. Each deals ADDamage x AD + APDamage x AP physical (spell crit with Precision) and
    ricochets with Trickshot (CD_Kaisa19_SpellMissileTrickshot, x RichochetDamage^k).
  - **Spell (GA_Kaisa19_Spell):** +ASOnCast as MultiplyAdditive (+15% of base) for 60 s, stacking; it finishes on
    activation (T12).
  - **Attacks:** 4 sequential animations, LowAS or fast at 1.75 AS (B13).
  - **Assumed:** each missile flies its own target's distance on the dummy layout (`layout.py`; owner, 2026-11-17):
    5 hexes to her target, 6 to the default layout's dummy next to it; identical dummies make the split irrelevant
    to the total.
- 2026-11-18, Day 1 PBE patch notes (rls-19.1.0.5983251, its archives encrypted: the page's build rls-19.1.0.5983251.Set19.Shipping.pbe.notes, B33): ADDamage 36/54/85 -> 33/50/80. Timing and everything else unchanged from rls-19.1.0.5973071 until a readable build says otherwise.
