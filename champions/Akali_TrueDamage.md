# Akali (5-cost MagicFighter) · `DA_Akali_TrueDamage19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.5995286.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.5995286.Set19.Shipping.pbe`

- **Role** MagicFighter: "Attacks grant 10 Mana. Gain 5-30% Attack Speed (based on Stage)." (ManaPerAttack + 10; AttackSpeed MultiplyAdditive 1.05/1.1/1.2/1.3 (stage 1-2/3/4/5+); MovementSpeed + 200; ManaMax at least 10)
- **Cost** 5, pool 9; traits: True Damage, Freestyle
- **HP** 1200 / 2160 / 3888 · **AD** 50 / 75 / 112.5 · **AS** 0.9 · **Range** 1 · **Armor** 65 · **MR** 65 · **Mana** 0 / 50
- **Unlock**: Earn 350 True Damage Bling without K/DA Akali unlocked.

### Ability: Killin' like Domino

> B-Side Passive: After every 4 takedowns, gain 1/1/10 Player Health. (⟨live⟩/4)
> 
> Active: Rapidly slash through the current target, dealing 550/825/9999 × AP magic damage, increased by 50% against Tanks. While casting, gain 25% Durability and become untargetable by attacks. 
> 
> Afterwards, blink over the target and throw a bomb that deals 620/930/9999 × AP magic damage split amongst all enemies within 2/2/8 hexes.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 50 | 75 | 112.5 |
| SlashTotalDamage | 550 | 825 | 9999 |
| NumSlashes | 6 | 6 | 6 |
| TankDamageIncrease | 1.5 | 1.5 | 1.5 |
| ShroudDuration | 2 | 2 | 2 |
| StrikeDuration | 1 | 1 | 1 |
| ExplosionDamage | 620 | 930 | 9999 |
| ShroudHexRadius | 2 | 2 | 8 |
| ShroudDurability | 0.25 | 0.25 | 0.25 |
| ASidePassiveKillReq | 5 | 5 | 5 |
| ASidePassiveTakedownReq | 4 | 4 | 4 |
| ASideTakedownHealthReward | 1 | 1 | 10 |
| ASideKillHealthReward | 3 | 4 | 30 |
| BSidePassiveKillReq | 5 | 5 | 5 |
| BSidePassiveTakedownReq | 4 | 4 | 4 |
| BSideTakedownGoldReward | 2 | 3 | 20 |
| BSideKillGoldReward | 5 | 8 | 60 |
| BSideFreeRerollsReward | 1 | 2 | 10 |

Formulas (as stored; AD and AP are multipliers):

- `MagicDamageCalc1` = 550/825/9999 × AP
- `MagicDamageCalc2` = 1 × MagicDamageCalc1 ÷ 6
- `DurabilityCalc1` = 1 + -0.25
- `MagicDamageCalc3` = 620/930/9999 × AP

### Timing the client predicts (unverified for Set 19)

- Attack chrono `CD_Akali_TrueDamage19_Attack`: launch 0.3385 s (10.16 ticks), variants 0.3385, 0.3685; animation length 2.3 s (69 ticks); release at base AS 0.3385 s (10.16 ticks)
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Akali_TrueDamage19_Spell` (chrono `CD_Akali_TrueDamage19_Spell`): cast ends –, next attack can start –, mana lock removed –; **no cast end found**
  - notes: curve CT_Akali_TrueDamage19.TankDamageIncrease input unresolved (self.OwnerLevel), used star 2 ×1; curve CT_Akali_TrueDamage19.NumSlashes input unresolved (self.OwnerLevel), used star 2 ×1; curve CT_Akali_TrueDamage19.ShroudHexRadius input unresolved (self.OwnerLevel), used star 2 ×1; curve CT_Akali_TrueDamage19.ShroudDuration input unresolved (self.OwnerLevel), used star 2 ×1; curve CT_Akali_TrueDamage19.StrikeDuration input unresolved (self.OwnerLevel), used star 2 ×1; chrono not found K2Node_CustomEvent_StrikeChrono_1 ×1

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Akali_TrueDamage19_3StarSpell` | Chronos/3Star | 1.5403 | Default 0, Explosion 1.3865, Return 1.4068 |
| `CD_Akali_TrueDamage19_3StarSpellStrike` | Chronos/3Star | 0.75 | Teleport 0.0241, Dash 0.1788 |
| `CD_Akali_TrueDamage19_3StarStrikeTar` | Chronos | 0.1988 | End 0.1138 |
| `CD_Akali_TrueDamage19_Attack` | Chronos | 2.3 | LaunchAttack 0.3385, LaunchAttack 0.3685, Unlock 0.6664, Unlock 0.92 |
| `CD_Akali_TrueDamage19_Spell` | Chronos | 0.4981 | StartShroud 0.1599 |
| `CD_Akali_TrueDamage19_SpellShroudDetonate` | Chronos | 1.3342 | Default 0, Explosion 0.4317, ReturnFacing 0.9104, Return 1.0006 |
| `CD_Akali_TrueDamage19_SpellStrike` | Chronos | 0.9979 | Teleport 0.0418, Dash 0.1965, StrikeDamage 0.574 |

### Scripts on the unit

`GA_DoLaunchAttackLogic`, `GA_SetAATarget`, `GA_PlayAdditionalChronoOnStarUp`, `GA_TrueDamage19_PlayChronoOnTraitActivation`, `GA_Play3Star5CostCamera`, `GA_MoveToTarget`, `GA_Celebration`, `GA_Death`, `GA_AutoAttack`, `GA_LaunchMeleeAttack`, `GA_Akali_TrueDamage19_Spell`, `GA_ShopEvents`, `GA_Akali_TrueDamage19_Passive`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Abilities/GA_Akali_TrueDamage19_Spell.txt
- `GE_ManaLock`: applies mana lock: Abilities/GA_Akali_TrueDamage19_Spell.txt
- `GE_UnitStopAttackingMovingCasting`: stops the unit attacking/moving/casting: Abilities/GA_Akali_TrueDamage19_Spell.txt

### Changed since `rls-19.1.0.5986094.Set19.Shipping.pbe`

- nothing in this unit's data

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
| Q4 | Attack windup at base AS (attack start to hit / release) | 0.3385 s (10.16 ticks) | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | – | open | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | open | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | – | open | |
| Q10 | Does the mana lock scale with attack speed? | script does not read AS | open | |
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

