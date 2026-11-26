# Graves (4-cost AttackFighter) · `DA_Graves19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6037882.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6037882.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Beach Pop, Renegade
- **HP** 1100 / 1980 / 3564 · **AD** 85 / 127.5 / 191.25 · **AS** 0.6 · **Range** 2 · **Armor** 60 · **MR** 60 · **Mana** 0 / 30

### Ability: Left Hand Free

> For the next 2 attacks, gain 125% Attack Speed, dash to targets, and replace attacks with a cone of 5 bullets that deal 42/63/325 × AD + 5/7/35 × AP physical damage each. On kill, empower an additional attack.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 85 | 127.5 | 191.25 |
| ADDamage | 42 | 63 | 325 |
| NumAttacks | 2 | 2 | 2 |
| APDamage | 5 | 7 | 35 |
| AttackSpeed | 1.25 | 1.25 | 1.25 |
| NumMissiles | 5 | 5 | 5 |
| ExtraAttackPerKill | 1 | 1 | 1 |
| ConeWidth | 500 | 500 | 500 |
| OnHitEffectivenessPerBullet | 0.6 | 0.6 | 0.6 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 42/63/325 × AD + 5/7/35 × AP
- `AttackSpeedCalc1` = 1.25 + 1
- `PhysicalDamageCalc2` = ? × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Graves19_Attack`: launch 0.12 s (3.6 ticks); animation length 1.4667 s (44 ticks); release at base AS 0.1364 s (4.09 ticks)
- Attack projectile: DA_Graves19_AutoAttackProjectile, speed 3000 units/s
- Spell `GA_Graves19_Spell` (chrono `–`): cast ends 0 s (0 ticks), next attack can start 0.0333 s (1 ticks), mana lock removed –; ended by `FinishCasting via activate`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Graves19_Attack` | Chronos | 1.3 | CustomLaunchAttack1 0.12, LaunchAttack 0.12, CustomEventOnAttack1 0.52, Unlock 0.5864 |
| `CD_Graves19_Dash` | Chronos | 3.2951 | Arrive 0.3964 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Graves19_Spell`, `GA_ShopEvents`, `GA_Graves19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Graves19_Spell.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: GA_Graves19_Passive.txt
- `IsAttack`: damage flagged as an attack (or checked for it): GA_Graves19_Passive.txt
- `LaunchAttack`: launches or listens for attacks: GA_Graves19_Passive.txt, GA_Graves19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: GA_Graves19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Graves19_Spell.txt

### Changed since `rls-19.1.0.6028987.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-21, `set19champs.Graves`, D1); stats, attack rhythm, the cast, the AS
  buff's end, the mana lock and the dash's delay checked on VOD8 at 5-7 (E1-E3)
- Keep in the simulator: **not yet** (owner, 2026-11-21: needs more information). The class and test_graves.py stay;
  he is left out of `set19champs.champ_list` until the questions in docs/OPEN-QUESTIONS.md 7ad are answered

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (1,100 HP, 0 / 30, AD 85, 2 Hex; AS 0.82 = 0.6 x 1.36 with the stage-5 Fighter bonus and Aphelios's Heartsteel bonus; armor / MR 68 from the board) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackFighter: 10 per attack, no regen | confirmed (+10 steps 27-28 ticks apart at AS 1.09, nothing between) | E2 |
| Q3 | First attack at combat start: when does it land? | G3: released on tick 4 | not seen (PvE: the monster walks in) | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.12 s (3.6 ticks) | consistent (heals 4 ticks after each mana step: release + flight to a large monster) | E2 |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 (bUseRateScalingThreshold, no threshold) | predicted | |
| Q6 | Projectile travel time (ranged only) | speed 3000; bullets 2500 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 1 tick (instant: FinishCasting on activation); after a dash, the 'Arrive' tick (12) | confirmed (AS buff's end 33 ticks after the in-place cast, 44 after the dash cast: engine 33 / 44) | E3 |
| Q8 | Does the cast time scale with attack speed? | no | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | at the 2nd empowered attack's CustomEventOnAttack1 (0.52 s into it), with the AS buff's end | confirmed (no mana from the empowered attacks; the first +10 after a cast is the next normal attack) | E3 |
| Q10 | Does the mana lock scale with attack speed? | through the attack period only (two empowered attacks at +125%) | confirmed at AS 1.84 | E3 |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 (no GE_SimulateLaunchAttack); each empowered attack is a custom launch, its first bullet to hit the attack (IsAttack) | predicted | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | 5 bullets x (ADDamage x AD + APDamage x AP) per empowered attack, each on the first enemy in its path; on-hit at 0.8 per bullet | timing consistent (a heal 18 ticks after the dash cast: the first volley; engine lands 19); amounts predicted | D1, E3 |
| Q14 | Passives and other mechanics that need modelling | the dash to the hex where most bullets hit (passive) | implemented (D1); the dash on a target change and the extra attack per kill: not applicable (dummies never move or die) | D1, E3 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-21 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD8 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-21-2026_12-18-17-802/` `...PBE_11-21-2026_13-2-9-650.mp4`
(owner's game, 2026-11-21, 60 fps). Client rls-19.1.0.6013636 (not exported; owner: it only fixed a Graves crash in
premade lobbies), so 6011486 is assumed; nothing below disagrees with it. Graves 1 star at 5-7 (PvE: a large
monster); Heartsteel (3) with Aphelios fielded (AS x 1.06), Beach Pop and Renegade inactive (1 member each). Mana and
AS from `tools/vod_text_changes.py --field mana` / `--field as`; items by icon (normalised correlation against the
texture dump) and by the stats they add.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 32:01-32:13 (5-7 planning) | 60 | inspection panel | no items: 1,100 / 1,100, 0 / 30, Front, 2 Hex, AD 85, armor / MR 68, AS 0.82; items placed before combat: Edge of Night (icon 0.91), Bloodthirster (0.90), Infinity Force (by its stats: +30% AD / AP, +30 armor / MR, +300 HP); then 1,400 HP, AD 132 (55%), AP 55%, armor / MR 118, AS 1.09 | engine (`test_vod8_5_7_panel`, stage 5, Heartsteel (3) with Aphelios): AS 0.6 x (1 + 0.3 + 0.06 + 0.15 + 0.3) = 1.086, AD 131.75, AP 1.55, 1,400 HP; under the cast 1.836 (VOD 1.84) | Q1 |
| E2 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 f115916-116034 (5-7) | 60 | mana text, HP text | +10 at f115916, 115972, 116026 (28, 27 ticks apart; no regen); his 43% omnivamp heals 8 frames after each (+59, +42, +42) | engine (`test_vod8_5_7_casts`): attacks 27 / 28 ticks apart at AS 1.086 | Q2, Q4 |
| E3 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 f116026-116309 (5-7) | 60 | AS text, mana text | cast 1: mana 20 -> 0 and AS 1.09 -> 1.84 on f116026; heal +89 at f116062 (+18 ticks); AS back to 1.09 at f116114 (+44); first +10 at f116124 (+49). Cast 2 (f116233): AS back at f116299 (+33); first +10 at f116309 (+38). The dash is not visible in the melee; the 11 extra ticks on the first cast are its 'Arrive' | engine (`test_vod8_5_7_casts`): cast 1 dashes 1 hex, attacks start on the 'Arrive' tick (12), AS off at +44; cast 2 from that hex, no dash, AS off at +33: both exact. First mana +48 / +37 (VOD +1 on both, T10). First volley released +16, lands +19 at 1 hex (VOD heal +18; the monster is large) | Q7, Q9, Q10, Q13, Q14 |

## Decisions and notes

- 2026-11-21, D1 (implemented, `set19champs.Graves`; its docstring cites the scripts):
  - **Cast (GA_Graves19_Spell):** instant (FinishCasting on activation; it cancels an attack under way). Mana lock,
    GE_GenericGetEmpoweredAutoAttackTag and GE_Graves19_AttackSpeedBuff (AttackSpeed MultiplyAdditive 1 + AttackSpeed
    row, Channel1). Each custom launch counts an attack; at the CustomEventOnAttack1 of the NumAttacks-th
    (0.52 s into its animation, at the attack period: G2) the buff, the empower and the mana lock end (E3: 33 ticks
    after an in-place cast). ExtraAttackPerKill: dummies never die.
  - **Attack:** CD_Graves19_Attack's AttackGroup: EmpoweredAttack (the tag: CustomLaunchAttack1 0.12 s,
    CustomEventOnAttack1 0.52 s, of 1.4333 s) or SequentialAttack (LaunchAttack 0.12 s of 1.4667 s, two identical
    modules). The snapshot lists only the normal one (ledger P14); both release at 0.12 s, and the lengths differ only
    below AS 0.70, which the +125% empowered attacks never reach.
  - **Bullets (GA_Graves19_Passive 0x1826, 0xeb5):** NumMissiles CD_Graves19_ConeProjectile 'SpellMis' (2500 units/s)
    from him to points TotalRange = min(AttackRange x 214.5 + 200, 2300) ahead, spread ConeWidth across; each is
    destroyed on its first overlap with an enemy, which takes GE_Graves19_Damage (the first bullet to hit anything:
    IsAttack) or GE_Graves19_DamageNoIsAttack: PhysicalDamageCalc1, physical, AppliesOnSpell, AppliesOnHit at
    OnHitEffectivenessPerBullet, crit only with Precision (Renegade gives it). Simulated: a dummy is in a bullet's path
    when its centre is within ProjectileWidth / 2 (125, the script's 250 for the dash's sort; P15 b) of it. The
    bullet's own box is 2 x 55 wide; units' size is not in the data.
  - **Dash (passive, on the cast's Combat.Casting tag):** DetermineHexToDashTo: unoccupied hexes (his own included)
    within AttackRange of the target, nearest him first, then TR_Sort_SlotForGravesStyleShotgun (the bullets whose
    250-wide rectangle from that hex holds any unit, 0 unless one holds the target; decoded from the FModel export).
    Another hex: attacks blocked, CD_Graves19_Dash; 'Arrive' (the movement module's end, 0.3964 s, a fixed time as
    Vayne's 'MovementComplete') unblocks them, and the first empowered attack starts on that tick (E3: 44 vs 33; the
    build's +1 after FinishCasting does not apply). With a range bonus the game sorts by safety first: not
    simulated. On the page: 1-2 targets, one hex forward (3 bullets on the target from 2 hexes, 5 from 1); 3-4, beside
    the target; 5+, no dash (the layout's 5th dummy stands between him and the target, and takes every bullet).
  - Open questions: docs/OPEN-QUESTIONS.md 7ad.
