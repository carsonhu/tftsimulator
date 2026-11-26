# Qiyana (2-cost AttackFighter) · `DA_Qiyana19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6037882.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6037882.Set19.Shipping.pbe`

- **Role** AttackFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 2, pool 25; traits: True Damage, Renegade
- **HP** 750 / 1350 / 2430 · **AD** 45 / 67.5 / 101.25 · **AS** 0.8 · **Range** 1 · **Armor** 40 · **MR** 40 · **Mana** 0 / 40

### Ability: Shuffled Playlist

> Passive: Qiyana's ring changes color periodically, giving her Ability bonus effects.
> 
> Active: Dash to strike enemies in a line, dealing 30/45/70 × AP + 210/315/475 × AD physical damage to the target and 0.5 × PhysicalDamageCalc1 to other enemies hit.
> 
> Red: Deal 20% bonus damage.
> Green: Heal for 20% of damage dealt.
> Blue: Refund 10 Mana.
> Gold: Gain 1 gold and randomly use another effect. (Gold Gained: ⟨live⟩)

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 45 | 67.5 | 101.25 |
| GreenHealPercent | 0.2 | 0.2 | 0.2 |
| BlueManaRefund | 10 | 10 | 10 |
| GoldAmount | 1 | 1 | 1 |
| RedBonusDamagePercent | 0.2 | 0.2 | 0.2 |
| DamageAD | 210 | 315 | 475 |
| DamageAP | 30 | 45 | 70 |
| SecondaryDamagePercent | 0.5 | 0.5 | 0.5 |
| RedWeight | 1 | 1 | 1 |
| GreenWeight | 1 | 1 | 1 |
| BlueWeight | 1 | 1 | 1 |
| GoldChanceIndependent | 0.1 | 0.1 | 0.2 |
| TimeRingChange | 1.5 | 1.5 | 1.5 |
| WaveNumHexesBehindTarget | 2 | 2 | 2 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 30/45/70 × AP + 210/315/475 × AD
- `PhysicalDamageCalc2` = 0.5 × PhysicalDamageCalc1

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Qiyana19_Attack`: launch 0.2992 s (8.98 ticks), variants 0.2992, 0.3067, 0.307; animation length 2.1 s (63 ticks); release at base AS 0.2992 s (8.98 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Qiyana19_Spell` (chrono `–`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Qiyana19_Attack` | Chronos | 1.9667 | LaunchAttack 0.2992, LaunchAttack 0.3067, LaunchAttack 0.307, Unlock 0.5867, Unlock 0.7867, Unlock 0.84 |
| `CD_Qiyana19_CastAnimMove` | Chronos | 1.5006 | MovementEnd 0.4004, Fire 0.7299, PrintGold 0.7784, ManaUnlock 1.2495, Unlock 1.4916 |
| `CD_Qiyana19_CastAnimNoMove` | Chronos | 1.1016 | Fire 0.3498, PrintGold 0.3779, ManaUnlock 0.8491, Unlock 1.0912 |
| `CD_Qiyana19_Celebration` | Chronos | 7 | Default 0, Loop 2.0324 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Qiyana19_Spell`, `GA_ShopEvents`, `GA_TrueDamage19_PlayChronoOnTraitActivation`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Qiyana19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Abilities/GA_Qiyana19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Qiyana19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Qiyana19_Spell.txt

### Changed since `rls-19.1.0.6028987.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Qiyana`, D1); the mana lock (with Blue's refund) and the
  next attack after a cast checked on VOD6 to a tick (E2)
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has her at 1-5)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed at 2 stars: HP 1425 = 1350 + Heartsteel's Sett 75; AD 68, armor and MR 40, mana 40, range 1 | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackFighter: 10 per attack, no regen | confirmed (+10 steps, casts at 40) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.2992 s (8.98 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable | |
| Q7 | Cast time: cast start to the next attack starting | 'Unlock' 1.0912 s: 34 ticks (NoMove) | confirmed: the next attack's mana 44 / 44 / 43 ticks after the cast (engine 43) | E2 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 'ManaUnlock' 0.8491 s: 26 ticks | confirmed: Blue's +10 shows 27 ticks after the bar empties (26 + the tick after the fill) | E2 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 1 GE_SimulateLaunchAttack at 'Fire' | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | cancels (CancelAbilitiesWithTag Combat.Attacking) | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | target DamageAP x AP + DamageAD x AD; others x SecondaryDamagePercent; Red +20% | predicted | D1 |
| Q14 | Passives and other mechanics that need modelling | the ring: Red +20% damage, Blue 10 mana, Green heal, Gold gold | Red and Blue by the ring's colour at the cast, the ring cycling Red -> Green -> Blue (D2); Green and Gold change no damage | D1, D2 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |
| Q16 | Does she dash before the wave against stationary enemies? | she picks the hex within her range of the target with the most enemies in the line through it; her own hex -> no dash | simulated without the dash (NoMove); VOD6's three casts played NoMove (the refund at 27 ticks, not Move's 38) | E2 |
| Q17 | How fast does the ring switch, and in what order? | every TimeRingChange (1.5 s), to one of the other two at random | **open**: simulated as a cycle (owner, D2) at 1.5 s; E2's three Blue casts 3.13 and 3.48 s apart need ~1.1 s per colour for a cycle, or the random pick (1 in 4) | E2, D2 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18, 60 fps; client rls-19.1.0.5986652, not exported: the simulator's newest is 5986094). Round 1-5:
Qiyana 2 stars with one item; Heartsteel (3) on the board (Sett among its members). The panel lists a third trait,
Collab, which 5986094 doesn't give her. Mana from `tools/vod_text_changes.py --field mana` (crops read by eye).

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f12150, f12600 (round 1-5) | 60 | inspection panel | 1425/1425, x/40, range 1 hex, Front, Attack Fighter; AD 68, AP 10%, armor 40, MR 40, AS 0.98 then 1.42, crit 35% | HP 1350 + 75 (Heartsteel SettHealth, Sett fielded), AD 67.5, armor, MR, mana match; the AS sources (item, traits) not identified | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f12088-12756 | 60 | mana text; the board at each cast | 10, 20, 30 at f12088, f12152, f12215; casts f12273, f12461, f12670 (blue wave each time); +10 at f12327, f12515, f12724 (+54 frames each); the next +10 at f12361, f12549, f12756 (+88, +88, +86) | Blue's refund at 'ManaUnlock': 27 ticks = 26 + the tick after the fill (NoMove; Move would be 38); the next attack 44 / 44 / 43 ticks after the cast, engine 43 | Q2, Q7, Q9, Q16 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Qiyana`):
  - **Ring (GA_Qiyana19_PassiveRingRoulette):** ChangeColor at once and every TimeRingChange (1.5 s, looping timer):
    the new colour is one of the two others, by RedWeight / GreenWeight / BlueWeight (1 each), so the long-run
    shares are 1/3 each (`roulette_shares`). In PvP rounds a GoldChanceIndependent roll adds Gold (no combat power).
  - **Cast (GA_Qiyana19_Spell):** mana lock (0x2a1e); colour tags read at the cast. The dash hex: the hex within
    her range of the target with the most enemies in the line offset behind it (LineWidth 440); her own hex ->
    CD_Qiyana19_CastAnimNoMove (Fire 0.3498, ManaUnlock 0.8491, Unlock 1.0912 s), else CastAnimMove (0.7299,
    1.2495, 1.4916 s). 'Fire': GE_SimulateLaunchAttack, the wave aimed WaveNumHexesBehindTarget x 214.5 units
    behind the target.
  - **Wave:** 'Wave' projectile (spawned 0.3779 s, 1200 units/s, box 100 x 440). Overlaps: her target ->
    GE_Qiyana19_PrimaryDamage (PhysicalDamageCalc1 = DamageAP x AP + DamageAD x AD), others -> _SecondaryDamage
    (Calc2 = 0.5 x Calc1); physical, AOE, on-spell, RollIfCanSpellCrit. Red: the _Red effects add Calc x
    RedBonusDamagePercent.
  - **ManaUnlock:** lifts the lock; Blue: GE_Qiyana19_ManaRefundBlue (+BlueManaRefund). 'Unlock': FinishCasting.
  - **Simulated:** NoMove; the colour averaged like crits (I6, replaced by D2): damage x (1 + 0.2 x 1/3), refund 10 x 1/3 at
    'ManaUnlock' (paid during the cast, E2); the wave hits every dummy within 220 units of its path, each when the
    box's front reaches it.

- 2026-11-18, D2 (owner: "it should probably cycle between them"): the ring cycles Red -> Green -> Blue
  (`Qiyana.RING`), Red at combat start, one colour every TimeRingChange (1.5 s, the build); a cast takes the colour
  at its start tick: Red x 1.2 damage, Blue +10 mana at 'ManaUnlock'. The rate is open (Q17).
