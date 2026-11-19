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
| Adaptive Helm | `DA_AdaptiveHelm` | IncomingManaMultiplier, MagicResist, ManaPerSecond | `GA_AdaptiveHelm` (to 5973071) | confirmed (VOD) | 2026-11-17: non-Tank/Fighter roles get GE_AdaptiveHelm_OtherRoles (10% AD, 10% AP); from rls-19.1.0.5986094 no script: the item lists the role effects, each with its role condition (B34), same stats; +15% mana gained, 3 regen. VOD3 Lux (champions/Lux.md E1-E2): AD 38 with Shojin, regen 6.9/s and attacks +13.8, i.e. every source x1.15. |
| Archangel's Staff | `DA_ArchangelsStaff` | AbilityPower, ManaPerSecond | `GA_ArchangelsStaff_RampingStats` | implemented (script read) | +20 AP every 5 s from combat start (I4, predicted; no VOD yet). |
| Bloodthirster | `DA_Bloodthirster` | AbilityPower, AttackDamage, MagicResist, Omnivamp | `GA_Bloodthirster` | implemented (stats) | 2026-11-17: the 60%-health shield and omnivamp never trigger against dummies (I8). |
| Blue Buff | `DA_BlueBuff` | AbilityPower, AttackDamage, ManaPerSecond | `GA_BlueBuff` | confirmed (VOD) | [worksheet](../items/BlueBuff.md): +10 mana at combat start, 6 regen; VOD 2026-11-17. |
| Bramble Vest | `DA_BrambleVest` | Armor, HealthMax | `GA_BrambleVest` | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). |
| Crownguard | `DA_Crownguard` | AbilityPower, Armor, HealthMax, IncomingHealMultiplier, IncomingShieldMultiplier | `GA_Crownguard` | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). |
| Deathblade | `DA_Deathblade` | AttackDamage | none | **confirmed** (VOD3) | 2026-11-17: 55% AD, every bonus AD ×1.15 (Channel1 MultiplyAdditive with base-cancelling AddFinals; ×1.30 with two), ledger I5. VOD3 panel: 63%, 103% with IE, 189% with IE + 2. No script. |
| Dragon's Claw | `DA_DragonsClaw` | HealthMax, MagicResist | none | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). `GE_DragonsClaw_HPRegen` (period 2 s); defensive. |
| Edge of Night | `DA_EdgeOfNight` | AbilityPower, Armor, AttackDamage, AttackSpeed | `GA_EdgeOfNight` | implemented (stats) | 2026-11-17: the 40%-health effect never triggers against dummies (I8). |
| Evenshroud | `DA_Evenshroud` | HealthMax, MagicResist | none | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). `GE_Evenshroud_ApplyGA` grants an ability though the item has none listed. |
| Gargoyle Stoneplate | `DA_GargoyleStoneplate` | Armor, HealthMax, MagicResist | none | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). `GE_GargoyleStoneplate_TargetedBuff` is conditional (+10 armor/MR per targeting enemy); defensive. |
| Giant Slayer | `DA_GiantSlayer` | AbilityPower, AttackDamage, AttackSpeed, OutgoingDamageMultiplier | `GA_GiantSlayer` | implemented (script read) | 2026-11-17: two entries: (vs Tank) adds GE_GiantSlayer_ConditionalAmp (+15%) to every hit, (vs non-Tank) stats only (I8). |
| Guinsoo's Rageblade | `DA_GuinsoosRageblade` | AbilityPower, AttackSpeed | `GA_GuinsoosRageblade` | confirmed (VOD) | [worksheet](../items/GuinsoosRageblade.md): stacks on the 1 s timer from combat start, +7% base AS each (I4); VOD 2026-11-17. |
| Hand Of Justice | `DA_HandOfJustice` | CritChance, ManaPerSecond | `GA_HandOfJustice` | implemented (script read) | 2026-11-17: the above-50%-health effect (36% AD, 36% AP) holds all fight (I8). |
| Hextech Gunblade | `DA_HextechGunblade` | AbilityPower, AttackDamage, ManaPerSecond, Omnivamp | `GA_HextechGunblade` | implemented (stats) | 2026-11-17: the ally heal does nothing against dummies (I8). |
| Infinity Edge | `DA_InfinityEdge` | AttackDamage, CritChance | none | implemented (stats) | 2026-11-17: stats + Precision (I1, I2); no script. |
| Ionic Spark | `DA_IonicSpark` | AbilityPower, HealthMax, MagicResist | none | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). `GE_IonicSpark_ApplyGA` grants an ability though the item has none listed. |
| Jeweled Gauntlet | `DA_JeweledGauntlet` | AbilityPower, CritChance | none | implemented (stats) | 2026-11-17: stats + Precision (I1, I2); no script. |
| Kraken's Fury | `DA_KrakensFury` | AttackDamage, AttackSpeed, MagicResist | `GA_KrakensFury` | implemented (script read) | 2026-11-17: +3.5% AD per Combat.Event.LaunchAttack (simulated attacks count, G11) up to 15, then +15% AS (Bonus_AS). Predicted. |
| Last Whisper | `DA_LastWhisper` | AttackDamage, AttackSpeed, CritChance | `GA_LastWhisper` | implemented (script read) | 2026-11-17: armor x0.7 on the damaged unit after each hit, 3 s (I7). Predicted. |
| Morellonomicon | `DA_Morellonomicon` | AbilityPower, HealthMax, ManaPerSecond | `GA_Morellonomicon` | implemented (stats) | Burn not simulated (owner, 2026-11-18, as set18): listed as "Morellonomicon (no burn)", stats only (I7). |
| Nashor's Tooth | `DA_NashorsTooth` | AbilityPower, AttackSpeed, CritChance, HealthMax, ManaPerAttack | `GA_NashorsTooth` | implemented (script read) | 2026-11-17: ManaPerAttack 2 with the role mana (I3); +2 mana per attack crit (I6). Predicted. |
| Protector's Vow | `DA_ProtectorsVow` | Armor, MagicResist, ManaPerSecond | `GA_ProtectorsVow` | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). |
| Quicksilver | `DA_Quicksilver` | AttackSpeed, CritChance, MagicResist | `GA_Quicksilver` | confirmed (VOD) | 2026-11-17: +3% base AS (GE_Quicksilver_StacksToAttackSpeed, x1.03) at 1, 2, 3, ... s (WaitOnTimePassedInPhase 1 s, then RepeatAction(1 s, 99) acting at once); the 18 s is only the Unstoppable. VOD4 (19-0-51-650) Senna 1★ with Guinsoo's, round 1-4, combat start f41837: AS 0.94, then 1.01, 1.09, 1.16, 1.24, 1.31, 1.39, 1.46, 1.54, 1.61 every 60 frames = 0.75 x (1.25 + 0.1k). VOD2 (16-35-16-966, 60 fps) Senna with Quicksilver and Guinsoo's, round 1-10: from 1.09 at 435.77 s (f26146) one step every 60 frames to 3.11 at 462.77 s (f27766), 27 steps averaging +0.0748 = 0.75 x (0.07 + 0.03): Quicksilver keeps stacking past 9 stacks and past 18 s. Its effect's StackLimitCount 9 (snapshot `stacking.limit`) does nothing: the effect has no StackingType, and a limit without one is not applied (a cap at 9 would have ended near 2.71). |
| Rabadon's Deathcap | `DA_RabadonsDeathcap` | AbilityPower | none | implemented (stats) | 2026-11-17: 55% AP, every bonus AP ×1.15: the same effect structure as Deathblade (I5), which VOD3 confirms; not seen itself. No script. |
| Red Buff | `DA_RedBuff` | AttackSpeed, OutgoingDamageMultiplier | `GA_RedBuff` | implemented (stats) | Burn not simulated (owner, 2026-11-18, as set18): listed as "Red Buff (no burn)", stats only (I7). |
| Spear of Shojin | `DA_SpearOfShojin` | AbilityPower, AttackDamage, ManaPerAttack, ManaPerSecond | none | confirmed (VOD) | 2026-11-17: stats; 5 mana per attack paid with the role mana (I3). No script. VOD3 Lux (champions/Lux.md E2): attacks +13.8 = (7 + 5) x 1.15 with Adaptive Helm. |
| Spirit Visage | `DA_SpiritVisage` | HealthMax, IncomingDamageMultiplier, ManaPerSecond | `GA_SpiritVisage` | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). |
| Steadfast Heart | `DA_SteadfastHeart` | Armor, CritChance, HealthMax, IncomingDamageMultiplier | none | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). HealthMax and IncomingDamageMultiplier magnitudes computed in game; defensive. |
| Sterak's Gage | `DA_SteraksGage` | AttackDamage, HealthMax | `GA_SteraksGage` | implemented (stats) | 2026-11-17: the 40%-health shield never triggers against dummies (I8). |
| Striker's Flail | `DA_StrikersFlail` | AttackSpeed, CritChance, HealthMax, OutgoingDamageMultiplier | `GA_StrikersFlail` | implemented (script read) | 2026-11-17: +5% damage amp per crit for 5 s, 4 instances (I6). Predicted. |
| Sunfire Cape | `DA_SunfireCape` | Armor, HealthMax | `GA_SunfireCape` | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). |
| Tactician's Cape | `DA_TacticiansCape` | MaxTeamSizeBonus | `GA_TacticiansCape` | implemented (stats) | Listed with the emblems (below): team size does nothing here, but U.R.F. counts it twice (A6). |
| Tacticians Crown | `DA_TacticiansCrown` | MaxTeamSizeBonus | `GA_TacticiansCrown` | implemented (stats) | Listed with the emblems (below): team size does nothing here, but U.R.F. counts it twice (A6). |
| Tacticians Shield | `DA_TacticiansShield` | MaxTeamSizeBonus | `GA_TacticiansShield` | implemented (stats) | Listed with the emblems (below): team size does nothing here, but U.R.F. counts it twice (A6). |
| Thief's Gloves | `DA_ThiefsGloves` | CritChance, HealthMax | `GA_ThiefsGloves` | out of scope | Random items each round: pick the items themselves instead. |
| Titan's Resolve | `DA_TitansResolve` | Armor, AttackSpeed | `GA_TitansResolve` | confirmed (VOD) | 2026-11-17: one stack (+2% AD and AP, GE_TitansResolve_StackingStats) per Combat.Event.LaunchAttack, up to 25; simulated attacks count (G11); damage taken also stacks (nothing against dummies). Engine event `LAUNCH` (attack release, `Champion.simulateLaunch`; events.py). VOD4 (19-0-51-650) Ezreal 1★ with IE and Guinsoo's, round 2-2 (`tools/vod_text_changes.py --field ap`): AP 12, 14, 16 on the release frames f75988, 76052, 76114; +4 at the cast f76174 (release + simulated attack) and +2 at f76216 (stage 2); 22-28 on releases; +4 at f76447, +2 at 76489 (2nd cast). |
| Void Staff | `DA_VoidStaff` | AbilityPower, AttackSpeed, ManaPerSecond | `GA_VoidStaff` | implemented (script read) | 2026-11-17: MR x0.7 on the damaged unit after each hit, 5 s (I7). Predicted. |
| Warmog's Armor | `DA_WarmogsArmor` | HealthMax | none | out of scope (tank item) | Not in the DPS item table (owner, 2026-11-17; I8). Stats only (HP), no damage effect: added when an HP-scaling champion needs it. |

## Radiants

Every offensive craftable has its Radiant in the Radiant table (`set19items.radiants`, ledger I9): the same class and
script, with the Radiant's key (the base item's `upgrade`), stats effect, rows and script effects. Status follows the
base item's; nothing is VOD-checked yet.

## Artifacts

The Artifact table (`set19items.artifacts`, ledger I10). Nothing is VOD-checked yet.

| Item | Status | Notes |
|---|---|---|
| Infinity Force | implemented (stats) | No script. |
| Silvermere Dawn | implemented (stats) | AS locked at 0.5 (Channel2 Override, I10); the stun does nothing to dummies. |
| Rapid Firecannon | implemented (stats) | Damage amp x1.05; its +1 range doesn't change flights (owner); +range per kill never happens. |
| Fishbones | implemented (stats) | Its +2 range doesn't change flights; random targets change nothing among identical dummies. |
| Gold Collector | implemented (stats) | The execute needs a target below 12% health: dummies never lose health (G9). |
| Luden's Tempest | implemented (stats) | Overkill damage needs a kill (G9). |
| Horizon Focus | implemented (stats) | Needs a stun: no implemented champion stuns. |
| Seeker's Armguard | implemented (stats) | Takedown stats need kills (G9). |
| Gambler's Blade | implemented (stats) | +30% AS from 30 gold in the bank (owner, I10). |
| Cappa Juice | implemented (stats) | +1% AD/AP per Hat = the page's Total takedowns (owner, I10). |
| Hullcrusher | implemented (script read) | 400 HP, 10% AD/AP: no adjacent ally assumed (owner, I10). |
| Statikk Shiv | implemented (script read) | Every 3rd release: 6 x (15 + 35% bonus AP) magic split over min(enemies, 6) bolts; not boosted (I10). |
| Lich Bane | implemented (script read) | First hit after each cast: ProcDamage by stage, magic; not boosted (I10). |
| Wit's End | implemented (script read) | Every hit: OnHitDamage by stage, magic; not boosted; the heal does nothing here (I10). |
| Titanic Hydra | implemented (script read) | Every hit: 2% max HP + 4% AD physical to the target and one enemy next to it (owner: always one, G22); not boosted (I10). |
| Hellfire Hatchet | implemented (script read) | Every hit: 3% max HP physical; AS per missing health is 0 here (I10). |
| Flickerblades | implemented (script read) | +4% AS per release, +2% AD/AP every 3rd (I10). |
| Dawncore | implemented (script read) | Max mana -10, then -5% per cast (min 15), after each cast's cost (I10). |
| Manazane | implemented (script read) | After the first cast, 110 mana in 2.2 steps every 0.1 s, paused while mana is locked (I10). |
| Talisman of Ascension | implemented (script read) | At 22 s: +120% damage amp, +12 mana regen (I10). |
| Blighting Jewel | not listed | Flat MR shred needs a modelling decision (owner); see docs/OPEN-QUESTIONS.md. |
| Death's Defiance, Mittens, Mogul's Mail, The Indomitable, Lightshield Crest, Zhonya's Paradox, Void Gauntlet, Aegis of Dawn, Aegis of Dusk, Forbidden Idol | out of scope | Defensive or support: no damage of their own against dummies. |
| Eternal Pact | out of scope | Depends on an ally's behaviour (owner). |

## Emblems and Spatula items

The Emblem table (`set19items.emblems`, `items/emblems.py`): the Spatula items U.R.F. counts (A6) and the emblems whose
effect is plain stats. An emblem applies its stats effect GE_<Trait>_Emblem; its AttackSpeed is 1 x AttackSpeedCalc1,
checked to be 1 + EmblemAS. The trait it adds is the buff bar's level (picking the emblem offers the trait). Nothing
is VOD-checked yet.

| Item | Status | Notes |
|---|---|---|
| Spatula, Frying Pan | implemented (stats) | No stats; U.R.F. counts each once. |
| Tactician's Crown, Cape, Shield | implemented (stats) | Team size only; U.R.F. counts each twice. |
| K/DA, Ill Beats, Ionic Spark, Rock, Beach Pop, Pentakill, Jazz, True Damage, Classical, Hyperpop | implemented (stats) | Stats effect only. K/DA's GE_KDA19_StarLevelContribution is the trait's side. Rock's trait isn't simulated. |
| Arcanist, Bodyguard, Choreographer, Frontman, Heartsteel, Hitmaker, Juggernaut, Manager, Prodigy, Renegade, Slayer, Swiftstriker | not listed | More than stats: execute, resist conversion, back-row AS, on-hit scripts, trait tags, amp per health, a max-mana row, granted abilities, empowered crits. Added when their mechanic is written. |

The rest are added when needed.
