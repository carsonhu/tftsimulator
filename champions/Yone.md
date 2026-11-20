# Yone (4-cost AttackFighter) · `DA_Yone19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6005555.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6005555.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Heartsteel, Slayer
- **HP** 1150 / 2070 / 3726 · **AD** 55 / 82 / 123 · **AS** 0.85 · **Range** 1 · **Armor** 70 · **MR** 70 · **Mana** 0 / 50

### Ability: Two Sides

> Passive: This ability scales Attack Damage or Ability Power, whichever is higher. Attacks deal 55/82/123 × AD physical damage.
> 
> Active: Rapidly strike the target and up to 2 nearby enemies 10/10/30 times, each dealing 35/55/400 × AD physical damage. After the assault, unleash a massive slash that deals 175/265/1500 × AD physical damage to target.
> 
> Heartsteel Upgrade: Casts strike 2 more times and ignore 25%25% of Armor.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 55 | 82 | 123 |
| NumSpirits | 10 | 10 | 30 |
| PrimaryDamage | 35 | 55 | 400 |
| TanksBonusDamage | 0 | 0 | 0 |
| NumBonusEnemies | 2 | 2 | 2 |
| AOERangeAroundCurrentTarget | 2 | 2 | 4 |
| PercentStrikesOnTarget | 0.5 | 0.5 | 0.5 |
| SecondaryDamage | 175 | 265 | 1500 |
| HeartsteelStan_ExtraClones | 2 | 2 | 2 |
| HeartsteelStan_ArmorIgnore | 0.25 | 0.25 | 0.25 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 35/55/400 × AD
- `PhysicalDamageCalc2` = 175/265/1500 × AD
- `PhysicalDamageCalc3` = 55/82/123 × AD
- `MagicDamageCalc1` = 35/55/400 × AP
- `MagicDamageCalc2` = 175/265/1500 × AP
- `MagicDamageCalc3` = 55/82/123 × AP
- `GenericCalc1` = 1 + -0.25

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Yone19_AttackNew`: launch 0.26 s (7.8 ticks), variants 0.26, 0.323, 0.353, 0.3542; animation length 2.5 s (75 ticks); release at base AS 0.26 s (7.8 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Yone19_Spell` (chrono `switch(Temp_bool_Variable_1){false: Temp_object_Variable_4; true: Temp_object_Variable_3; default: K2Node_Select_Default_1}`): cast ends –, next attack can start –, mana lock removed –; **script reads attack speed**; **no cast end found**
  - notes: chrono not found switch(Temp_bool_Variable_1){false: Temp_object_Variable_4; true: Temp_object_Variable_3; default: K2Node_Select_Default_1} ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Yone19_AttackNew` | Chrono | 2.5 | LaunchAttack 0.26, LaunchAttack 0.323, LaunchAttack 0.353, LaunchAttack 0.3542, Unlock 0.9864, Unlock 1 |
| `CD_Yone19_CastAnim` | Chrono | 9.9446 | Default 0, Loop 0.2966, StartStrikes 0.4992 |
| `CD_Yone19_CastAnim_Part2` | Chrono | 0.7915 | DealDamage 0.3453, Unlock 0.6589 |
| `CD_Yone19_Celebration` | Chrono | 12.2141 | Default 0, Loop 3.0894 |
| `CD_Yone19_SpellMissile` | Chrono | 0.3999 | Damage 0.0576, Damage 0.0793, Damage 0.0831, Damage 0.1619 |
| `CD_Yone19_CastAnimAlt` | Chrono/OLD | 9.9957 | Default 0, Loop 0.3478, StartStrikes 0.5504 |
| `CD_Yone19_CastAnim_Part2_Alt` | Chrono/OLD | 1.0058 | DealDamage 0.7784, Unlock 0.9879 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Yone19_Passive`, `GA_ForceSequentialAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_Yone19_LaunchMeleeAttack`, `GA_Yone19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Yone19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Yone19_LaunchMeleeAttack.txt, GA_Yone19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): GA_Yone19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: GA_Yone19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Yone19_Spell.txt

### Changed since `rls-19.1.0.5995286.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Yone`, D1); the AP form, the cast's timelines and the
  strike / slash damage ratio checked on VOD6 (E1-E3)
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has him at 2-1 (AP) and 2-2, 2-4 (AD), with Heartsteel)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (HP 1225 = 1150 + Heartsteel's Sett 75; mana 50; armor / MR 70 + bonuses) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackFighter (AP form: MagicFighter): 10 per attack | confirmed (+10 steps, casts at 50) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.26 s (7.8 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable | |
| Q7 | Cast time: cast start to the next attack starting | StartStrikes + (strikes - 1) x the slash interval + Part2 'Unlock', + 1 tick | consistent with the non-Alt timelines: the next attack's mana 64 / 58.5 / 56 ticks after the cast at ~1.3 AS (engine ~54 + windup); the Alt ones would give ~72 | E2, E3 |
| Q8 | Does the cast time scale with attack speed? | yes: the slash interval (GetTimeBetweenSlashes) | predicted (script) | D1 |
| Q9 | Mana lock: from cast start, when can mana be gained again? | the cast's end ('Unlock') | predicted (no regen to show it) | |
| Q10 | Does the mana lock scale with attack speed? | with the cast (as Q8) | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 1 GE_SimulateLaunchAttack per 3 strikes | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | strikes PrimaryDamage x AD (AP), final SecondaryDamage x AD (AP) | consistent: strike 36 / slash 182 = 0.2 = 35 / 175 under one MR | E3 |
| Q14 | Passives and other mechanics that need modelling | the AD / AP form; Heartsteel Bias +2 strikes, 25% armor (MR) ignored | modelled; the form confirmed (AP 120% > AD: Magic Fighter, magic numbers) | E1, E3 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |
| Q16 | Which cast timelines play? | UseAltAnims (decoded default True) -> CD_Yone19_CastAnimAlt / _Part2_Alt (folder OLD) | **the non-Alt ones** (CD_Yone19_CastAnim / _Part2): VOD6's strikes and slash keep one display offset with them, not with Alt | E3 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18, 60 fps; client rls-19.1.0.5986652, not exported: the simulator's newest is 5986094). Round 2-1:
Yone 1 star with two AP items (AP form); Heartsteel on the board (Sett fielded). Rounds 2-2 and 2-4 (AD form,
Heartsteel bonus) not measured yet. Mana from `tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 8:50 (round 2-1, planning) | 60 | inspection panel | 1225/1225, 0/50, range 1 hex, Front, **Magic Fighter**; AD 55, AD 0%, AP 20%, armor 93, MR 93, AS 1.15, crit 25%, omnivamp 5% | HP 1150 + 75 (Sett); AP 1.2 > AD 1.0: AP form (DA_Yone19_APOverride's MagicFighter role) | Q1, Q14 |
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f32767-33812 | 60 | mana text | casts f32948, f33202, f33421, f33621; the next +10 at f33076, f33319, f33533 (+128, +117, +112 frames) | 10 per attack; the next attack 64 / 58.5 / 56 ticks after a cast, attacks ~21-24 ticks apart before it (~1.3 AS) | Q2, Q7 |
| E3 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 9:09.0-9:11.4 (the board every 1/15 s), cast f32948 (9:09.13) | 60 | strike and slash damage numbers | magic 36s from ~9:09.87 to ~9:10.45; the final slash 182 at ~9:10.73 | the first strike ~0.74 s and the slash ~1.60 s after the panel's cast frame: non-Alt predicts 0.56 / 1.45 s (one ~0.16 s offset), Alt 0.61 / 1.93 s (no single offset). 36 / 182 = 0.198 = 35 / 175 | Q7, Q13, Q16 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Yone`):
  - **Form (GA_Yone19_Passive):** AD form while AttackDamage >= AbilityPower, else AP form (GE_Yone19_MagicForm,
    DA_Yone19_APOverride: role MagicFighter, Magic calcs); re-checked on every AD / AP change. Simulated: checked at
    each attack and cast.
  - **Attacks (GA_Yone19_LaunchMeleeAttack):** AutoAttackDamage x AD physical; AP form x AP magic (MagicDamageCalc3).
  - **Cast (GA_Yone19_Spell):** commit, mana lock; CD_Yone19_CastAnim (Q16). 'StartStrikes' (0.4992 s): a strike
    at once and every GetTimeBetweenSlashes = 0.085 / (1 + Min((Max(AS / base AS, 1) - 1) x 0.5, 2)) s until
    NumSpirits strikes; each plays CD_Yone19_SpellMissile and deals GE_Yone19_Damage (_Magic) = Calc1 x
    TankDamageMult at its 'Damage' event; even strikes on the target, odd ones on the next of up to 2 enemies within
    2 hexes of it (row distance; refilled; the target if none). Every 3rd strike: GE_SimulateLaunchAttack. After the
    last: CD_Yone19_CastAnim_Part2: 'DealDamage' (0.3453 s) GE_Yone19_FinalDamage (_Magic) = Calc2 on the target;
    'Unlock' (0.6589 s) ends the cast and the lock.
  - **Heartsteel Bias:** +HeartsteelStan_ExtraClones strikes, the interval x 10 / 12, and GE_Yone19_ArmorIgnore
    (_MRIgnore) on his spell damage: the target's armor (MR) x 0.75.
  - **Simulated:** a strike's damage at the SpellMissile's (k mod 4)-th 'Damage' time (the selector-to-group map is
    not decoded; 0.06-0.16 s); the timer on whole ticks; dummies are not tanks (TankDamageMult 1).
