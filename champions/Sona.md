# Sona (5-cost MagicSpecialist) · `DA_Sona19`

<!-- AUTO BEGIN: written by tools/worksheets.py from build rls-19.1.0.6011486.Set19.Shipping.pbe; edits here are overwritten -->
## Client data: build `rls-19.1.0.6011486.Set19.Shipping.pbe`

- **Role** MagicSpecialist: "Specialists generate resources in a unique way." ()
- **Cost** 5, pool 9; traits: Producer, Collab
- **HP** – · **AD** 0 · **AS** 0.8 · **Range** 10 · **Armor** 50 · **MR** 50 · **Mana** 0 / 220
- **Unlock**: Collab champions are inspired 15 times during player combat.

### Ability: feat. Sona

> Passive: Cannot attack, instead every 3 seconds, gain 30/30/100 + 1 × ManaPerAttack Mana, deal 120/180/1000 × AP magic damage to the 3/3/10 nearest enemies, and 2/2/5 allies gain 40/65/9999 × AP Shield for 3/3/10 seconds. Sona is Unstoppable.
> 
> Active: Unleash a sonic wave across the battlefield, dealing 1500/2400/1e+07 × AP magic damage split between all enemies and Stunning them for 2/2/30 seconds. Allies gain 250/450/99999 × AP Shield split amongst allies for 5/5/10 seconds.

| variable | 1★ | 2★ | 3★ |
|---|---|---|---|
| AutoAttackDamage | 0 | 0 | 0 |
| PassiveShield | 40 | 65 | 9999 |
| PassiveAS | 0 | 0 | 0 |
| PassiveNumAllies | 2 | 2 | 5 |
| KDA_ManaRegen | 0 | 0 | 0 |
| IonicSpark_AttackSpeed | 0 | 0 | 0 |
| Heartsteel_ADAP | 0 | 0 | 0 |
| Pentakill_Health | 0 | 0 | 0 |
| TrueDamage_PercentTrueDamage | 0 | 0 | 0 |
| PassiveCadence | 3 | 3 | 3 |
| ResourceStartCast | 0 | 0 | 0 |
| PassiveDuration | 3 | 3 | 10 |
| ActiveDamage | 1500 | 2400 | 9999999 |
| ActiveStunDuration | 2 | 2 | 30 |
| StatConversionMult | 1 | 1 | 1 |
| ManaRegenConversionMult | 0 | 0 | 0 |
| ManaConversionMult | 0 | 0 | 0 |
| ManaPerAttackConversionMult | 0 | 0 | 0 |
| ManaPerPassiveTick | 30 | 30 | 100 |
| HeartsteelManaRegen | 2 | 2 | 30 |
| HeartsteelAdditionalPassiveAllies | 0 | 0 | 0 |
| HeartsteelAdditionalPassiveEffectiveness | 0 | 0 | 0 |
| PassiveNumEnemies | 3 | 3 | 10 |
| ActiveShield | 250 | 450 | 99999 |
| PassiveDamage | 120 | 180 | 1000 |
| ActiveShieldDuration | 5 | 5 | 10 |

Formulas (as stored; AD and AP are multipliers):

- `ShieldCalc1` = 40/65/9999 × AP
- `MagicDamageCalc2` = 120/180/1000 × AP
- `AttackSpeedCalc1` = 1 + 0 × AP
- `MagicDamageCalc1` = 1500/2400/1e+07 × AP
- `ShieldCalc2` = 250/450/99999 × AP
- `ManaCalc1` = 30/30/100 + 1 × ManaPerAttack

### Timing the client predicts (unverified for Set 19)

- Attack chrono `–`: launch –; animation length –; release at base AS –
- Attack projectile: none (melee or not a fixed projectile)
- Spell `GA_Sona19_Spell` (chrono `CD_Sona19_Spell`): cast ends 2.6 s (78 ticks), next attack can start 2.6333 s (79 ticks), mana lock removed 2.6 s (78 ticks); ended by `FinishCasting via OnEventBegin:CD_Sona19_Spell:Unlock`
  - notes: projectile (hit time depends on travel) ×3

Every timeline in the champion folder that has events (the spell prediction above follows one path through the script; a unit with several cast versions has a timeline for each):

| chrono | folder | length | events (s) |
|---|---|---|---|
| `CD_Sona19_3Star_IncreaseCopySize` | Champion/Chronos | 89.9866 | Default 0, Loop 0.9997 |
| `CD_Sona19_PassivePulse` | Champion/Chronos | 8.0105 | DamagePulse 0.3002, Pulse 0.5063, HeartsteelPulse 0.6995 |
| `CD_Sona19_Spell` | Champion/Chronos | 2.6983 | CalculateWaveSplit 1.2661, Unlock 2.5983 |
| `CD_Sona19_ChangeFormIn` | Trait | 0.5992 | SwapForm 0.5254 |

### Scripts on the unit

`GA_Sona19_Spell`, `GA_PlayAdditionalChronoOnStarUp`, `GA_Sona19_Passive`, `GA_Play3Star5CostCamera`, `GA_Celebration`, `GA_Death`, `GA_SetAATarget`, `GA_ShopEvents`

Script hints (identifiers present in this champion's decoded scripts; leads, not evidence):

- spell cancels an attack in progress (`CancelAbilitiesWithTag` has `Combat.Attacking`): Champion/Abilities/GA_Sona19_Spell.txt
- `LaunchAttack`: launches or listens for attacks: Champion/Abilities/GA_Sona19_Passive.txt, Champion/Abilities/GA_Sona19_Spell.txt
- `GE_SimulateLaunchAttack`: applies the "simulate a launched attack" effect (may count as an attack for on-attack effects): Champion/Abilities/GA_Sona19_Spell.txt
- `GE_ManaLock`: applies mana lock: Champion/Abilities/GA_Sona19_Spell.txt

### Changed since `rls-19.1.0.6005555.Set19.Shipping.pbe`

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
| Q2 | Mana per attack and per second follow the role; when is an attack's mana paid (attack start, release or hit, T3)? | MagicSpecialist | predicted | |
| Q3 | First attack at combat start: when does it land? | G3 | open | |
| Q4 | Attack windup at base AS (attack start to hit / release) | – | predicted | |
| Q5 | Windup at higher AS: shortened, unchanged, or stretched at low AS? | G2 | open | |
| Q6 | Projectile travel time (ranged only) | none | not applicable? | |
| Q7 | Cast time: cast start to the next attack starting | 2.6333 s (79 ticks) | predicted | |
| Q8 | Does the cast time scale with attack speed? | script does not read AS | predicted | |
| Q9 | Mana lock: from cast start, when can mana be gained again? | 2.6 s (78 ticks) | predicted | |
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

