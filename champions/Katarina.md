# Katarina (1-cost MagicFighter) · `DA_Katarina19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6018196.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6018196.Set19.Shipping.pbe`

- **Role** MagicFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Classical, Slayer
- **HP** 650 / 1170 / 2106 · **AD** 30 / 45 / 67.5 · **AS** 0.75 · **Range** 1 · **Armor** 35 · **MR** 35 · **Mana** 0 / 40

### Ability: Blade Sonata

> Twirl, slashing adjacent enemies for 120/180/285 × AP magic damage. Then, eviscerate the current target, dealing 240/360/610 × AP magic damage to them. Enemies hit are Captivated for 8 seconds. 
> 
> Captivated enemies grant bonuses to Classical champions.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| AoEDamageAp | 120 | 180 | 285 |
| CaptivateDuration | 8 | 8 | 8 |
| AoERadius | 1 | 1 | 1 |
| TargetDamageAP | 240 | 360 | 610 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 120/180/285 × AP
- `MagicDamageCalc2` = 240/360/610 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Katarina19_Attack`: launch 0.2918 s (8.75 ticks), variants 0.2918, 0.2985; animation length 1.5 s (45 ticks); release at base AS 0.2918 s (8.75 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Katarina19_Spell` (chrono `CD_Katarina19_CastAnimCombined`): cast ends 1.3 s (39 ticks), next attack can start 1.3333 s (40 ticks), mana lock removed 1.3 s (39 ticks); ended by `FinishCasting via OnEventBegin:CD_Katarina19_CastAnimCombined:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Katarina19_Attack` | CD_Katarina19_Attack | 1.4667 | LaunchAttack 0.2918, LaunchAttack 0.2985, Unlock 0.5867, Unlock 0.6 |
| `CD_Katarina19_CastAnimCombined` | CD_Katarina19_CastAnimCombined | 1.4499 | Default 0, Spin 0, CheckIfMove 0.2484, Movement 0.2995, Eviscerate 0.835, MovementEnd 0.8994, Unlock 1.2743, Eviscerate 1.285, Unlock 1.4251 |
| `CD_Katarina19_Move` | CD_Katarina19_Move | 0.5996 | MovementEnd 0.5271 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Katarina19_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Katarina19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Katarina19_Spell.txt

### Changed since `rls-19.1.0.6011486.Set19.Shipping.pbe`

- row CaptivateDuration: 5 -> 8
- row TargetDamageAP: 240 / 360 / 575 -> 240 / 360 / 610
- ability text changed

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Katarina`, D1); stats, mana and attack rhythm checked
  on VOD6 (E1-E2); the one VOD cast took the dash branch (E3); 2 stars at 3-2 on VOD8 (E4-E5): stats, attack
  rhythm and the no-dash cast lock match to the tick
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has her at 1-2)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above confirmed (HP 725 = 650 + Heartsteel's Sett 75) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicFighter: 10 per attack, no regen | confirmed (+10 steps, nothing between them) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open (VOD6's minions walk in) | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2918 s (8.75 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable | |
| Q7 | Cast time: cast start to the next attack starting | 1.3333 s (40 ticks) without the dash | confirmed without the dash (VOD8: 4th attack to the next 50 ticks, engine 50) | E3, E5 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.3 s (39 ticks) without the dash | predicted | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 (no GE_SimulateLaunchAttack) | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | spin AoEDamageAp x AP on enemies within 1 hex of her; eviscerate TargetDamageAP x AP on her target | eviscerate formula consistent (218 on a 10 MR minion = 240 / 1.1); spin predicted | E3, D1 |
| Q14 | Passives and other mechanics that need modelling | Captivate (5 s) on every enemy hit | modelled (Classical, traits/classical.py) | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18 18:15-18:40, 60 fps). The client patched to rls-19.1.0.5986652 at 16:20 that day and that build
isn't exported yet; the simulator's newest is 5986094, so a mismatch may be a 5986652 change. Round 1-2: Katarina 1
star, no items, Classical 1/2 and Slayer 1/2 (inactive), Heartsteel (1) with Sett fielded (+75 Health to the team, SettHealth); minions (armor and MR 10). Mana from
`tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 1:06 (round 1-2, combat start) | 60 | inspection panel | 725/725, 0/40, range 1 hex, Front, Magic Fighter; AD 30, AP 0%, armor 35, MR 35, AS 0.79, crit 25% | the simulator: AD 30, AS 0.7875 (0.75 x 1.05, stage 1), armor 35, MR 35, 0/40; HP 650 + 75 (Sett's Heartsteel bonus) = 725. Matches | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f4094-4323, f4449-4602 | 60 | mana text | 10, 20, 30 at f4094, f4170, f4247; cast f4323; 10, 20, 30 at f4449, f4525, f4602 | +10 per attack, no regen; attacks 76-77 frames apart = 38.25 ticks (engine 38 at 0.7875 AS); she casts on the 4th attack | Q2 |
| E3 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 1:12.05-1:14.2 (board every 0.1 s), f4323-4449 | 60 | the cast | spin at 1:12.1; she dashes; 218 magic on the target ~1:13.35-1:13.4; next +10 at f4449 (+126 fr = 63 ticks) | the dash branch: 'Eviscerate' at 1.285 s (the Movement group; 1:13.34) matches. The next attack came 63 ticks after the cast (Movement 'Unlock' 43 + windup ~9 = ~52; she walked to a new target) | Q7, Q13 |

Not used: the second cast at ~f4678 (the panel was on other units; the round ended at 1:18.7).

VOD8 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-21-2026_12-18-17-802/` `…PBE_11-21-2026_13-2-9-650.mp4`
(owner's game, 2026-11-21, 60 fps). Client rls-19.1.0.6013636 (patched 11:32 that day, not exported; owner: only a
Graves crash fix), so the simulator's 6011486 is assumed. Round 3-2 (PvP): Katarina 2 stars, no items; Slayer 2
active (3 Slayers on the board), Classical 1/2 inactive, Rock 3. Mana from `tools/vod_text_changes.py --field mana`
f42540-45000 (crops read by eye; changes that are only the HP text left out).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E4 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 11:52 (round 3-2) | 60 | inspection panel | 1,170/1,170, 0/40, 1 hex, Front, Magic Fighter; AD 45, AP 0%, armor 35, MR 35, AS 0.98, crit 25%, omnivamp 8% | engine (2 stars, stage 3, Slayer 2): HP 1170, AD 45, AS 0.975 (0.75 x (1 + Fighter stage 3 + Slayer 20%)), 0/40. Matches | Q1 |
| E5 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 f42847-44168 | 60 | mana text | 10/20/30 at f42847, 42909, 42972, cast (0) f43034; 10/20/30 f43134, 43196, 43260, cast f43320; 10 f43421, 20 f43481, 30 f43541, cast f43599; 10 f43699, (walk) 20 f43852, 30 f43912, cast f43970; 10 f44078; died f44168 | attacks 60-64 frames apart = 30-32 ticks (engine 31, 31, 30); 4th attack to the next attack after the cast 100, 101, 100 frames = 50 ticks (engine 50: the NoMovement 'Unlock' 40-tick lock + windup), the 4th 108 (she changed target); +10 per attack, no regen; casts on the 4th attack | Q2, Q7 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Katarina`):
  - **Cast (GA_Katarina19_Spell):** mana lock (0x1f38); CD_Katarina19_CastAnimCombined at her target. Phases
    Default 0.2995 s, Movement 0.6 s, MovementEnd 0.5504 s. A FirstActiveGroup picks Movement when she has
    Set19.Unit.Katarina.ShouldMove (GE_Katarina19_MovementTag, applied at 'CheckIfMove' 0.2484 s when her target is
    out of her attack range, 0xcb1), else NoMovement.
  - **Timeline:** 'Spin' 0 s; NoMovement 'Eviscerate' 0.835 s and 'Unlock' 1.2743 s; Movement 1.285 s and
    1.4251 s (E3 saw the Movement one). 'Unlock' lifts the mana lock and finishes the cast (0x170d).
  - **Damage:** 'Spin': GE_Katarina19_SpinDamage on the enemies within AoERadius (1) hexes of her, her target if
    none: MagicDamageCalc1 = AoEDamageAp x AP, magic, AOE, on-spell, RollIfCanSpellCrit. 'Eviscerate':
    GE_Katarina19_EviscerateDamage on her target: MagicDamageCalc2 = TargetDamageAP x AP, same tags without AOE.
  - **Captivate:** every enemy hit gets GE_Virtuosos19_Captivate for CaptivateDuration (5 s) when the board has
    Classical (ApplyCaptivate checks the trait level >= 1); it feeds the Classical damage amp.
  - **Simulated:** the target stands next to her, so the NoMovement group (the build's first 'Eviscerate' and
    'Unlock'; the predicted 39 / 40-tick locks). The spin hits the page's targets (G22).
