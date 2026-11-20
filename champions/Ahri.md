# Ahri (4-cost MagicCaster) · `DA_Ahri19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6005555.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6005555.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: K/DA, Choreographer
- **HP** 850 / 1530 / 2754 · **AD** 30 / 45 / 67.5 · **AS** 0.8 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 0 / 30

### Ability: Burn it Down

> Passive: Start combat with 6 fox-fires and gain 2/2/4 after casting, up to 14. Then enter a flow state, moving faster and empowering subsequent casts.
> 
> Active: Launch all fox-fires at the target, each dealing 28/42/400 × AP magic damage. If in the flow, instead launch a heart at the target that deals 235/350/2000 × AP magic damage and split the fox-fires among all enemies within 2 hexes of them.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| APDamage | 28 | 42 | 400 |
| HexRangeAroundTarget | 2 | 2 | 2 |
| APDamage_Secondary | 235 | 350 | 2000 |
| FoxFiresPerCast | 2 | 2 | 4 |
| BaseFoxFires | 6 | 6 | 6 |
| APAtMaxFire | 0 | 0 | 0 |
| MaxFoxFires | 14 | 14 | 14 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 28/42/400 × AP
- `MagicDamageCalc2` = 235/350/2000 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_19_Ahri_Attack`: launch 0.3067 s (9.2 ticks), variants 0.3067, 0.3874; animation length 3.2 s (96 ticks); release at base AS 0.3067 s (9.2 ticks)
- Attack projectile: DA_Ahri19_AutoAttackProjectile, speed 1750 units/s
- Spell `GA_19_Ahri_Spell` (chrono `CD_19_Ahri_CastAnim_Empowered`): cast ends 0.9667 s (29 ticks), next attack can start 1 s (30 ticks), mana lock removed 0.9667 s (29 ticks); ended by `FinishCasting via OnEventBegin:CD_19_Ahri_CastAnim_Empowered:Unlock`
  - notes: projectile (hit time depends on travel) ×6

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_19_Ahri_Attack` | Chronos/Default | 3.2 | LaunchAttack 0.3067, LaunchAttack 0.3874, Unlock 1.2, Unlock 1.28 |
| `CD_Ahri19_DashMove` | Chronos/Default | 0.3002 | Arrived 0.3002 |
| `CD_19_Ahri_CastAnim_Empowered` | Chronos/Spell/Empowered | 1.8155 | Fire 0.5157, Unlock 0.9443 |
| `CD_19_Ahri_SpiritRushActivationPose` | Chronos/Spell/Empowered | 0.7667 | PowerUp 0.2009, Unlock 0.7512 |
| `CD_19_Ahri_CastAnim_Basic` | Chronos/Spell/Standard | 1.1568 | StartMissiles 0.1398, Unlock 0.9981 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_19_Ahri_SunglassesOn`, `GA_PlayChronoOnTraitActivation`, `GA_Ahri19_MoveToTarget`, `GA_Death`, `GA_Celebration`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_19_Ahri_Spell`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_19_Ahri_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_19_Ahri_Spell.txt

### Changed since `rls-19.1.0.5995286.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Ahri`, D1); the three cast lengths (basic, the one
  reaching 14 fox-fires with the pose, the flow) checked on VOD6 to a tick (E2)
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has her at 2-8)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | mana 30 confirmed; 3/s and +12 per attack are the role's 2 and 7 + Spear of Shojin's 1 and 5 (owner: she held one, D3); HP 1025 vs 850 not identified | E2, D3 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster: 7 per attack, 2/s | confirmed with Spear of Shojin: +12 = 7 + 5, 3/s = 2 + 1; when it is paid: open | E2, D3 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3067 s (9.2 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1750 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | basic 31, reaching 14 54, flow 30 ticks | consistent (Q9) | E2 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | basic 'Unlock' 30; + the pose 53; empowered 29 ticks | confirmed: the banked overflow 31 / 31 (basic), 54 (reaching 14), 30 x 6 (flow) ticks after the bar empties | E2 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 (no GE_SimulateLaunchAttack) | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | basic: every fox-fire APDamage x AP at the target; flow: heart APDamage_Secondary x AP + the fox-fires split | predicted | D1 |
| Q14 | Passives and other mechanics that need modelling | fox-fires 6, +2 per cast, 14 max; the flow at 14 | modelled; the cast count to the flow confirmed (the 4th cast plays the pose) | E2 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18, 60 fps; client rls-19.1.0.5986652, not exported: the simulator's newest is 5986094). Round 2-8:
Ahri with items. Mana from `tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f66695-67914 | 60 | mana text | 1025/1025, x/30, 3/s, +12 per attack. Casts and the overflow's frame: f66786 -> f66868 (+82), f66958 -> f67020 (+62), f67073 -> f67135 (+62), f67181 -> f67289 (+108), f67347 -> f67407 (+60), f67471 -> f67531, f67564 -> f67624, f67654 -> f67714, f67766 -> f67826, f67854 -> f67914 (+60 each) | basic 31, the 4th cast (12 -> 14 + pose) 54, the flow 30 ticks: the locks + the tick after the fill. The first cast's +82 is not a lock: that cast filled from regen (29 at f66772, 0 at f66786), so nothing was banked and f66868's 0 -> 12 is the next attack (D3) | Q1, Q2, Q9, Q14 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Ahri`):
  - **Fox-fires:** BaseFoxFires at combat start (the Stack attribute); each basic cast's 'Unlock' adds
    FoxFiresPerCast (AddFoxFires), up to MaxFoxFires.
  - **Basic (fewer than 14):** mana lock; CD_19_Ahri_CastAnim_Basic. 'StartMissiles' (0.1398 s):
    RepeatAction(0.5 / N, N), first at once: CD_Ahri19_FoxFireAtTarget (2100) at her target,
    GE_19_Ahri_PrimaryDamage (MagicDamageCalc1). 'Unlock' (0.9981 s): AddFoxFires; reaching the max ->
    CD_19_Ahri_SpiritRushActivationPose ('PowerUp' 0.2009 s: GE_Ahri19_SpiritRush; 'Unlock' 0.7512 s) -> EndSpell;
    else EndSpell.
  - **Flow (14):** CD_19_Ahri_CastAnim_Empowered: 'HeartMis' (spawned 0.3642 s, 1600) at her target,
    GE_19_Ahri_SecondaryDamage (MagicDamageCalc2); the fox-fires (spawned at the chrono's eight 'SpellMis' times in
    turn, 1600) split half way (PercentDistanceBeforeSplit 0.5, CD_Ahri19_EmpowedSpell_SpreadMissile): every other
    one at her target, the others at enemies within HexRangeAroundTarget (2) of it; MagicDamageCalc1 each. 'Unlock'
    (0.9443 s) ends the cast.
  - **Simulated:** each fox-fire's flight over its target's whole distance at its speed; the split's secondary
    enemies in turn.

- 2026-11-18, D2 (build data, ledger B36): the projectile modules' Delay, read since the snapshot tool's fix. A basic
  fox-fire waits 0.1 s before flying. In the flow the heart leaves at 0.3642 + 0.2 = 0.5642 s, and the eight
  'SpellMis' modules (spawned 0.0355-0.3894 s, waits 0.6338 down to 0.1667 s) all leave 0.5561-0.6693 s into the
  cast, in turn; each fox-fire flies half its target's distance at 1600, waits 0.05 + 0.1 s at the split
  (CD_Ahri19_EmpowedSpell_SpreadMissile) and flies on at 2100. D1's spawn times without the waits had them leave
  0.04-0.39 s in. The cast lengths (E2) don't change.

- 2026-11-19, D3 (owner: VOD6's Ahri held a Spear of Shojin; E2's crops re-read):
  - **Mana:** Shojin's ManaPerAttack 5 and ManaRegen 1 (GE_SpearOfShojin) on the MagicCaster role's 7 and 2 give the
    clip's +12 per attack and 3/s (Q1, Q2). The HP (1025, build 850) comes from something else.
  - **The first cast (E2's +82):** it filled from regen, not an attack: 28 -> 29 (f66772) -> cast (f66786, 0), so
    no overflow was banked and the next change, 0 -> 12 at f66868, is an attack's mana. Regen then shows 13 at f66876,
    which puts the lock's end at about f66848-66856 (at 3/s the bar reaches 1 about 20 frames after mana is gained
    again): 31-35 ticks after the cast, so consistent with the 31-tick basic lock the other casts show.
    Nothing to change in the engine.
