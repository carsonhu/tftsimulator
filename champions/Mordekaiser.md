# Mordekaiser (5-cost MagicFighter) · `DA_Mordekaiser19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5973071.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5973071.Set19.Shipping.pbe`

- **Role** MagicFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive ⟨computed in game: TFTStageMagnitude⟩ → FighterAttackSpeed curve; MovementSpeed + 200; ManaMax at least 10)
- **Cost** 5, pool 9; traits: Pentakill
- **HP** 1200 / 2160 / 3888 · **AD** 75 / 112.5 / 168.75 · **AS** 0.5 · **Range** 1 · **Armor** 65 · **MR** 65 · **Mana** 0 / 60
- **Unlock**: 10 unique star levels of Pentakill

### Ability: Hand of Doom

> Briefly gain 40% Durability. Summon a claw that deals 100/150/800 × AP magic damage in a massive line. The 4 closest enemies take 25% more damage and are pulled towards Mordekaiser.
> 
> For the rest of combat, gain 20% Omnivamp, +1 Attack Range, and replace attacks with a slam that deals 300/480/3000 × AP magic damage to the target and 70/105/1500 × AP damage to other enemies within 2 hexes.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 75 | 112.5 | 168.75 |
| UltDuration | 60 | 60 | 60 |
| NumToYeet | 4 | 4 | 4 |
| StunDuration | 0.5 | 0.5 | 0.5 |
| SlamDamage | 300 | 480 | 3000 |
| SlamAOE | 70 | 105 | 1500 |
| Omnivamp | 0.2 | 0.2 | 0.2 |
| YeetDamage | 100 | 150 | 800 |
| SlamRadius | 2 | 2 | 2 |
| Durability | 0.4 | 0.4 | 0.4 |
| ClawBonusDamageAmp | 0.25 | 0.25 | 0.25 |
| RangeBonus | 1 | 1 | 1 |
| MaxPullDistance | 230 | 230 | 230 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 300/480/3000 × AP
- `MagicDamageCalc2` = 70/105/1500 × AP
- `MagicDamageCalc3` = 100/150/800 × AP
- `DurabilityCalc1` = 0.4

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Mordekaiser19_Attack`: launch 0.6 s (18 ticks); animation length 2.9333 s (88 ticks); release at base AS 0.6 s (18 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Mordekaiser19_Spell` (chrono `CD_Mordekaiser19_Cast`): cast ends 1.5 s (45 ticks), next attack can start 1.5333 s (46 ticks), mana lock removed 1.5 s (45 ticks); ended by `FinishCasting via OnEventBegin:CD_Mordekaiser19_Cast:Empowered`

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Mordekaiser19_3StarKnockup` | Chronos/3Star | 1 | Damage 0.1275, Destroy 0.6521 |
| `CD_Mordekaiser19_3StarSpell` | Chronos/3Star | 44.5788 | Slam 1.9929, Slam 3.8056, Slam 5.5077, Slam 7.1792, Unlock 8.9773 |
| `CD_Mordekaiser19_Attack` | Chronos | 2.6 | LaunchAttack 0.6, CustomLaunchAttack1 0.8, Unlock 1.1732, Unlock 1.35 |
| `CD_Mordekaiser19_Cast` | Chronos | 1.5801 | YeetBuildup 0, Empowered 1.4751 |
| `CD_Mordekaiser19_Claw` | Chronos | 1.6291 | Yeet 0.9858 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_PlayChronoOnTraitActivation`, `GA_Play3Star5CostCamera`, `GA_GainDamageReductionAt3Star`, `GA_ReduceOutgoing3StarDamage`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Mordekaiser19_Spell`, `GA_ShopEvents`, `GA_Mordekaiser19_Whack`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): GA_Mordekaiser19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: GA_Mordekaiser19_Spell.txt, GA_Mordekaiser19_Whack.txt
- `GE_ManaLock`: applies mana lock: GA_Mordekaiser19_Spell.txt

<!-- AUTO END -->

## Status

- Worksheet status: **not started**
- Keep in the simulator: **undecided** (remove if it can't be simulated realistically; give the reason)

## Questions

Each answer needs evidence (an entry in the evidence log) or a reference to a global assumption in
`docs/ASSUMPTIONS.md`. Status: open / predicted (client data only) / confirmed / refuted / not applicable.

| # | Question | Client prediction | Status | Evidence |
|---|---|---|---|---|
| Q1 | Base stats in game match the build (HP, AD, AS, range, armor, MR, mana) | see above | predicted | |
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicFighter | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.6 s (18 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 1.5333 s (46 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 1.5 s (45 ticks) | predicted | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | predicted | |
| Q11 | How many attacks does a cast count as (on-attack effects, attack counters, role mana)? | 0 unless the script says otherwise (G11) | open | |
| Q12 | Does the cast cancel or reset an attack in progress? | see script hints | predicted | |
| Q13 | Ability damage: formula, targets, hit count match the text and variables | see above | predicted | |
| Q14 | Passives and other mechanics that need modelling | see ability text | open | |
| Q15 | Can this unit be simulated realistically? | | open | |

## Evidence log

One row per measurement. VOD times are the video's own timestamps; frames at the stated fps. Cite the build the
VOD was played on (check the patch shown in game or the date against builds/index.json).

| Date | Build | Source (VOD URL @ time) | fps | Measured | Frames / values | Result | Question |
|---|---|---|---|---|---|---|---|

## Decisions and notes

