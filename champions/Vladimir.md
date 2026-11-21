# Vladimir (5-cost MagicFighter) · `DA_Vladimir19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** MagicFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Classical, Arcanist
- **HP** 1150 / 2070 / 3726 · **AD** 40 / 60 / 90 · **AS** 0.75 · **Range** 2 · **Armor** 60 · **MR** 60 · **Mana** 0 / 40
- **Unlock**: Only 1 champion in the 2 front rows of the battlefield.

### Ability: The Opera Phantom

> Passive: Gain 30%/30%/100% Omnivamp. Debuffed enemies are Captivated.
> 
> Active: Deal 120/180/999 × AP magic damage to the 3 nearest enemies and Captivate them for 3 seconds. 
> 
> Every 5/5/1th cast, drop a chandelier on the board. It deals 380/600/9999 × AP magic damage to all enemies, reduced by 10% per hex they are away from the epicenter.
> 
> Debuffs: Burn, Wound, Shred, Sunder, Mana Reave, Weaken, Slow, Vunerable

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 40 | 60 | 90 |
| CaptivateDuration | 60 | 60 | 60 |
| APDamage | 120 | 180 | 999 |
| NumCastsForChandelier | 5 | 5 | 1 |
| ShredPercent | 0.2 | 0.2 | 0.2 |
| ChandelierDamage | 380 | 600 | 9999 |
| DamageReductionPerHexFromCenter | 0.1 | 0.1 | 0.1 |
| DamageMinimumPercent | 0.01 | 0.01 | 0.01 |
| NumEnemiesMainCast | 3 | 3 | 3 |
| PassiveOmnivamp | 0.3 | 0.3 | 1 |
| 3StarDamageAmpNerf | 0.2 | 0.2 | 0.2 |
| CaptivateSpellDuration | 3 | 3 | 3 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 120/180/999 × AP
- `MagicDamageCalc2` = 380/600/9999 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Vladimir19_Attack`: launch 0.38 s (11.4 ticks); animation length 1.0012 s (30.04 ticks); release at base AS 0.5061 s (15.18 ticks)
- Attack projectile: DA_Vladimir19_AutoAttackProjectile, speed 1600 units/s
- Spell `GA_Vladimir19_Spell` (chrono `CD_Vladimir19_CastTracker`): cast ends 1.8 s (54 ticks), next attack can start 1.8333 s (55 ticks), mana lock removed 1.8 s (54 ticks); ended by `FinishCasting via OnEventBegin:CD_Vladimir19_CastSpecial:Unlock`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Vladimir19_3StarCast` | Chronos | 3.6 | Default 0, Clap 0.5076, Clap 0.6692, Drop 0.6692, Drop 2, Laugh 2.5959 |
| `CD_Vladimir19_Attack` | Chronos | 1.0012 | LaunchAttack 0.38, Unlock 0.7495 |
| `CD_Vladimir19_CastNormal` | Chronos | 0.961 | Cast 0.1425, Unlock 0.9503 |
| `CD_Vladimir19_CastNormal_Projectile` | Chronos | 2 | Default 0, Hit 0.5 |
| `CD_Vladimir19_CastSpecial` | Chronos | 1.8148 | Unlock 1.8 |
| `CD_Vladimir19_Chandelier` | Chronos | 5 | Teleport 0, Damage 1.7963, DestroyActor 4.2469 |

### Scripts on the unit

`GA_LaunchProjectileAttack`, `GA_SetAATarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Play3Star5CostCamera`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_DoLaunchAttackLogic`, `GA_Vladimir19_Spell`, `GA_ShopEvents`, `GA_Vladimir19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Vladimir19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Vladimir19_Spell.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-20, `set19champs.Vladimir`, D1); both cast locks checked on VOD7
- Keep in the simulator: **yes** (owner's VOD7 has him at 4-2 and 4-3 with the panel open)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | mana 40, AS 0.90 at stage 4 (0.75 x 1.2), AD 46 (40 + 15% Bloodthirster) confirmed; HP 1300 = 1150 + 150 (Prodigy Emblem); max HP +52 per cast = the emblem's 1% per 10 Mana spent (owner) | E1, E2 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicFighter: 10 per attack | confirmed: +10 per attack, 33-34 ticks apart at AS 0.90; regen 8/s = Prodigy (5) member 6 + 1 + the emblem's 1 | E1, E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.38 s (11.4 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 1600 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | two timelines (D1): CastNormal 'Unlock' 0.9503 s -> 30 ticks; every 5th cast CastSpecial 'Unlock' 1.8 s -> 55 ticks (the build's prediction follows CastSpecial only) | consistent: next attack's mana 44 ticks after a regen fill (normal; engine 44), 68.5 after the 5th cast's fill (engine 69); 43 after an attack fill (engine 44, the T10 tick) | E2, E3 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | normal 29 ticks, 5th cast 54 ticks | confirmed: banked overflow 6 shown exactly 60 frames (30 ticks = 29 + T4) after the filling attack; the 5th cast of the 4-2 fight 47.5-55 ticks, the 6th and 7th <= 30 | E2, E3 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script, D1); the chandelier replaces the 3-target hit on every 5th cast (the tooltip doesn't say) | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | not modelled: omnivamp/heal (no damage), passive Captivate on shredded enemies (no shred source), 3-star timeline | D1 |
| Q15 | Can this unit be simulated realistically? | | yes; where enemies stand relative to the chandelier: the owner's ring table (D2) | D1, D2 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD7 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-20-2026_21-47-56-118/`
`…PBE_11-20-2026_22-23-46-350.mp4` (owner's full PBE game, 1280x720, 60 fps). Played on client rls-19.1.0.6011486
(patched 20:35, game 22:00), adopted 2ace527. Vladimir 1★ with Bloodthirster and a
Prodigy Emblem (icon matched to T_Prodigy19_Emblem, 0.98), Prodigy (5), Classical (2), stage 4. Mana from
`tools/vod_text_changes.py --field mana` (crops read by eye). The panel shows 0 during the lock and a full bar only
once (E3), so a regen-filled cast's lock end (overflow 0) shows only at the next regen step: a bound, not a value.

| # | Date | Build | Source (VOD time / frames) | fps | Measured | Frames / values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-20 | rls-19.1.0.6011486 (client) | VOD7 20:24 (f73440), 21:01 (f76368, planning) | 60 | inspection panel | 1607/1612, 0/40, 8/s; AD 46 (15%), AP 28%, armor 83, MR 99, AS 0.90, crit 25%, omnivamp 55%; planning 1300/1300, 8/s | AS 0.75 x 1.2 (stage 4), omnivamp 30 + 25?; 8/s = Prodigy member 6 + 1 + Prodigy Emblem 1; HP 1300 = 1150 + 150 (emblem); max HP +52 a cast = 4% of 1300 (the emblem: 1% per 10 Mana spent) | Q1, Q2 |
| E2 | 2026-11-20 | rls-19.1.0.6011486 | VOD7 f73056-73853 (4-2, combat start ~f72400) | 60 | mana text | +2 every 15 frames; attacks +10 at f73068, 73135, 73312, 73380, 73520, 73586 (66-68 frames apart); casts at f73176 (38 + 2), f73432 (38 + 2), f73632 (38 + 2; 40/40 shown f73626-73631), f73836 (28 + 10 + 2). First mana after them: f73286 (+110), 73492 (+60), 73700 (+68) | f73176 = the 5th cast (Stack mod 5): lock in (95, 110] frames = 47.5-55 ticks (CastSpecial 54); the others in (45, 60] / (53, 68] frames (CastNormal 29). Next attack after f73176: +136 frames (engine 69 ticks from the fill), after f73432: +88 (engine 44) | Q2, Q7, Q9 |
| E3 | 2026-11-20 | rls-19.1.0.6011486 | VOD7 f77207-77955 (4-3) | 60 | mana text | cast f77440 filled by an attack (36 + 10: overflow 6), 6/40 shown f77500 (+60 frames); next attack's mana f77526 (+86); casts f77271 (38 + 2), f77805 (32 + 10, overflow 2 shown f77866, +61) | normal mana lock 29 ticks + T4 = 30 after the fill: exact; next attack 43 ticks after the fill (engine 44: the T10 tick) | Q7, Q9 |

## Decisions and notes

- **D1 (2026-11-20, `set19champs.Vladimir`):** from GA_Vladimir19_Spell. Each cast adds 1 to the unit's Stack
  (GE_IncSpellStackBy1_CombatOnly, from 0 each combat); Stack mod NumCastsForChandelier == 0 plays BigCast, else
  NormalCast. NormalCast: CD_Vladimir19_CastNormal 'Cast' (0.1425 s) hits GetMainSpellTargets (the attack target and
  the nearest enemies by row distance, the first 3, as a repeating list of 3) with MagicDamageCalc1 and Captivates
  them for CaptivateSpellDuration (Classical on the board); 'Unlock' 0.9503 s ends it. BigCast: CastSpecial at the
  grid centre ('Unlock' 1.8 s) and the chandelier (CD_Vladimir19_Chandelier at speed 1, 'Damage' 1.7963 s):
  MagicDamageCalc2 x max(DamageMinimumPercent, 1 - DamageReductionPerHexFromCenter x ring) on every enemy, ring =
  the CT_BoardAOERange hex ring from the grid centre. Linear, not compounding: the script computes
  FMax(min, 1 - 0.1 x n) (DetermineChandelierDamageBasedOnDistance); no VOD damage numbers checked. Not modelled: heal/omnivamp, the passive (Captivates shredded enemies), the 3-star
  timeline (CD_Vladimir19_3StarCast: Clap shreds all enemies, repeated drops); a 3-star casts the chandelier every
  time (NumCastsForChandelier 1) on the CastSpecial timeline.
- **D2 (owner, 2026-11-20): targets.** He hits far more units than usual: default 7 targets, at least 3 (he
  Captivates 3), up to 10 (a full board). Their rings from the chandelier's centre, in targets order: the target at
  the epicentre, 2 at 1 hex, 2 at 2, 2 at 3, the rest at 4 (`Vladimir.CHANDELIER_RINGS`); fewer targets drop the
  furthest. The page's Targets buttons run 3-10 (`TARGETS_MIN` / `TARGETS_MAX`, catalog `targetsMin`).
