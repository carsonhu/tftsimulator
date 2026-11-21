# Olaf with the hero augment Axe Crescendo (AttackMarksman) · `DA_Olaf19_HeroAugment_Override`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** AttackMarksman: "Attacks grant 10 Mana." (ManaPerAttack + 10; ManaMax at least 10)
- **Cost** 0, pool –; traits: Pentakill, Juggernaut
- **HP** 500 / 900 / 1620 · **AD** 45 / 67.5 / 101.25 · **AS** 0.7 · **Range** 4 · **Armor** 25 · **MR** 25 · **Mana** 0 / 50
- Other stats: CritChance 0

### Ability: Axe Crescendo

> For the next 3 attacks, throw flaming axes that deal 140/210/335 × AD + 15/20/30 × AP physical damage. Each time this is cast, increase the number of flaming axe throws by 1 for the rest of combat.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| NumAttacks | 3 | 3 | 3 |
| AutoAttackDamage | 45 | 67.5 | 101.25 |
| ExtraAttacksPerCast | 1 | 1 | 1 |
| ADDamage | 140 | 210 | 335 |
| APDamage | 15 | 20 | 30 |

Formulas (as stored; AD and AP are multipliers):

- `PhysicalDamageCalc1` = 140/210/335 × AD + 15/20/30 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Olaf19_Attack`: launch 0.32 s (9.6 ticks), variants 0.32, 0.4; animation length 1.1667 s (35 ticks); release at base AS 0.3918 s (11.75 ticks)
- Attack projectile: DA_Olaf19_AutoAttackProjectileL_HeroAugment, speed 2000 units/s
- Spell `GA_Olaf19_HeroAugment` (chrono `CD_Olaf19_Empower_HeroAugment`): cast ends 0 s (0 ticks), next attack can start 0.0333 s (1 ticks), mana lock removed –; ended by `FinishCasting via OnEventBegin:CD_Olaf19_Empower_HeroAugment:Empower`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Olaf19_Attack` | Chrono | 1 | LaunchAttackVariant1 0.32, LaunchAttackVariant2 0.32, LaunchAttack 0.4, CustomLaunchAttack1 0.5, Unlock 0.6 |
| `CD_Olaf19_Empower_HeroAugment` | Chrono | 2.0821 | Default 0, Empower 0, LoopMarker 0.6603 |
| `CD_Olaf19_Revive` | Chrono | 1.5012 | KillableAgain 0.5006, Unlock 1.4879 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_Olaf19_EmpoweredAttack_HeroAugment`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchProjectileAttack`, `GA_ShopEvents`, `GA_Olaf19_HeroAugment`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Olaf19_HeroAugment.txt
- `LaunchAttack`: launches or listens for attacks: Abilities/GA_Olaf19_EmpoweredAttack_HeroAugment.txt, Abilities/GA_Olaf19_HeroAugment.txt, Abilities/GA_Olaf19_Passive.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Olaf19_HeroAugment.txt
- `GE_UnitStopAttackingMovingCasting`: stops the unit attacking/moving/casting: Abilities/GA_Olaf19_Passive.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

- nothing in this unit's data

<!-- AUTO END -->

## Status

- Worksheet status: **implemented** (2026-11-18, `set19champs.OlafHeroAugment`, D1); panel, mana and the cast's rhythm
  checked against VOD5
- Keep in the simulator: **yes** (owner, 2026-11-18: hero augment units are separate champions; `roster.json`
  `hero_augments`)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | confirmed with his item (1★) | E1 |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | AttackMarksman | confirmed: 10 per attack, no regen | E2 |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.32 s (9.6 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | speed 2000 | predicted | |
| Q7 | Cast time: cast start to the next attack starting | 0.0333 s (1 ticks) | confirmed with the empowered rhythm: the first normal attack after the throws pays 77 ticks after the filling attack, engine 77 | E2 |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | the tick after the last empowered launch (script, D1); consistent with E2 | D1, E2 |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | predicted: 0; the empowered throws are attack launches (LaunchAttack.Custom.1, heard by on-launch items) whose mana the lock eats | D1 |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted (script read: D1); no damage number read yet | D1 |
| Q14 | Passives and other mechanics that need modelling | see ability text | the growing axe count (D1); Pentakill (B25); Juggernaut is durability only | D1 |
| Q15 | Can this unit be simulated realistically? | | **yes**, implemented 2026-11-18 | D1 |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

Source for all rows below: VOD5 (`…PBE_11-18-2026_0-57-11-500.mp4`, session folder 0-33-59-673, 60 fps), the owner's
PBE recording in the score mode, build `rls-19.1.0.5973071`; Olaf with Axe Crescendo 1★, round 1-5, combat start f18522
(Quicksilver's first +3% at f18582). Ticks count from combat start.

| # | Date | Build | VOD time / frames | fps | Measured | Values | Result | Question |
|---|---|---|---|---|---|---|---|---|
| E1 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 5:09 (f18560) | 60 | inspection panel | 500/500, 0/50, no regen; AD 45, AS 0.80, crit 20%, range 4 hexes, Attack Marksman; Quicksilver; Bodyguard (2) from the board. Before the augment (f16002) the panel showed the base Olaf: 650 HP, Attack Tank | 0.7 x 1.15 AS, 0 + 20 crit: as built | Q1 |
| E2 | 2026-11-18 | rls-19.1.0.5973071 | VOD5 f18574-19295 (`tools/vod_text_changes.py`, mana and as) | 60 | mana text | +10 at 26, 63, 99, 133 (gaps 37, 36, 34, 33.5) and 166.5 (fills: cast, 0 shown); nothing until +10 at 243.5 (77 ticks after the fill), then 274.5, 304.5, (357.5 after a 53-tick gap: a retarget), 386.5 (fills: cast) | engine (Quicksilver, from his first attack): gaps 37, 36, 35, 34; fill to the next normal attack's mana 77; then gaps 32, 30 (the clip 31, 30, its attacks 14 ticks later in Quicksilver's ramp); the second cast on the 5th attack, as the clip. His first attack came 14 ticks after the engine's (a walk) | Q2, Q7, Q9 |

## Decisions and notes

- 2026-11-18 (owner): hero augment versions are separate champions in the simulator; every hero augment is on a tank,
  which the roster excludes anyway.
- 2026-11-18, D1 (implemented, `set19champs.OlafHeroAugment`, label "Olaf (Axe Crescendo)"):
  - **Cast (GA_Olaf19_HeroAugment):** NumAttacks = the row (2) + Stack; mana lock; the Empower event (0 s) gives the
    CustomAttack.1 tag and finishes the cast (cast lock 1 tick; it cancels an attack in progress). Each empowered
    launch counts; at NumAttacks GE_Olaf19_CastStacker_HeroAugment adds ExtraAttacksPerCast (1) to Stack and the
    empower ends; the mana lock is removed one tick later.
  - **Attacks:** CD_Olaf19_Attack's HeroAugment groups: normal attacks release at 0.32 s of a 1.0 s animation,
    empowered ones at 0.5 s of 1.1667 s (both rate-scaled). The empowered launch throws only the BigAxe (1700 units/s):
    150/225/360 x AD + 15/20/30 x AP physical, no on-hit, crits only with Precision.
  - **Not on this unit:** the base Olaf's heal passive and death revive.

