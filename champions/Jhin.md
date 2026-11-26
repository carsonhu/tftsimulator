# Jhin (4-cost AttackSpecialist_Ammo) · `DA_Jhin19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6037882.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6037882.Set19.Shipping.pbe`

- **Role** AttackSpecialist_Ammo: "Specialists generate resources in a unique way." ()
- **Cost** 4, pool 10; traits: Classical, Encore
- **HP** 804 / 1447.2 / 2604.96 · **AD** 30 / 45 / 67.5 · **AS** 0.84 · **Range** 5 · **Armor** 44 · **MR** 44 · **Mana** 4 / 4

### Ability: String Quartet

> Passive: Convert 1% bonus Attack Speed into 0.8% Attack Damage.
> 
> Attacks summon violins that attack in unison, dealing 25/38/124 × AD physical damage and Captivating the target for 4 seconds. Every 4th attack is empowered, dealing 80/120/744 × AD + 14/21/104 × AP physical damage and resetting the violins.
> 
> On the 4th sequence onwards, all violins remain out, Jhin gains infinite range, and attacks pierce, dealing 60% reduced damage for each target hit.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 30 | 45 | 67.5 |
| 4thShotDamageAP | 14 | 21 | 104 |
| DamageReductionPerHit | 0.6 | 0.6 | 0.6 |
| BaseAttackSpeed | 0.84 | 0.84 | 1.04 |
| CaptivateDuration | 4 | 4 | 4 |
| ViolinDamageAD | 25 | 38 | 124 |
| MinDamagePercent | 0.4 | 0.4 | 0.4 |
| ASToADRatio | 0.8 | 0.8 | 0.8 |
| 4thShotDamageAD | 80 | 120 | 744 |
| Num4thShotsToAscend | 3 | 3 | 1 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 25/38/124 × AD
- `PhysicalDamageCalc2` = 80/120/744 × AD + 14/21/104 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Jhin19_Attack_new`: launch 0.534 s (16.02 ticks); animation length 1.6506 s (49.52 ticks); release at base AS 0.534 s (16.02 ticks)
- Attack projectile: DA_Jhin19_AutoAttackProjectile, speed 2600 units/s
- No spell timeline decoded (no spell ability, or the script never reaches a cast end).

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Jhin19_Attack_new` | Chronos | 1.2519 | CustomEventOnAttack1 0, CustomEventOnAttack4 0, CustomLaunchAttack2 0.2508, CustomLaunchAttack3 0.2508, CustomLaunchAttack1 0.534, LaunchAttack 0.534, EncorePiercing 0.7508, Encore 1.0321, Unlock 1.2338 |
| `CD_Jhin19_CastAnim` | Chronos | 0.8387 | Unlock 0.8358 |
| `CD_Jhin19_ViolinAttack` | Chronos | 0.5004 | Shoot 0, Encore 0.494 |
| `CD_Jhin19_ViolinAttackEncore` | Chronos | 0.402 | Shoot 0, Death 0.3997 |
| `CD_Jhin19_ViolinAttackEncore_Piercing` | Chronos | 0.402 | Shoot 0, Death 0.3997 |
| `CD_Jhin19_ViolinAttack_Piercing` | Chronos | 0.5004 | Shoot 0, Encore 0.494 |
| `CD_Jhin19_ViolinDeath` | Chronos | 0.5008 | Despawn 0.3709 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_ForceSequentialAttack_Jhin`, `GA_ShopEvents`, `GA_Jhin19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- `LaunchAttack`: launches or listens for attacks: GA_ForceSequentialAttack_Jhin.txt, GA_Jhin19_Passive.txt
- `OnHitEffectivenessMultiplier`: scales on-hit effects: GA_Jhin19_Passive.txt
- `AttackSpeed`: reads or changes attack speed: GA_Jhin19_Passive.txt
- `GE_UnitStopAttackingMovingCasting`: stops the unit attacking/moving/casting: GA_Jhin19_Passive.txt

### Changed since `rls-19.1.0.6028987.Set19.Shipping.pbe`

- row ViolinDamageAD: 27 / 41 / 124 -> 25 / 38 / 124
- ability text changed

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.Jhin`, D1); the AS -> AD conversion, the launch rhythm,
  the Ammo reload and the ascension's pause checked on VOD6 (E1, E2)
- Keep in the simulator: **yes** (owner, 2026-11-18: VOD6 has him at 1-9 and 1-10)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | AS 0.84, Ammo 4, range 5 confirmed; HP 979 vs 804 (items / traits not identified) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | Ammo: -1 per launch, +4 when empty, AttackLockout / scalar after the launch | confirmed: -1 at each launch; 4 again 36-37 frames after the 4th (18 ticks) | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.534 s; ascended 0.2508 s (CustomLaunchAttack2/3) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | his AS is clamped to BaseAttackSpeed; Silvermere Dawn's Channel2 Override sets it to 0.5 (I5) | not applicable, except Silvermere Dawn: 0.5 (owner, earlier sets; D2) | D1, D2 |
| Q6 | Projectile travel time (ranged only) | attack 2600; violins 3000 (4th: 4200); 4th shot and piercing 4000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | no spell; the ascension pauses him UltDelay / scalar + CD_Jhin19_CastAnim | the pause: 53 ticks from the 3rd 4th shot to the next launch, VOD 54 | E2 |
| Q8 | Does the cast time scale with attack speed? | the delays divide by AS / 0.8 (AS fixed) | predicted (script) | D1 |
| Q9 | Mana lock: from cast start, when can mana be gained again? | no spell | not applicable | |
| Q10 | Does the mana lock scale with attack speed? | no spell | not applicable | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | every launch (custom ones too) is a LaunchAttack | predicted (script) | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | the ascension stops him (GE_UnitStopAttackingMovingCasting) | modelled: the attack restarts after it | D1 |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | violins Calc1 x NumViolins (1, 2, 3, 4 per cycle); 4th shot Calc2; ascended: piercing x1 then x0.4 | predicted | D1 |
| Q14 | Passives and other mechanics that need modelling | AS -> AD (0.8), the 4-attack sequence, the ascension, Encore copies | AS -> AD confirmed (16% AD at +20% AS); the ascension after the 3rd 4th shot seen (range 44 at 8:14) | E1, E2 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |
| Q16 | Encore copies: do the damage terms (Encore effectiveness, NumViolins, the piercing multiplier) multiply or add? | GAS adds MultiplyAdditive terms (1 + sum(v - 1)); added, a piercing Encore violin on a second enemy (0.25 + 0.4 - 1) would be negative | simulated as a product (D1) | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

VOD6 = `F:/Outplayed/Teamfight Tactics PBE/Teamfight Tactics PBE_11-18-2026_18-15-31-219/` `…PBE_11-18-2026_18-40-41-766.mp4` (owner's
clip, 2026-11-18, 60 fps; client rls-19.1.0.5986652, not exported: the simulator's newest is 5986094). Round 1-10:
Jhin 1 star with two items. Panel read every second (7:56-8:25); Ammo from `tools/vod_text_changes.py --field mana`.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 7:57-8:25 (round 1-10) | 60 | inspection panel each second | 979/979, x/4, range 5 Hex (44 Hex from 8:14 to the round's end), Back, Attack Specialist; AS 0.84 throughout; AD 35 / 16% at the start, rising about 11% a second to 122 / 307% (the two items' attack speed stacking) | AS clamped to BaseAttackSpeed; AD 16% = 0.8 x 20% bonus AS at the start (the items' base AS), and AD keeps following the AS stacking; the range 44 after the ascension (GE_Jhin19_UltiForm) | Q1, Q14 |
| E2 | 2026-11-18 | rls-19.1.0.5986652 (client) | VOD6 f28655-30196 | 60 | Ammo text | 3,2,1,0 then 4 and so on; launches f28655, 28725, 28797, 28923, 28994, 29066, 29138, 29208, 29280, 29352, 29483, 29553, 29661, 29731, 29803, 29875, 29946, 30018, 30088, 30160; reloads (0 -> 4) 37 / 36 / 36 / 36 / 35 / 36 frames after each 4th launch | launches 70 / 72 frames (35 / 36 ticks) apart, the engine's; two gaps of 126 / 131 frames (a retarget, not modelled); the reload 18 ticks after the 4th launch (AttackLockout / scalar = 17.1 -> 18); after the 3rd 4th launch (f29553) the next launch 108 frames (54 ticks) later, engine 53 (UltDelay 18 + CastAnim 27 + piercing windup 8) | Q2, Q7, Q14 |

## Decisions and notes

- 2026-11-18, D1 (implemented, `set19champs.Jhin`):
  - **AS -> AD (GE_Jhin19_ASToADConverter, infinite):** AttackSpeed Override 1.0 on Channel0; AttackDamage AddBase on
    Channel2 = ASToADRatio x AttackSpeed (evaluated up to Channel1) - ASToADRatio; AttackSpeed at least and at most
    BaseAttackSpeed on Channel2. Modelled with `stats.AttributeBased` (not cached; follows later bonuses).
  - **Ammo (GA_Jhin19_Passive 0x8be2):** every LaunchAttack (non-exact, custom launches too): GE_Jhin19_AmmoTracker
    (-1), GE_Jhin19_BlockAttackTemporarily for AttackLockout / GetJhinASScalar (AttackSpeed / 0.8), then Ammo 0 ->
    GE_Jhin19_Reload (+4). Never delays an attack at his fixed AS.
  - **Sequence:** CurrentAttackCounter 1..4 (+1 at each launch). CustomEventOnAttack1 (attack start) spawns violin n
    (positions at 45 / -45 / 90 / -90 degrees behind him) unless ascended. LaunchAttack (attacks 1-3): ShootViolins
    (3000); Custom.1 (attack 4): EncoreDelay copy, 4thShotCounter + 1, ShootViolins(4200), CD_Jhin19_4thShotMis.
    ShootViolins: each violin plays CD_Jhin19_ViolinAttack (speed GetJhinASScalar) at his target; the first
    'ViolinMis' to arrive (DealtDamage) captivates and applies GE_Jhin19_ViolinDamage (Calc1, Encore effectiveness 1,
    NumViolins); its 'Encore' event (Encore active) replays CD_Jhin19_ViolinAttackEncore, the first arrival dealing
    Calc1 x r x NumViolins. After the 4th's violin attacks (counter 4, not ascended) the violins despawn.
  - **4th shot:** GE_Jhin19_4thShotDamage (Calc2; AppliesOnSpell, AppliesOnHit.IsAttack; RollIfCanSpellCrit) +
    Captivate; Encore: CD_Jhin19_4thShotMisEncore EncoreDelay / scalar later, GE_Jhin19_4thShotDamageEncore (Calc2 x
    r, AppliesOnHit, on-hit at r).
  - **Ascension:** 4thShotCounter >= Num4thShotsToAscend: WaitDelay(UltDelay / scalar) -> GE_UnitStopAttackingMoving
    Casting + CD_Jhin19_CastAnim; 'Unlock' -> GE_Jhin19_UltiForm (AttackRange 44, ChronoTags.Dynamic.CustomAttack.2),
    the stop removed.
  - **Ascended:** no more spawns (the 4 violins stay). Custom.2 (0.2508 s): ShootViolinsPiercing + CD_Jhin19_PiercingMis
    (GE_Jhin19_PiercingAutoAttack: BasicAttackDamage x multiplier, AOE, CanBeDodged, IsAttack, the attack's crit).
    Custom.3 (4th): Encore copy, ShootViolinsPiercing, CD_Jhin19_4thPiercingMis (GE_Jhin19_4thShotPiercingDamage).
    Every piercing projectile: to ProjectDistanceThroughTarget(3000), 4000 units/s, box 100 x 300; per projectile
    (ChronoToDamageMultiplierMap) the multiplier starts at 1 and after each enemy becomes max(m x (1 - 0.6), 0.4).
    Each violin's 'ViolinMisPierce' deals GE_Jhin19_ViolinDamage_Piercing (Calc1 x Encore x multiplier), no
    NumViolins.
  - **Damage terms multiply** (Q16): a piercing Encore violin's second enemy would take 0.25 + 0.4 - 1 < 0 if the
    MultiplyAdditive terms added; the owner's Seraphine reading (champions/SeraphineIndie.md D2) is the same rule.
  - **Simulated:** violins fly from his hex; a piercing line hits the dummies within 150 units of it, each when the
    box's front reaches it; pierced enemies' on-hit effects are at full effectiveness; the retarget pauses (E2) not
    modelled.
- 2026-11-18, D2 (owner, from earlier sets; no VOD this set): **Silvermere Dawn overrides his fixed AS to 0.5.** Its
  GE_Artifact_SilvermereDawn_Stats Overrides AttackSpeed on Channel2, the same channel as his converter's
  BaseAttackSpeed bounds. The engine had applied the bounds after the Override (0.84); now an Override is its
  channel's result (ledger I5, as GAS's aggregator does). His AS -> AD reads AttackSpeed up to Channel1, so it is
  unchanged; GetJhinASScalar follows the 0.5 (0.625), so his lockout, ascension and Encore delays lengthen.
