# Viego (3-cost AttackFighter) · `DA_Viego19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5995286.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5995286.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 3, pool 18; traits: Pentakill, Choreographer, Slayer
- **HP** 850 / 1530 / 2754 · **AD** 60 / 90 / 135 · **AS** 0.8 · **Range** 1 · **Armor** 55 · **MR** 55 · **Mana** 0 / 40

### Ability: Singled Out

> Summon 10 + 1 × GenericCalc2 swords around the target. After a brief delay, impale them, dealing 34/51/82 × AP + 3/5/7 × AP physical damage per sword.
> 
> Every 8 takedowns, gain a permanent sword. (Current Takedowns: ⟨live⟩)

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 60 | 90 | 135 |
| KillsToGainSword | 8 | 8 | 8 |
| SwordPerStack | 1 | 1 | 1 |
| NumBaseSwords | 10 | 10 | 10 |
| DamagePerSwordAD | 34 | 51 | 82 |
| DamagePerSwordAP | 3 | 5 | 7 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 34/51/82 × AP + 3/5/7 × AP
- `GenericCalc1` = 10 + 1 × GenericCalc2

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Viego19_Attack`: launch 0.3 s (9 ticks); animation length 2.9 s (87 ticks); release at base AS 0.3 s (9 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Viego19_Spell` (chrono `CD_Viego19_SpellCast`): cast ends 1.8333 s (55 ticks), next attack can start 1.8667 s (56 ticks), mana lock removed 1.8333 s (55 ticks); ended by `FinishCasting via OnEventBegin:CD_Viego19_SpellCast:Unlock`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Viego19_Attack` | AnimChronos | 2.9 | LaunchAttack 0.3, Unlock 0.8 |
| `CD_Viego19_SpellCast` | AnimChronos | 1.8557 | FireSwords 1.0579, Unlock 1.832 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Viego19_SwordStacking`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Viego19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Viego19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Viego19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Viego19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Viego19_Spell.txt

### Changed since `rls-19.1.0.5986094.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Viego`, D1); panel and the cast's rhythm checked against
  VOD5; Slayer's attack speed against VOD5's second fight
- Keep in the simulator: **yes**

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed with his items (1★, 2★) | E1, E3 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackFighter | confirmed: 10 per attack, no role regen (Blue Buff's 6/s) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3 s (9 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 1.8667 s (56 ticks) | confirmed: the next attack's mana 65 ticks after the cast (56 + 9-tick windup), engine 65 | E2 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.8333 s (55 ticks) | consistent: mana shown again 55 ticks after the cast | E2 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | predicted: one GE_SimulateLaunchAttack per cast, at FireSwords | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read, D1): both coefficients scale **AP** in the client data; no damage number read yet | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | takedown swords: from the page's Takedowns, +SwordPerStack per KillsToGainSword (2026-11-19, below); none gained in a fight (dummies never die); Pentakill (B25), Slayer (B29), Choreographer (B30) implemented | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD5 (`…PBE_11-18-2026_0-57-11-500.mp4`, session folder 0-33-59-673, 60 fps), the owner's
PBE recording in the score mode, build `rls-19.1.0.5973071`. First fight: Viego 1★, round 1-7, combat start f24670 (Blue
Buff's +10). Ticks count from combat start.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 6:51 (f24660) | 60 | inspection panel | 850/850, 0/40, 6/s; AD 69, AP 15%, AS 0.96, crit 45%, armor 70, MR 90; Quicksilver, Blue Buff; Bodyguard (2) from the board; Pentakill, Choreographer, Slayer 1 each (inactive) | 0.8 x (1.05 Fighter stage 1 + 0.15), 60 x 1.15 AD: as built | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 f24670-25021 (`tools/vod_text_changes.py`, mana) | 60 | mana text | 10 (combat start), regen +1.5 at 3, 11, 18, 26, 33, 41, 48 (the first step 3 ticks in: G17), +10 at 20 and 52 (fills: cast); 2 at 108; +10 at 118, 147.5, ~175.5 (fills) | engine (Quicksilver, Blue Buff): the next attack 65 ticks after the cast (clip 65), then 29, 28 (clip 29.5, 28); mana lock 55 as built. His first attack came 11 ticks after the engine's (a walk) | Q2, Q7, Q9 |
| E3 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 9:16 (f33360) | 60 | inspection panel, round 2-1 | 2★, no items, 504/1530 HP; AD 104, AS 1.11, omnivamp 13%; Pentakill (3), Slayer (2), Bodyguard (2) active | Slayer: 0.8 x (1.05 + 0.2 x (1 + 1026/1530)) = 1.107 AS, 8% x 1.67 = 13% omnivamp: the missing-Health scaling as the trait text says (B29) | Q14 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Viego`):
  - **Spell (GA_Viego19_Spell):** mana lock; 10 swords (+ takedown swords: GenericCalc2, 0 against dummies) spawn
    around his target over 0.75 s; at FireSwords (1.0579 s) each flies into the target (CD_Viego19_SwordCollapse_Mis,
    a fixed-time projectile, taken as 0.25 s: G21) and deals GE_Viego19_SwordDamage; then one GE_SimulateLaunchAttack.
    Unlock (1.832 s) ends the cast (build: 55 / 56 ticks).
  - **Damage:** PhysicalDamageCalc1 in DA_Viego19's CalcComponent = DamagePerSwordAD x AbilityPower + DamagePerSwordAP x
    AbilityPower: both terms capture AP (the row name says AD; the tooltip shows AP twice). **Owner, 2026-11-18: the AD
    row scales with AD**, so each sword deals DamagePerSwordAD x AD + DamagePerSwordAP x AP. Physical, on-spell, crit
    only with Precision.
- 2026-11-18, Day 1 PBE patch notes, confirmed in the client build rls-19.1.0.5986094 (read from an FModel raw export, B34; it replaced the patch-notes stand-in, B33): DamagePerSwordAD 36/54/86 -> 34/51/82. Its timing is unchanged from rls-19.1.0.5973071.
- 2026-11-19, takedown swords (owner: Viego must scale with the page's Takedowns). GA_Viego19_SwordStacking counts
  each takedown in Stack (GE_Viego19_KillTracker) and applies GE_Viego19_SwordStacks at FMod(Stack, KillsToGainSword),
  whose return in UE is the whole quotient: Stack // 8. GA_Viego19_Spell reads GenericCalc2 as the cast starts and
  adds it to NumBaseSwords (NumTotalSwords). GenericCalc2's formula isn't in the build's calcs; the tooltip's
  "10 + 1 x GenericCalc2" (1 = SwordPerStack) and the script's plain sum agree while SwordPerStack is 1, so the
  simulator takes SwordPerStack x (takedowns // 8). Predicted from the scripts; no VOD check yet.
