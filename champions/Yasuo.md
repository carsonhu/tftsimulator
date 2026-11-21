# Yasuo (4-cost AttackFighter) · `DA_Yasuo19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 4, pool 10; traits: True Damage, Slayer
- **HP** 1100 / 1980 / 3564 · **AD** 60 / 90 / 135 · **AS** 0.85 · **Range** 1 · **Armor** 65 · **MR** 65 · **Mana** 0 / 30
- **Unlock**: 6 unique star levels of True Damage or Slayer champions.

### Ability: Last Breath

> Dash and thrust forward, dealing 180/270/1400 × AD physical damage to enemies in a line.
> 
> Every 3rd cast, knock up the target and deal 400/600/2500 × AD physical damage. Then slam them down, dealing 1 × GenericCalc1 + 1 × GenericCalc2 physical damage to enemies within 1/1/2 Hex.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 60 | 90 | 135 |
| UltDamageAD | 400 | 600 | 2500 |
| SlashDamageAD | 180 | 270 | 1400 |
| SlashHexLength | 2 | 2 | 2 |
| UltDamageAOEAD | 180 | 270 | 1500 |
| AOEHexRadius | 1 | 1 | 2 |
| UltDamageAOEAP | 30 | 45 | 200 |
| TargetSearchRadius | 1 | 1 | 1 |
| NumCastsToUlt | 3 | 3 | 3 |
| UltKnockupDuration | 1 | 1 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 180/270/1400 × AD
- `PhysicalDamageCalc2` = 400/600/2500 × AD
- `GenericCalc1` = 180/270/1500 × AD
- `GenericCalc2` = 30/45/200 × AP
- `PhysicalDamageCalc3` = 1 × GenericCalc1 + 1 × GenericCalc2

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Yasuo19_Attack`: launch 0.26 s (7.8 ticks), variants 0.26, 0.2775, 0.2823; animation length 1.6333 s (49 ticks); release at base AS 0.26 s (7.8 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Yasuo19_Spell` (chrono `CD_Yasuo19_UltWhirlwind`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Yasuo19_Attack` | Chronos | 1.6 | LaunchAttack 0.26, LaunchAttack 0.2775, LaunchAttack 0.2823, Unlock 0.6533, Unlock 0.6664 |
| `CD_Yasuo19_BaseSpell` | Chronos | 0.8709 | Default 0, Thrust 0.2204, Damage 0.4115, Unlock 0.8568 |
| `CD_Yasuo19_BaseSpell_NoDash` | Chronos | 0.716 | Damage 0.194, Unlock 0.6409 |
| `CD_Yasuo19_UltKnockup` | Chronos | 1.4355 | Default 0, Knockup 0.1273, Damage1 0.1888, Damage2 0.5278, Slam 1.1514, ReturnToHex 1.2504, Unlock 1.4317 |
| `CD_Yasuo19_UltNoKnockup` | Chronos | 1.4355 | Default 0, Knockup 0.1273, Damage1 0.1888, Damage2 0.5278, Slam 1.1514, ReturnToHex 1.2504, Unlock 1.4317 |
| `CD_Yasuo19_UltWhirlwind` | Chronos | 0.9999 | FireWind 0.3025 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_TrueDamage19_PlayChronoOnTraitActivation`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Yasuo19_Spell`, `GA_ShopEvents`, `GA_Yasuo19_SpellIndicatorHandler`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Yasuo19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Yasuo19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Yasuo19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Yasuo19_Spell.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-21, `set19champs.Yasuo`, D1); mana, attack rhythm and every cast's lock
  checked on VOD8 at 4-1 and 4-3 (E1-E3)
- Keep in the simulator: **yes** (owner, 2026-11-21: VOD8 recorded for him)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (with items: HP 1,400, AS 1.62, crit 80%, armor / MR 95, 0/30); bonus AD 108% vs the items' 101%: open | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackFighter: 10 per attack | confirmed (+10 per attack, +1/s from Hand of Justice) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open (VOD8 4-1: ~17 frames after the HP shield appears; combat start not exact) | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.26 s (7.8 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | consistent (AS 1.62: the next attack lands 10 ticks after each lock end, engine 10) | E2 |
| Q6 | Projectile travel time (ranged only) | none | not applicable | |
| Q7 | Cast time: cast start to the next attack starting | NoDash 'Unlock' 0.6409 s + 1 tick; dash 0.8568 s; ult 1.4317 s | confirmed (all three locks on VOD8, to the tick) | E2, E3 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted (one AS seen) | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | End Spell at each chrono's 'Unlock': 20 / 26 / 43 ticks | confirmed (overflow shown 21 / 27 / 44 ticks after the filling attack = lock + T4) | E2, E3 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | base 0; ult 1 (GE_SimulateLaunchAttack at 'Slam'; +1 at a whirlwind's launch) | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | stab Calc1 on a 2-hex line; ult 2 x 0.5 x Calc2 on the target, slam Calc3 within AOEHexRadius | predicted (GEs read) | D1 |
| Q14 | Passives and other mechanics that need modelling | every 3rd cast is the ult (spell Stack, reset each combat) | confirmed (VOD8: ult locks on casts 3 and 6 of both fights) | E2, E3 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-21 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD8 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-21-2026_12-18-17-802/` `…PBE_11-21-2026_13-2-9-650.mp4`
(owner's game, 2026-11-21, 60 fps). Client rls-19.1.0.6013636 (patched 11:32 that day, not exported; owner: only a
Graves crash fix), so 6011486 is assumed. Yasuo 1 star with Hand of Justice, Infinity Edge and Infinity Force (icons
matched to the client textures), Slayer (4), True Damage inactive, stage 4. Mana from `tools/vod_text_changes.py
--field mana` (crops read by eye; changes that are only the HP text left out). "Filling attack" = the frame the bar
drops to 0 (the panel never shows a full bar); the cast is one tick later (T4).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 18:06 (round 4-1) | 60 | inspection panel | 1,568 / 1,400 (shield), 0/30, 1/s, 1 hex, Front, Attack Fighter; AD 125, bonus AD 108%, AP 66%, armor 95, MR 95, AS 1.62, crit 80%, omnivamp 22% | engine: HP 1400, AS 1.615, crit 0.8, AP 0.66, armor / MR 95, regen 1. Bonus AD: engine 101% (IE 35 + Infinity Force 30 + Hand of Justice 36), panel 108% (unexplained, same at 4-3) | Q1 |
| E2 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 f65152-66266 (4-1) | 60 | mana text | attacks +10 36-38 frames apart; fills at f65243, 65379, 65606, 65827, 65964, 66178; first change after each: +1 at f65285 (42 fr), +3 at 65433 (54), +5 at 65694 (88), +8 at 65869 (42), +9 at 66018 (54), +2 at 66266 (88); the next attack 20 frames after each of the first five | casts 3 and 6 are ults (44 ticks = 'Unlock' 43 + T4); the others alternate NoDash (21 = 20 + 1) and dash (27 = 26 + 1); casts 136-137 frames apart (engine 68 ticks, NoDash); next attack 10 ticks after the lock (engine 10) | Q2, Q5, Q7, Q9, Q14 |
| E3 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 f75101-76400 (4-3) | 60 | mana text | panel closed f75113-75193 and f75325-75387; fills (first change after) f75465 (+4, 88 fr), 75647 (+6, 42), 75804 (+8, 43), 75940 (+9, 88), 76104 (+1, 43), 76305 (+3, 41) | the first two casts fall where the panel is closed (f75193: three attacks after combat start, its overflow +1 at f75235 = 21 ticks; ~f75327); then ult, base, base, ult, base, base: the Stack resets each combat (GE_IncSpellStackBy1_CombatOnly unapplied after CombatDeparture) | Q9, Q14 |

## Decisions and notes

- 2026-11-21, D1 (implemented, `set19champs.Yasuo`):
  - **Cast (GA_Yasuo19_Spell):** commit, Stack +1 (GE_IncSpellStackBy1_CombatOnly), mana lock (0x2db9). Stack a
    multiple of NumCastsToUlt (3): Ultimate Spell and Clear Spell Stacks (0x2b59-0x2d16); else Base Spell. End Spell
    (0x1e99) at each chrono's 'Unlock' removes the mana lock and finishes the cast.
  - **Base:** dash hex = first of (hexes within TargetSearchRadius of the target + his own), sorted by distance to the
    board centre, then by enemies in a SlashHexLength-hex line through the target (width 150). His own hex:
    CD_Yasuo19_BaseSpell_NoDash (Damage 0.194, Unlock 0.6409 s); else CD_Yasuo19_BaseSpell (Damage 0.4115, Unlock
    0.8568 s). Damage: GE_Yasuo19_StabDamage on the enemies in a rectangle from him to the target, SlashHexLength x
    214.5 long, 150 wide (his target if none): PhysicalDamageCalc1 = SlashDamageAD x AD, physical, AOE, on-spell,
    AppliesOnHit.IsAttack, crit only with Precision.
  - **Ultimate:** target within 1 hex: CD_Yasuo19_UltKnockup (no whirlwind). Knockup 0.1273 s; Damage1 0.1888 s and
    Damage2 0.5278 s: GE_Yasuo19_UltDamageTarget each 0.5 x PhysicalDamageCalc2 (UltDamageAD x AD) on the target
    (on-spell only); Slam 1.1514 s: GE_SimulateLaunchAttack and GE_Yasuo19_UltDamageAOE on the enemies within
    AOEHexRadius of the target (PhysicalDamageCalc3 = UltDamageAOEAD x AD + UltDamageAOEAP x AP, AOE, on-spell,
    IsAttack); ReturnToHex 1.2504; Unlock 1.4317 s.
  - **Simulated:** the page's second target stands straight behind the first (layout.py), so his own hex is always
    the best line: every base cast is NoDash (VOD8 shows both kinds against moving enemies; the dash's lock is 6
    ticks longer). The stab hits the target and the enemy behind it (2 x 214.5 reaches 2 hexes, as Kayn's 429-unit
    swipe, owner). Damage tagged AppliesOnHit.IsAttack (stab, slam) gives every enemy hit the on-hit events, as Gnar's
    rock. No whirlwind (target adjacent). Open questions: docs/OPEN-QUESTIONS.md 7z.
