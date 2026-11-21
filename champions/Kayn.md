# Kayn (1-cost AttackFighter) · `DA_Kayn19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 1, pool 30; traits: Heartsteel, Slayer
- **HP** 650 / 1170 / 2106 · **AD** 42 / 63 / 94.5 · **AS** 0.75 · **Range** 1 · **Armor** 35 · **MR** 35 · **Mana** 0 / 30

### Ability: Shadow of the Night

> Dash and swipe, dealing 115/175/270 × AD + 15/25/45 × AP physical damage to enemies in a 2 hex line.
> 
> Heartsteel Upgrade: At 70% Health, turn into the Shadow Assassin, briefly becoming untargetable and dealing 35% bonus magic damage for the rest of combat.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 42 | 63 | 94.5 |
| SpellMagicDamage | 15 | 25 | 45 |
| SpellPhysicalDamage | 115 | 175 | 270 |
| SpellWidth | 100 | 100 | 100 |
| SpellLength | 429 | 429 | 429 |
| SpellHexLength | 2 | 2 | 2 |
| ExtraDashRangeAboveAttackRange | 1 | 1 | 1 |
| HeartsteelStan_PercentHealthTrigger | 0.7 | 0.7 | 0.7 |
| HeartsteelStan_MagicDamagePostTransform | 0.35 | 0.35 | 0.35 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 115/175/270 × AD + 15/25/45 × AP
- `GenericCalc1` = 115/175/270 × AD
- `GenericCalc2` = 15/25/45 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Kayn19_Attack`: launch 0.3273 s (9.82 ticks); animation length 2.6 s (78 ticks); release at base AS 0.3273 s (9.82 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Kayn19_Spell` (chrono `CD_Kayn19_Spell`): cast ends 0.7333 s (22 ticks), next attack can start 0.7667 s (23 ticks), mana lock removed 0.7333 s (22 ticks); ended by `FinishCasting via OnChronoStopped:CD_Kayn19_Spell:None`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Kayn19_Attack` | ChronoDefs | 2.6 | LaunchAttack 0.3273, Unlock 1.04 |
| `CD_Kayn19_Dash` | ChronoDefs | 1.1094 | Default 0, Loop 0.4624, FinishJump 0.4816 |
| `CD_Kayn19_Heartsteel_BecomeShadowAssassin` | ChronoDefs | 89.9497 | Default 0, Loop 0.012 |
| `CD_Kayn19_Spell` | ChronoDefs | 0.7304 | DealDamage 0.4591 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Kayn19_Heartsteel_Passive`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Kayn19_Spell`, `GA_ShopEvents`, `GA_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Kayn19_Spell.txt
- `GE_ManaLock`: applies mana lock: GA_Kayn19_Spell.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Kayn`, D1); stats and the tooltip checked on VOD6
  (E1-E2), the Shadow Assassin's trigger and the cast rhythm seen (E3)
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has him at 1-3 and 1-4, the latter as the Shadow Assassin)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed (with Heartsteel and an item; HP 725 = 650 + Heartsteel's Sett 75) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackFighter: 10 per attack, no regen | confirmed (+10 steps, nothing between them; casts at 30) | E3 |
| Q3 | First attack at combat start: when does it land? | G3 | open (VOD6's enemies walk in) | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3273 s (9.82 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable | |
| Q7 | Cast time: cast start to the next attack starting | 0.7667 s (23 ticks) standing still; more with a dash | consistent: the next attack's mana came +66 frames after one cast (standing: ~64), +78 / +79 / +95 after the others (dashes) | E3 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 0.7333 s (22 ticks) | predicted (no regen to show it) | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 (no GE_SimulateLaunchAttack) | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | SpellPhysicalDamage x AD + SpellMagicDamage x AP, physical, on the enemies in a 429 x 100 rectangle toward the target | formula confirmed (tooltip 140 = 115 x 1.07 + 15 x 1.10) | E2, D1 |
| Q14 | Passives and other mechanics that need modelling | Heartsteel Bias: Shadow Assassin at 70% Health, +35% of his damage as magic | modelled (D1); the trigger seen at 70% | E3, D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |
| Q16 | Does he dash before the swipe against stationary enemies? | MakeDashDecision: dashes when the best hex within 2 of the target hits at least as many as standing still, unless he is on it | **open**: simulated standing still; VOD6's casts mixed (E3) | E3 |
| Q17 | When does the Bias Kayn become the Shadow Assassin in the simulator (dummies never hit back)? | at 70% Health | **owner, 2026-11-18 (tentative)**: 5 s into combat (he is fronted, then transforms); VOD6 1-4 crossed 70% ~4.8 s in | E3, D2 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18, 60 fps; client rls-19.1.0.5986652, not exported: the simulator's newest is 5986094). Round 1-4:
Kayn 1 star with one item, Heartsteel (3) with him as the Bias; enemies walk in. Mana and Health from
`tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 1:57.6 (round 1-4, planning) | 60 | inspection panel | 725/725, 0/30, range 1 hex, Front, Attack Fighter; AD 45, bonus AD 7%, AP 10%, armor 35, MR 35, AS 0.86, crit 35% | AD 42 x 1.07 = 44.9 (Heartsteel: his own +7%); armor, MR, mana match; AS 0.86 = 0.75 x (1 + 0.05 + 0.10) with the item; HP 650 + 75 (Heartsteel SettHealth, Sett fielded) | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 1:57.6 (ability tooltip) | 60 | damage | 140 | 115 x 1.07 + 15 x 1.10 = 139.6: AD and AP are the multipliers | Q13 |
| E3 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f7832-8738 (round 1-4) | 60 | mana and Health text | +10 steps; casts f7968, f8155, f8345, f8569, f8738; next +10 at +79, +66, +78, +95 frames; Health 508/725 (70.07%) at f7968, 499 (68.8%) at f8032, then 472 for the rest of the round | the transform at 70% of max (Health falls past it ~4.8 s after f7745, then he is untargetable a while); casts at 30 mana; the after-cast gaps mix a standing cast (~64 frames: 23 ticks + windup at 0.86 AS) and dashes | Q2, Q7, Q14, Q16, Q17 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Kayn`):
  - **Cast (GA_Kayn19_Spell):** commit, mana lock (0x1729), EstablishVariables (SpellWidth 100, SpellLength 429,
    SpellHexLength 2, ExtraDashRangeAboveAttackRange 1). MakeDashDecision (0x1f26): standing still hits more ->
    Cast(); else he dashes (CD_Kayn19_Dash, Cast() at 'FinishJump') to the best unoccupied hex within SpellHexLength
    of the target and within his range + 1 of him (most enemies in the line through the target, ties to the row
    nearest the middle), unless he is already on it; no hits either way or no hex -> the nearest free hex.
  - **Swipe:** Cast() plays CD_Kayn19_Spell at the target; 'DealDamage' (0.4591 s): GE_19_KaynDamageEnemies on the
    units in the rectangle (TR_Add_UnitsWithinRectanglePointProjection, from him toward the target, 429 x 100), the
    target if none: PhysicalDamageCalc1 = SpellPhysicalDamage x AD + SpellMagicDamage x AP, physical, on-spell,
    RollIfCanSpellCrit. The chrono's end (0.7304 s) lifts the mana lock and ends the cast (CleanupAbility).
  - **Shadow Assassin (GA_Kayn19_Heartsteel_Passive):** with SpellUpgradeTierIsActive + Selected (Heartsteel (3)/(5)
    Bias), the first damage taken that leaves Health + Shield at or under 70% of max applies MinHealthBuff (Health
    floor 70% for 0.1 s), IsShadowAssassin and 1 s untargetable. From then each of his Damage.Source.Unit damages
    at PreMitigation adds GE_Kayn19_Heartsteel_BonusMagicDamage = that amount x 0.35: magic, Damage.Source.Trait,
    no tags, CritCondition.Never.
  - **Simulated:** standing still (Q16); the swipe hits the dummies in the rectangle (the target, plus any straight
    behind it); as the Bias he is the Shadow Assassin from combat start (Q17; changed in D2); the bonus is not
    amplified again (as True Damage's bonus, B19) and the averaged crit is in its base.

- 2026-11-18, D2 (owner): the Bias becomes the Shadow Assassin `Kayn.SHADOW_ASSASSIN_AT` = 5 s into combat, not from
  the start: he is meant to be fronted, then take enough damage to transform (tentative; VOD6 1-4: ~4.8 s, E3). The
  bonus is on his damage from that tick on (`test_kayn.py`).
