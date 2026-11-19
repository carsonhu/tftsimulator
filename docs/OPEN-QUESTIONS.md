# Open questions

Every question the simulator still has an assumption for, grouped by the evidence that would settle it, so that one
recording can answer several. The full rule and its history stay in the ledger (`docs/ASSUMPTIONS.md`) or the
champion's worksheet. This page is the index of what's still open.

**How to use it:** when a clip answers a row, log the measurement in the worksheet or ledger entry it links to (how:
`docs/evidence-method.md`), update that entry's status, and delete the row here. When a new assumption is made, add a
row here at the same time as its ledger entry.

Recording tips that make a clip answer more:
- 60 fps, inspection panel open on the unit from before combat starts (planning phase) to well after its first cast.
- A Blue Buff holder somewhere on the board marks combat start to the frame (its +10 mana, items/BlueBuff.md).
- Note the patch / time, so the clip can be matched to a build.

## Clips wanted

### 1. A K/DA (7)+ board (owner will record later)

A K/DA member with its panel open from the planning phase through ~17 s of combat. K/DA (10) as well would also
check the ×1.25 boost.

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| When does the combat-start song land? | at combat start (tick 0). The script's `TriggerBonus` is 0.95 s into a chrono whose start relative to combat start isn't decoded. | the frame the max mana drops and the AS jumps, relative to combat start | B14 |
| VILLAIN attack speed: +60% decaying to 0 over 8 s | linear, -1/32 of the bonus every 0.25 s (`bChangeOverTimeForPeriodic`) | the panel AS text every 0.25 s for 8 s | B14 |
| Second song after 8 s | the AS bonus is given again at 8.0 s; the mana reduction doesn't stack again (stack limit 1) | AS jump at ~8 s; max mana unchanged | B14 |
| (10) boost | ×1.25: +75% AS, max mana × 0.875 (30 → 26.25: how does the panel show a fractional max?) | panel AS and max mana at K/DA (10) | B14 |

### 2. Any 60 fps fight with a Blue Buff holder (exact combat start)

Best: the Blue Buff holder's own panel, a ranged caster that casts at least twice.

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Do fresh attacks start one tick later than the engine starts them? | no; every precise sighting says +1 tick (4 Varus, 2 Neeko, 1 Ziggs, 1 Ezreal at combat start), Draven by eye at 30 fps said the opposite | first attack's mana step after combat start; first attack after a cast lock | T10 |
| When does the first mana-regen step come? | at combat start (tick 0); two sightings say ~4 ticks after | the first +regen step of a caster after combat start | G17, T7 |
| Must a unit attack between casts? | yes (set18's rule) | a unit whose regen + items refill the bar during its own cast lock | G18, T8 |

### 3. Kai'Sa again (or any unit gaining attack speed every cast)

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Why do releases drift late as Kai'Sa's AS climbs? | the attack after a cast keeps the period it was timed with; the engine runs up to +4 ticks late by the 20th attack (exact for 11) | another long Kai'Sa fight (panel mana text), ideally without crowd control | T13, champions/Kaisa.md E2 |
| Missile damage | 36/54/85 × AD + 6/9/15 × AP each; physical; 3 every 3 attacks | damage numbers on a target of known armor | champions/Kaisa.md Q13 |
| First attack at combat start | Attack1LowAS: 0.3255 s → tick 10 | first +10 after combat start (needs a Blue Buff elsewhere) | B13, Kai'Sa Q3 |

### 4. Yunara again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Orb damage and timing | each orb Calc1 (13/20/30 x AD + 3/5/7 x AP), the i-th orb spawning at the orb chrono's i-th time scaled to 0.5 / AS, flying 1850 units/s | damage numbers after her 2nd and 3rd casts | champions/Yunara.md D1 |
| First attack at combat start | a stationary ranged unit releases one windup in (8 ticks); VOD2 she walked first (21.5 ticks) | a fight where she starts in range | G3, Yunara Q3 |

### 5. Ziggs with attack speed

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Does his cast speed up with attack speed, capped at 2x? | the cast chrono plays at FClamp(AS / base AS, 1, 2): cast lock 25 ticks at base AS, 12 at 2x | a Ziggs with attack-speed items or Swiftstriker stacks: cast to next release | G7, champions/Ziggs.md D1 |
| First attack at combat start | a stationary ranged unit releases one windup in (18 ticks at base AS); VOD2's fight was minions walking in | a fight with a combat-start marker (Blue Buff) | G3, Ziggs Q3 |

### 6. Senna again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Does a crit attack release later (0.6364 s vs 0.531 s)? | the windup is weighted by crit chance: 17 ticks at 25% crit (16 normal, 20 crit) | a Senna fight with few items and no mana regen items, damage numbers (crits) next to the mana steps | B17 |
| Blast and detonation damage | 140 x AD + 25 x AP, then 1.5x that, +8% damage amp per detonation (stacking) | damage numbers on a target of known armor | champions/Senna.md D1 |
| First attack at combat start | one averaged windup in (17 ticks at 25% crit) | a fight with a combat-start marker | G3, Senna Q3 |

### 7. Ezreal again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Cast to the next attack | the bar fills at a release, the cast is the next tick, cast lock 36 ticks, then an 11-tick windup: 48 ticks from that release; VOD4 showed 46 and 44 | another Ezreal fight, ideally against a stationary target (no retargeting) | T4, T10, champions/Ezreal.md E2 |
| Detonation damage | 190 x AD + 30 x AP on the target, 0.33x that within 1 hex | damage numbers without Titan's Resolve, on a target of known armor | champions/Ezreal.md D1 |
| Encore's second missile | x RecastEffectiveness (25/50%) at 0.319 s into stage 2 | an Ezreal with Encore (2) | champions/Ezreal.md D1 |
| Heartsteel Bias upgrade | x1.25 on both hits; casts 3, 6, ... also hit the enemies 2 hexes from the target (0.33x) | an Ezreal chosen as Bias at Heartsteel (3)+: damage numbers of his 1st-3rd casts | B21, champions/Ezreal.md D1 |

### 7b. Lux again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Beam damage and its moment | 330/500/800 x AP on the target and 170/255/425 x AP on the enemy nearest Lux, both 32 ticks after the cast starts (DamageAndBeam 1.0416 s) | damage numbers of a Lux cast on targets of known MR | champions/Lux.md D1 |
| Which enemy the secondary beam hits | the enemy nearest Lux other than her target (not the one nearest the target) | a Lux cast with an enemy beside her and one beside her target | champions/Lux.md D1 |
| Prodigy | members +2/3/6/7 + 1 mana regen, everyone else +1 | the regen shown in the panel with Prodigy (2)+ active | B24 |

### 7c. Gnar again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Rock damage | 120/180/270 x AD physical, crits only with Precision, on-hit effects apply | damage numbers of his 3rd attacks on a target of known armor | champions/Gnar.md D1 |

### 7d. Malzahar again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Beam and burst damage | 9 beam ticks of 380/570/960 x AP / 9 on the target; 4 bursts of 40/60/110 x AP within 1 hex, each after a 30% shred | damage numbers of a cast on targets of known MR | champions/Malzahar.md D1 |

### 7e. Samira again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Cast to the next attack | cast lock 41 ticks (the build), then a fresh 9-tick windup: 50 ticks after the filling attack; VOD3 showed 54.5 (n = 1) | more Samira casts with the mana text | champions/Samira.md E3 |
| Does every barrage count as an attack launch? | yes, once per cast (the DoOnce resets each cast) | a Samira with Titan's Resolve: stacks per cast | champions/Samira.md D1 |
| Bullet damage | 10 x (4/6/9 x AP + 35/53/80 x AD), crit only with Precision | damage numbers of a barrage on a target of known armor | champions/Samira.md D1 |
| Classical's growing amp | +1% per 6 s an enemy is Captivated, in 0.25 s steps from the Captivate | a Classical (2)+ carrier's damage-amp panel over a fight | B28 |

### 7f. Karthus again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Requiem damage | 440/660/930 x AP magic, 34 ticks after the cast starts | damage numbers of a cast on a target of known MR | champions/Karthus.md D1 |

### 7g. Olaf (Axe Crescendo) again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Axe damage | 150/225/360 x AD + 15/20/30 x AP physical, no on-hit | damage numbers of an axe on a target of known armor | champions/Olaf_HeroAugment.md D1 |
| Do on-launch items hear the empowered throws? | yes (Combat.Event.LaunchAttack.Custom.1 is a LaunchAttack) | Olaf (Axe Crescendo) with Titan's Resolve: stacks per throw | champions/Olaf_HeroAugment.md D1 |

### 7h. Ashe again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| The second empowered phase | 6 flurries at the attack period (AS 1.53-1.60: ~19 ticks apart), lock lifted 109 ticks after the filling attack | VOD5 showed 122.5 (the first phase matched to 1.5 ticks); a clip of a longer Ashe fight on a target that stays alive | champions/Ashe.md E2 |
| Arrow damage | 3 x 33/50/75 x AD per flurry, on-hit at 0.6 | damage numbers of a flurry on a target of known armor | champions/Ashe.md D1, I11 |
| Play-rate threshold below 1 (G20) | applied (owner): Draven's release shrinks above AS 0.85, Malzahar's above 1.06, Ziggs's above 1.43 | a Draven or Malzahar attack at AS above ~1.2 (Guinsoo's or Quicksilver late in a fight) | G20 |

### 7i. Viego again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Sword travel | 0.25 s after FireSwords (fixed-time projectile, G21) | the frame of the swords' damage numbers | G21 |

### 7j. Kayle again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| The first attack after the finale | a fresh attack at the finale's Unlock: 12 ticks to its release | VOD5: 19.5 ticks after her mana showed again (n = 1; KeepFacing plays 1.1165 s at BigHit) | champions/Kayle.md E2 |
| The buff's length | 4 s + 0.75 x 0.5 s / S | the frames of the AS change in and out (VOD5's panel moved 10 ticks after the Buff event) | champions/Kayle.md D1 |
| Her attack projectile's speed in the build | 2250 typed from the client asset | (tool) the snapshot should read projectiles that a champion's own attack script names | champions/Kayle.md D1 |

### 7k. Lucian again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Dash length | MinDashDistance (1 hex, 4 ticks at 2000 units/s): the nearest of the equally safe hexes on the dummy layout | VOD1's casts lasted ~4 ticks longer (lock 37-39 after the fill, engine 33) | champions/Lucian.md E2 |

### 7l. Renata Glasc again

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Toxin's first tick | on application (Unreal's default) | the frame of the first Toxin number after the chain lands | champions/RenataGlasc.md D1 |

### 7m. Zoe and Beach Pop

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Zoe's cast (locks, the ball's flight) | the build: 55 / 56 ticks; the ball 41 + 14 ticks after the cast | any Zoe cast with the mana text (VOD5's fights ended at 86/90) | champions/Zoe.md D1 |
| Beach Pop's mana timer | +5/8/8 at 3, 6, 9 ... s from combat start | an empowered Beach Pop unit's mana text | B32 |

### 7o. Bard (VOD1 has one)

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| When the wave reaches the target | it starts half a hex behind Bard (back row): 29 ticks after FireMeeps (0.4381 s) at 4 hexes, then 7 ticks per hex | the frame of the wave's damage numbers after the cast | champions/Bard.md Q16 |
| The wave's two halves | 0.1 s apart, the first on application | two numbers per enemy, 3 frames apart | champions/Bard.md D1 |

### 7p. Syndra and Briar (VOD5 has both)

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Syndra's volleyball and bounce | the ball 40 + 11 ticks after the cast (4 hexes), the bounce 7 ticks later (2 hexes); 15 ticks bouncing in place | the frames of her two damage numbers (VOD5 11:35-12:30) | champions/Syndra.md Q16 |
| Briar's frenzy windup | G2: 15 ticks per slash though the period is 12.5 at x3 AS (bUseRateScalingThreshold, no threshold) | the slashes' damage numbers after a cast (VOD5 8:20) | champions/Briar.md Q5, G20 |
| Briar's mana after the frenzy | locked until the tick after the 3rd slash | her mana bar during and after the slashes | champions/Briar.md Q9 |

### 7q. Xayah and Gu Feng (VOD4 has Xayah)

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| When her feathers land | 1.37-1.77 s into the cast at 4 hexes (waits 0.88 / 0.4 s, 3200 units/s from the fan behind her) | a cast on a target 4 hexes away: the frames of the damage numbers | champions/Xayah.md Q16 |
| Her feathers' waits in the build | 0.88 / 0.4 s typed from the client asset | (tool) the snapshot should read a chrono projectile module's Delay | champions/Xayah.md D1 |

### 7r. Katarina (VOD6 has her at 1-2)

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Her cast with the target in range (no dash) | spin at once, eviscerate at 0.835 s, the next attack 40 ticks + windup after the cast | a cast on an enemy already next to her: the eviscerate's damage number and her next attack | champions/Katarina.md Q7, Q9 |

### 7s. Kayn (VOD6 has him at 1-3 and 1-4)

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| (owner) When the Bias Kayn becomes the Shadow Assassin | from combat start (dummies never hit back; the game: at 70% Health, VOD6 ~4.8 s in) | your call: from the start, never, or a time | champions/Kayn.md Q17 |
| Does he dash before each swipe against stationary enemies? | he stands still (the script dashes when another hex within 2 of the target hits at least as many, unless he is on it) | a cast on stationary enemies: does he move, and the next attack's timing | champions/Kayn.md Q16 |

### 7t. Qiyana (VOD6 has her at 1-5)

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| (owner) Her ring colour | averaged: each cast deals +20% x 1/3 (Red) and refunds 10 x 1/3 mana (Blue), the ring's long-run shares | your call: averaged, or a fixed colour per fight | champions/Qiyana.md Q14 |
| Her Collab trait | not in build 5986094 (VOD6's client 5986652 shows it) | (tool) export 5986652 | champions/Qiyana.md |

### 7n. Augments

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Timed augments' first step | Focused Fire at 5 s, Baron's Lair at 8 s, Submit to the Pit at 1 s, then each interval | a holder's AD % on the panel | A1 |
| Ascension, Espresso | on the tick at 12 s | a holder's AS (Espresso) on the panel | A2 |
| Soul Awakening's timing | set18's: first stack 0.8 s in | a Set 19 holder's AD % steps | A4 |
| Stakeholder Management | not implemented | (owner) waits for a Manager champion | |

### 8. Spell projectiles and damage numbers

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Do arcing missiles take longer than straight ones? | no: straight-line time (Neeko's 400-height arc 13 ticks, not ~20) | Neeko's damage numbers vs her cast | G4, Neeko Q6 |
| Draven's record flight | 14 ticks at 4 hexes; VOD1 showed 16 (5 hexes would give 16) | a Draven cast at a target at a known distance | P12, Draven E4 |
| Trickshot ricochet distance between dummies | the next dummy is 1 hex away (timing only; damage unchanged) | a ricochet's travel between two adjacent enemies | B12 |

### 9. Items

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Hitmaker's AD (a trait, checked the same way) | every member +12% AD, a Big Shot +20/35% more (32/47% in all) | panel AD % of a Big Shot and of another Hitmaker at Hitmaker (2) | B18 |
| Ionic Spark letters and gifts (a trait) | +7% AS per letter at 4, 8, 12 s; the 1st gift (25% AD/AP) at 0 s; no flight time | the panel AS / AD of an Ionic Spark member over the first ~13 s at Ionic Spark (5) | B22 |
| Heartsteel's team bonuses (a trait, read the same way) | each fielded member gives every ally Kayn +7% AD, Alune +7% AP, Aphelios +6% AS, Ezreal +10% crit; at (7) members get 2.5x (Ezreal's crit by the tooltip: the files give members only +10% more) | panel stats of a non-member and of a member with Kayn/Alune/Aphelios fielded, and at Heartsteel (7) | B21 |
| Illbeats (4) (a trait, read the same way) | the mix's values x1.5 (StatMult at level 3) | the mixer readouts at Illbeats (4) | B20 |
| Rabadon's Deathcap | every bonus AP × 1.15 (same structure as Deathblade, which VOD3 confirmed); panel 63% alone, 104% with Jeweled Gauntlet | panel AP % with a Rabadon's | I5, docs/ITEMS.md |
| Archangel's Staff stacks | first stack 5 s after combat start, then every 5 s | panel AP over the first ~15 s | I4 |
| Last Whisper / Void Staff | x0.7 armor / MR from the hit after the first, for 3 s / 5 s after the latest hit | a holder's damage numbers on one target: 1st hit vs 2nd | I7 |
| Kraken's Fury stacks | +3.5% AD per attack release (simulated attacks count), 15 max, then +15% AS | panel AD % of a holder over its first attacks (and a cast) | docs/ITEMS.md |
| Striker's Flail stacking | separate 5 s instances of +5% damage amp, 4 at most | the damage-amp line of a crit carrier's panel | I6 |
| Titanic Hydra's splash | the target and every enemy next to it (HexRange 1 taken to include the target; the page's layout, default one neighbour) | a Hydra holder's hit on a target with two neighbours | I10 |
| Lich Bane on a ranged holder | procs on the first hit after the release that follows the cast | a ranged Lich Bane holder's damage numbers after a cast | I10 |
| Dawncore's per-cast cut | 5% of max mana after each cast's cost (the next cast is cheaper) | the max mana a Dawncore holder shows after each cast | I10 |
| Where a timed effect ends (low priority: note it if seen) | a 3 s sunder applied at tick a covers ticks a to a + 90 and is gone at a + 91 (whole ticks, every unit) | a hit that lands about 3 s after a Last Whisper holder's previous hit on the same target, sundered or not | T14 |
| Spear of Shojin's mana | its 5 mana per attack is paid with the role's attack mana, at the same moment | a Shojin holder's mana steps (+12 for a caster) | I3 |

## No clip needed

| Question | Status | Where |
|---|---|---|
| Draven's vortex: the decoded damage effect has no tick-rate factor, yet each 0.5 s hit is half the per-second value (owner's ruling). Where does the game halve it? | implemented as the owner ruled; the decode is incomplete somewhere (calc component or attribute) | champions/Draven.md D1 |
| Trickshot ricochets' on-hit effects (at RichochetDamage^k) | not modelled; no listed item has an on-hit effect yet | B12 |
| True Damage's Prismatic tier, Heartsteel's Prismatic car, Ionic Spark's (10) fan waves, the other Heartsteel members' Bias upgrades (Kayn, Alune, Aphelios: not implemented champions) | not implemented | - |
| True Damage's B-Side | out of scope: it gives no combat power (owner, 2026-11-17) | B19 |
| Rapid Firecannon's damage amp | additive with other amps, 1 + others + 0.05 (owner default, 2026-11-17: damage amp is additive). Its effect is the only amp in the build written MultiplyAdditive (37 others are +), so the stock formula would give (1 + others) x 1.05. Only differs when another amp is active: about 0.6% with Giant Slayer vs a Tank, 2.7% with Talisman of Ascension's +120% | a Rapid Firecannon holder's damage numbers with another amp, e.g. with Talisman before and after its 22 s buff (the owner will look for one) | I1 |
| Blighting Jewel | not in the table: its flat -3 MR per magic hit stacks for the whole combat on dummies that never die, which overstates it (owner, 2026-11-17). Needs a decision on how to model flat MR shred (a cap, a target that changes, an average) | docs/ITEMS.md |
