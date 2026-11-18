# Items

How each Set 19 item is implemented, and what it rests on (the lighter form of the champion worksheets, decision
D6). One row per item. An item whose timing needs VOD evidence (stack intervals, mana timing, on-hit vs on-release)
also gets a worksheet in `items/<Name>.md`, linked from its row; every other item lives in this table only.

**Where numbers come from.** Every number is read from the selected build: an item's stats effect
(`items.<key>.effects`: attribute, operation, curve row, values; ledger P8) and its curve rows. The item's script
(`ability_refs`, decoded in the build's `ga_scripts.zip` under `Item_Shared/`) decides how its mechanic works and is
cited by file and offset in the class docstring. Nothing is typed in.

**Status:** not started / stats only, not listed (complete from its stats but no damage effect, so not in a slice) /
implemented (stats) (complete from its stats effect and tags, no script) / implemented (script read) / confirmed (VOD)
/ out of scope (with the reason). Scripted items are not listed until their script is implemented: a stats-only
Guinsoo's would show a wrong number.

**Columns.** *Stats effect*: the attributes the item's effect modifies in build rls-19.1.0.5973071 (from data).
*Script*: the item's ability, or none. *Evidence / notes*: assumptions and evidence, with dates.

## Craftables

| Item | Key | Stats effect (attributes) | Script | Status | Evidence / notes |
|---|---|---|---|---|---|
| Adaptive Helm | `DA_AdaptiveHelm` | IncomingManaMultiplier, MagicResist, ManaPerSecond | `GA_AdaptiveHelm` | not started | |
| Archangel's Staff | `DA_ArchangelsStaff` | AbilityPower, ManaPerSecond | `GA_ArchangelsStaff_RampingStats` | not started | |
| Bloodthirster | `DA_Bloodthirster` | AbilityPower, AttackDamage, MagicResist, Omnivamp | `GA_Bloodthirster` | not started | |
| Blue Buff | `DA_BlueBuff` | AbilityPower, AttackDamage, ManaPerSecond | `GA_BlueBuff` | not started | |
| Bramble Vest | `DA_BrambleVest` | Armor, HealthMax | `GA_BrambleVest` | not started | |
| Crownguard | `DA_Crownguard` | AbilityPower, Armor, HealthMax, IncomingHealMultiplier, IncomingShieldMultiplier | `GA_Crownguard` | not started | |
| Deathblade | `DA_Deathblade` | AttackDamage | none | not started | "15% additional AD from all sources": three more AttackDamage modifiers with operations `Multiplicitive` (×) and MultiplyAdditive; meaning to check before use. No script. |
| Dragon's Claw | `DA_DragonsClaw` | HealthMax, MagicResist | none | not started | `GE_DragonsClaw_HPRegen` (period 2 s); defensive. |
| Edge of Night | `DA_EdgeOfNight` | AbilityPower, Armor, AttackDamage, AttackSpeed | `GA_EdgeOfNight` | not started | |
| Evenshroud | `DA_Evenshroud` | HealthMax, MagicResist | none | not started | `GE_Evenshroud_ApplyGA` grants an ability though the item has none listed. |
| Gargoyle Stoneplate | `DA_GargoyleStoneplate` | Armor, HealthMax, MagicResist | none | not started | `GE_GargoyleStoneplate_TargetedBuff` is conditional (+10 armor/MR per targeting enemy); defensive. |
| Giant Slayer | `DA_GiantSlayer` | AbilityPower, AttackDamage, AttackSpeed, OutgoingDamageMultiplier | `GA_GiantSlayer` | not started | |
| Guinsoo's Rageblade | `DA_GuinsoosRageblade` | AbilityPower, AttackSpeed | `GA_GuinsoosRageblade` | not started | |
| Hand Of Justice | `DA_HandOfJustice` | CritChance, ManaPerSecond | `GA_HandOfJustice` | not started | |
| Hextech Gunblade | `DA_HextechGunblade` | AbilityPower, AttackDamage, ManaPerSecond, Omnivamp | `GA_HextechGunblade` | not started | |
| Infinity Edge | `DA_InfinityEdge` | AttackDamage, CritChance | none | implemented (stats) | 2026-11-17: stats + Precision (I1, I2); no script. |
| Ionic Spark | `DA_IonicSpark` | AbilityPower, HealthMax, MagicResist | none | not started | `GE_IonicSpark_ApplyGA` grants an ability though the item has none listed. |
| Jeweled Gauntlet | `DA_JeweledGauntlet` | AbilityPower, CritChance | none | implemented (stats) | 2026-11-17: stats + Precision (I1, I2); no script. |
| Kraken's Fury | `DA_KrakensFury` | AttackDamage, AttackSpeed, MagicResist | `GA_KrakensFury` | not started | |
| Last Whisper | `DA_LastWhisper` | AttackDamage, AttackSpeed, CritChance | `GA_LastWhisper` | not started | |
| Morellonomicon | `DA_Morellonomicon` | AbilityPower, HealthMax, ManaPerSecond | `GA_Morellonomicon` | not started | |
| Nashor's Tooth | `DA_NashorsTooth` | AbilityPower, AttackSpeed, CritChance, HealthMax, ManaPerAttack | `GA_NashorsTooth` | not started | |
| Protector's Vow | `DA_ProtectorsVow` | Armor, MagicResist, ManaPerSecond | `GA_ProtectorsVow` | not started | |
| Quicksilver | `DA_Quicksilver` | AttackSpeed, CritChance, MagicResist | `GA_Quicksilver` | not started | |
| Rabadon's Deathcap | `DA_RabadonsDeathcap` | AbilityPower | none | not started | "15% additional AP from all sources": as Deathblade, on AbilityPower. No script. |
| Red Buff | `DA_RedBuff` | AttackSpeed, OutgoingDamageMultiplier | `GA_RedBuff` | not started | |
| Spear of Shojin | `DA_SpearOfShojin` | AbilityPower, AttackDamage, ManaPerAttack, ManaPerSecond | none | implemented (stats) | 2026-11-17: stats; 5 mana per attack paid with the role mana (I3, predicted). No script. |
| Spirit Visage | `DA_SpiritVisage` | HealthMax, IncomingDamageMultiplier, ManaPerSecond | `GA_SpiritVisage` | not started | |
| Steadfast Heart | `DA_SteadfastHeart` | Armor, CritChance, HealthMax, IncomingDamageMultiplier | none | not started | HealthMax and IncomingDamageMultiplier magnitudes computed in game; defensive. |
| Sterak's Gage | `DA_SteraksGage` | AttackDamage, HealthMax | `GA_SteraksGage` | not started | |
| Striker's Flail | `DA_StrikersFlail` | AttackSpeed, CritChance, HealthMax, OutgoingDamageMultiplier | `GA_StrikersFlail` | not started | |
| Sunfire Cape | `DA_SunfireCape` | Armor, HealthMax | `GA_SunfireCape` | not started | |
| Tactician's Cape | `DA_TacticiansCape` | MaxTeamSizeBonus | `GA_TacticiansCape` | not started | |
| Tacticians Crown | `DA_TacticiansCrown` | MaxTeamSizeBonus | `GA_TacticiansCrown` | not started | |
| Tacticians Shield | `DA_TacticiansShield` | MaxTeamSizeBonus | `GA_TacticiansShield` | not started | |
| Thief's Gloves | `DA_ThiefsGloves` | CritChance, HealthMax | `GA_ThiefsGloves` | not started | |
| Titan's Resolve | `DA_TitansResolve` | Armor, AttackSpeed | `GA_TitansResolve` | not started | |
| Void Staff | `DA_VoidStaff` | AbilityPower, AttackSpeed, ManaPerSecond | `GA_VoidStaff` | not started | |
| Warmog's Armor | `DA_WarmogsArmor` | HealthMax | none | stats only, not listed | Stats only (HP), no damage effect: added when an HP-scaling champion needs it. |

Artifacts, radiants, emblems and the rest are added when needed.
