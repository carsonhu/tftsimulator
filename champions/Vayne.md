# Vayne (4-cost AttackMarksman) · `DA_Vayne19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6037882.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6037882.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Rock, Trickshot
- **HP** 850 / 1530 / 2754 · **AD** 62 / 93 / 139.5 · **AS** 0.8 · **Range** 5 · **Armor** 40 · **MR** 40 · **Mana** 0 / 50
- **Unlock**: 5 unique star levels of Rock or Trickshot.

### Ability: Darkest Hour

> Passive: On cast or when hit, tumble and gain 0.5 × AP ÷ 1 × GenericCalc2 Durability for 2 seconds. (4 second cooldown)
> 
> Active: Gain demonic power, enhancing the next 3 attacks to deal 175/265/2400 × AD physical damage + 1.5%/2.5%/20% of the target's max Health as true damage.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 62 | 93 | 139.5 |
| TumbleDurability | 0.5 | 0.5 | 0.5 |
| NumAttacks | 3 | 3 | 3 |
| DamageAD | 175 | 265 | 2400 |
| PercentMaxHealthDamage | 0.015 | 0.025 | 0.2 |
| DurabilityDuration | 2 | 2 | 2 |
| TumbleCooldown | 4 | 4 | 4 |
| MaxTumbleHexDistance | 3 | 3 | 3 |

Formulas (as stored; AD and AP are multipliers):

- `GenericCalc1` = 0.5 × AP ÷ 1 × GenericCalc2
- `GenericCalc2` = 1 + 0.5 × AP + -0.5
- `DurabilityCalc1` = 1 + -1 × GenericCalc1
- `PhysicalDamageCalc1` = 175/265/2400 × AD
- `GenericCalc3` = 4 ÷ 1 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Vayne19_Attack`: launch 0.2317 s (6.95 ticks), variants 0.2317, 0.3007, 0.3039; animation length 1.6667 s (50 ticks); release at base AS 0.2317 s (6.95 ticks)
- Attack projectile: DA_Vayne19_AutoAttackProjectile, speed 2000 units/s
- Spell `GA_Vayne19_Spell` (chrono `CD_Vayne19_CastAnim`): cast ends 0.7 s (21 ticks), next attack can start 0.7333 s (22 ticks), mana lock removed –; **script reads attack speed**; ended by `FinishCasting via OnEventBegin:CD_Vayne19_CastAnim:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Vayne19_Attack` | Chronos | 1.3 | LaunchAttack 0.2317, CustomLaunchAttack1 0.2323, LaunchAttack 0.3007, LaunchAttack 0.3039, CustomLaunchAttack1 0.3677, Unlock 0.52, Unlock 0.56, Unlock 0.6533, Unlock 0.6667, Unlock 1.2 |
| `CD_Vayne19_CastAnim` | Chronos | 0.7003 | DemonON 0.0726, Unlock 0.6968 |
| `CD_Vayne19_Celebration` | Chronos | 5.4324 | Default 0, Loop 3.4393 |
| `CD_Vayne19_TumbleMove` | Chronos | 0.2265 | MovementComplete 0.2224 |
| `CD_Vayne19_TumbleUnlock` | Chronos | 0.5118 | Unlock 0.5062 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Vayne19_TrickshotHandler`, `GA_Trickshot19_HandleAutoAttackBounce`, `GA_AutoAttack`, `GA_LaunchProjectileAttack_Trickshot19`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Vayne19_Spell`, `GA_ShopEvents`, `GA_Vayne19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Vayne19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Vayne19_Passive.txt, GA_Vayne19_Spell.txt
- `AttackSpeed`: reads or changes attack speed: GA_Vayne19_Spell.txt, GA_Vayne19_Tumble.txt
- `GE_ManaLock`: applies mana lock: GA_Vayne19_Spell.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: GA_Vayne19_TrickshotHandler.txt

### Changed since `rls-19.1.0.6028987.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-21, `set19champs.Vayne`, D1); mana, the cast lock, the bolts' mana lock
  and Kraken's Fury stacks checked on VOD8 at 4-2 (E1-E2)
- Keep in the simulator: **yes** (owner, 2026-11-21: VOD8 recorded for her)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (with Kraken's Fury and Heartsteel's fielded Kayn: HP 850, AD 73, bonus AD 17%, AS 0.88, armor 40, MR 60, 0/50, 5 hexes) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackMarksman: 10 per attack | confirmed (+10 per attack, on the frame of Kraken's launch stack: the release) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | SequentialAttack 0.3007 s (the build's attack_launch 0.2317 s is the TumbleAttack group, P14) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2; UltAttack G20 at 0.72 | consistent (AS 0.88: attacks 68 frames = 34 ticks apart, engine 34.09; 3rd bolt 38 ticks after the 2nd, engine 38) | E2 |
| Q6 | Projectile travel time (ranged only) | attack 2000 units/s; bolt 3100; Trickshot bolt 1900 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | tumble: 'MovementComplete' 0.2224 s + 'Unlock' 0.5062 s / CastSpeed, + 1 tick (the build's spell timeline follows the in-place CastAnim path, 0.7333 s) | confirmed (VOD8 4-2: first bolt 29 ticks after the cast = 7 + 14 + 1 + the UltTumbleAttack windup 7) | E2 |
| Q8 | Does the cast time scale with attack speed? | CastSpeed = clamp(AS / base, 1, 2) on TumbleUnlock only | confirmed at 1.1 (one sighting) | E2 |
| Q9 | Mana lock: from cast start, when can mana be gained again? | the tick after the 3rd bolt's launch | confirmed (no mana from the three bolts; +10 at the 4th attack) | E2 |
| Q10 | Does the mana lock scale with attack speed? | no: it lasts 3 bolts | predicted (script) | D1 |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0; the 3 bolts are attacks (Combat.Event.LaunchAttack.Custom.1) | confirmed (Kraken's Fury stacks at each bolt) | E2 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | each bolt PhysicalDamageCalc1 (DamageAD x AD) + PercentMaxHealthDamage x the target's HealthMax true, on her target; Trickshot ricochets at RichochetDamage^k | predicted (GEs read); tooltip 193 = 165 x AD 1.17 | D1, E1 |
| Q14 | Passives and other mechanics that need modelling | passive tumble when hit (4 s cooldown) cancels her attack | not simulated (dummies never attack); seen on VOD8 | E2 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-21 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD8 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-21-2026_12-18-17-802/` `…PBE_11-21-2026_13-2-9-650.mp4`
(owner's game, 2026-11-21, 60 fps). Client rls-19.1.0.6013636 (not exported; owner: only a Graves crash fix), so
6011486 is assumed. Vayne 1 star with Kraken's Fury (icon matched to the client texture); Rock 2/3 and Trickshot 1/2
inactive; Slayer (4), Juggernaut (2), Heartsteel (1, Kayn fielded) on the board. Launch marks: Kraken's Fury adds 3.5% AD per
Combat.Event.LaunchAttack, so the panel's bonus AD % (`tools/vod_text_changes.py --field ad`) changes on each launch's
frame; mana from `--field mana`.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 19:32 (round 4-2 planning) | 60 | inspection panel, ability tooltip | 850 / 850, 0/50, Back, 5 Hex, Attack Marksman; AD 73, bonus AD 17%, AP 0%, armor 40, MR 60, AS 0.88, crit 25%, omnivamp 18%; tooltip Damage 193 (165 / 250 / 2000), 1.5% max Health | engine with Kraken's Fury and Heartsteel (1) with Kayn ticked: HP 850, AS 0.88, MR 60, bonus AD 10% + KaynAD 7% = 17% (owner, 2026-11-21: Kayn fielded; `test_vod8_panel_bonus_ad`), AD 62 x 1.17 = 72.5; 193 = 165 x 1.17 | Q1, Q13 |
| E2 | 2026-11-21 | rls-19.1.0.6013636 (client) | VOD8 f70600-71800 (4-2) | 60 | bonus AD % and mana text | launches f70722, 70790, 70858, 70927, 70995 (68-69 frames apart; +10 mana on each, the last fills the bar); bolts f71055, 71177, 71253 (no mana); next attack f71319 (+10), then 71389, 71453, 71521, 71596 (fill) | cast at f70997 (fill + 1 tick); first bolt 58 frames = 29 ticks later (engine 29: tumble 7 + 14 at CastSpeed 1.1 + 1, then the UltTumbleAttack windup 7); HP drops from f71111 and a tumble at ~f71117-71123 (the cast's 2 s TumbleCooldownShort over) delayed the 2nd bolt to 122 frames; the 3rd 76 frames later (38 ticks, engine 38); the 4th attack 66 frames later (engine 32-33 ticks); no mana through the bolts, +10 again on the 4th | Q2, Q5, Q7-Q9, Q11, Q14 |

## Decisions and notes

- 2026-11-21, D1 (implemented, `set19champs.Vayne`):
  - **Cast (GA_Vayne19_Spell):** commit, CastSpeed = FMax(FMin(AS / base AS, 2), 1) (0x191f-0x1aef), mana lock
    (0x1b0a). With DoTumbleAttack and TumbleLockout (a passive tumble not yet attacked out of): CD_Vayne19_CastAnim in
    place, the demon at 'DemonON', FinishCasting at 'Unlock'. Otherwise (always, in the simulator) the tumble
    (0x1f5a): GE_Vayne19_UltActiveDemon + UltActiveTag (InUlt) at once, CD_Vayne19_TumbleMove (speed 1) to the safest
    hex within MaxTumbleHexDistance in range of her target, 'MovementComplete' -> CD_Vayne19_TumbleUnlock at
    CastSpeed, 'Unlock' -> UnlockForAttacking -> FinishCasting (0x29c9). GE_Vayne19_TumbleDurability and
    TumbleCooldownShort (2 s each), GE_Vayne19_TumbleAttackTag (DoTumbleAttack until her next launch).
  - **Bolts:** her attack chrono's first active group: UltTumbleAttack (InUlt + DoTumbleAttack: CustomLaunchAttack1
    0.2323 s of 1.3 s), UltAttack (InUlt: 0.3677 s of 1.6667 s, PlayRateScalingThreshold 0.72), TumbleAttack,
    SequentialAttack (normal: 0.3007 s). Each custom launch (0x832) plays CD_Vayne19_EmpoweredMis 'Bolt' (3100
    units/s) at her target; its arrival (0xf40): GE_Vayne19_UltBoltDamage = PhysicalDamageCalc1 (DamageAD x AD;
    AppliesOnSpell, AppliesOnHit.IsAttack) + the target's HealthMax x PercentMaxHealthDamage true (AppliesOnSpell),
    both RollIfCanSpellCrit; then the Trickshot bounce event. At NumAttacks (3), DelayUntilNextTick: mana lock and
    InUlt removed (0xf). The custom launch fires no attack projectile.
  - **Trickshot (GA_Vayne19_TrickshotHandler):** ricochet k: CD_Vayne19_EmpoweredMisTrickshot 'Bolt' (1900 units/s)
    to the next enemy, GE_Vayne19_UltBoltDamage_Trickshot = both parts x RichochetDamage^k (MMC_TrickshotReduction),
    on-hit at that effectiveness (AppliesOnHit, not IsAttack), up to NumRichochets (as Draven). Her normal attacks'
    ricochets are the trait's (B12).
  - **Simulated:** not the passive (GA_Vayne19_Passive: tumble when hit, 4 s cooldown, cancels her attack) nor the
    Durability, as dummies never attack; VOD8 shows the passive costs a real Vayne time. The variants are built from
    the attack chrono (the snapshot misses the nested ult groups, P14): normal attacks all play SequentialAttack's
    first module; UltAttack's 0.72 typed from the FModel export. Not AREA, as Draven: only Trickshot's ricochets
    reach the other dummies. Open questions: docs/OPEN-QUESTIONS.md 7aa.

