# Yuumi (4-cost MagicCaster) · `DA_Yuumi19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5995286.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5995286.Set19.Shipping.pbe`

- **Role** MagicCaster: "Attacks grant 7 Mana. Gain 2 Mana Regen." (ManaPerAttack + 7; ManaPerSecond + 2; ManaMax at least 10)
- **Cost** 4, pool 10; traits: Illbeats, Encore
- **HP** 850 / 1530 / 2754 · **AD** 30 / 45 / 67.5 · **AS** 0.8 · **Range** 4 · **Armor** 40 · **MR** 40 · **Mana** 0 / 20

### Ability: Girl, Put Your Records On (Your Head)

> Throw a spinning disc that deals 185/280/1400 × AP magic damage and stacks on the target's head, reducing their Magic Resist by 1 every second. 
> 
> When they have 4 + 1 discs, the stack topples over, dealing 40% of the stacked discs' total damage to the target and another 40% split among 4 nearby enemies.
> 
> If an enemy dies with a disc, it passes to another enemy.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| PopDamageAP | 0 | 0 | 0 |
| TickRate | 0.25 | 0.25 | 0.25 |
| DoTDuration | 999 | 999 | 999 |
| NumDiscsToPop | 4 | 4 | 4 |
| DoTDamageAP | 185 | 280 | 1400 |
| PoppedDotPercentToMainTarget | 0.4 | 0.4 | 0.4 |
| PoppedDotPercentToOtherTargets | 0.4 | 0.4 | 0.4 |
| NumTargetsToDistributeDiscs | 4 | 4 | 4 |
| MRShredPerSecond | 1 | 1 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 185/280/1400 × AP
- `MagicDamageCalc2` = 0 × AP
- `GenericCalc1` = 4 + 1
- `GenericCalc2` = 1 × 0.25
- `GenericCalc3` = 1 ÷ 1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Yuumi19_Attack`: launch 0.3671 s (11.01 ticks); animation length 2.6667 s (80 ticks); release at base AS 0.3671 s (11.01 ticks)
- Attack projectile: DA_Yuumi19_AutoAttackProjectile, speed 1500 units/s
- Spell `GA_Yuumi19_Spell` (chrono `self.SpellChrono`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_Encore19.RecastEffectiveness input unresolved (CallFunc_EvaluateCurveTableRow_InXY_ImplicitCast_3), used star 2 ×1; chrono not found self.SpellChrono ×1; projectile (hit time depends on travel) ×6

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Yuumi19_Attack` | CD_Yuumi19_Attack | 2.6667 | LaunchAttack 0.3671, Unlock 1.0667 |
| `CD_Yuumi19_CastAnimLeft` | CD_Yuumi19_CastAnimLeft | 1.0145 | Disk 0.365, EncoreDisk 0.4615, Unlock 0.9997 |
| `CD_Yuumi19_CastAnimRight` | CD_Yuumi19_CastAnimRight | 1.0158 | Disk 0.365, EncoreDisk 0.4615, Unlock 0.9997 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_Yuumi19_Spell`, `GA_ShopEvents`, `GA_Yuumi19_GESpecReceiver`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Yuumi19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Yuumi19_Spell.txt

### Changed since `rls-19.1.0.5986094.Set19.Shipping.pbe`

- stat AttackSpeed: 0.75 -> 0.8
- row DoTDamageAP: 175 / 265 / 1400 -> 185 / 280 / 1400
- ability text changed

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Yuumi`, D1); the mana lock checked on VOD6 to a tick (E2)
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has her at 1-8 and 1-9)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (HP 925 = 850 + Heartsteel's Sett 75; mana 20, 2/s, range 4) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicCaster: 7 per attack, 2/s | confirmed (+7 steps, +1 every 0.5 s) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3671 s (11.01 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1500 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 'Unlock' 0.9997 s: 31 ticks | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 'Unlock': 30 ticks | confirmed: the banked overflow shows 31 / 31 / 31 / 31.5 ticks after the bar empties (30 + the tick after the fill) | E2 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 (no GE_SimulateLaunchAttack) | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | a disc DoTDamageAP x AP on the target; the 5th disc topples 40% / 40% split | predicted | D1 |
| Q14 | Passives and other mechanics that need modelling | MR shred 1 per second per disc; discs passing on when an enemy dies | not modelled (flat resist reduction; dummies don't die) | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18, 60 fps; client rls-19.1.0.5986652, not exported: the simulator's newest is 5986094). Rounds 1-8
and 1-9: Yuumi 1 star with two items; Heartsteel on the board (Sett fielded). Mana from
`tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 6:40 (round 1-8) | 60 | inspection panel | 925/925, 7/20, 2/s, range 4 hex, Back, Magic Caster; AD 30, AP 20%, armor 48, MR 48, AS 1.22, crit 25% | HP 850 + 75 (Sett); AD, mana, regen, range match; AP, AS, armor, MR carry items and traits not identified | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f23739-24493 (round 1-8) | 60 | mana text | casts at f23917 (19 + 7 = 26), f24094 (17 + 7 = 24), f24261 (14 + 7 = 21), f24431 (19 + 7 = 26); the overflow 6 / 4 / 1 / 6 shows at f23980, f24156, f24323, f24493: +63, +62, +62, +62 frames | mana lock 30 ticks + the tick after the fill | Q2, Q9 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Yuumi`):
  - **Cast (GA_Yuumi19_Spell):** commit, mana lock (0x1ed8); CD_Yuumi19_CastAnimLeft / _Right in turn (same
    times). 'Disk' (0.365 s): 'Disc' (1800, spline) at her target; arrival: GE_Yuumi19_DiscDamage =
    MagicDamageCalc1 (DoTDamageAP x AP), magic, on-spell, RollIfCanSpellCrit, and GE_Yuumi19_Disc (no damage
    component: TickRate period, DoTDuration 999 s, grants GA_Yuumi19_MRShredHandler). 'EncoreDisk' (0.4615 s): the
    chrono's Encore group needs Set19.Trait.Encore: an 'EncoreDisc', GE_Yuumi19_DiscDamage_Encore = Calc1 x
    RecastEffectiveness and GE_Yuumi19_DiscEncore (its proportion = RecastEffectiveness). 'Unlock' (0.9997 s):
    lock off, FinishCasting.
  - **Topple (GA_Yuumi19_EnemyDiscHandler):** at NumDiscsToPop + 1 discs: the discs are removed; the target gets
    GE_Yuumi19_PoppedDiscDamage = MagicDamageCalc1 x RemainingDamageProp (SetByCaller, MultiplyAdditive) with
    PoppedDotPercentToMainTarget x the summed proportions (self-bounce chrono, 0.5997 s); the
    NumTargetsToDistributeDiscs nearest units (TR_Add_N_NearestUnits, row distance) get PoppedDotPercentToOtherTargets
    / NumTargetsToDistributeDiscs x the sum (CD_Yuumi19_ToppleNormalDisc, 1450).
  - **Simulated:** one topple flight per receiver; full proportions (no decay over 999 s); MR shred and passing on
    death not modelled.
