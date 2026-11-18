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
| Burn timing | 1% of the target's max HP as true damage every second from 1 s after the first hit, one burn per target renewed by every hit | burn numbers on a target of known HP, from the first hit | I7 |
| Last Whisper / Void Staff | x0.7 armor / MR from the hit after the first, for 3 s / 5 s after the latest hit | a holder's damage numbers on one target: 1st hit vs 2nd | I7 |
| Kraken's Fury stacks | +3.5% AD per attack release (simulated attacks count), 15 max, then +15% AS | panel AD % of a holder over its first attacks (and a cast) | docs/ITEMS.md |
| Striker's Flail stacking | separate 5 s instances of +5% damage amp, 4 at most | the damage-amp line of a crit carrier's panel | I6 |
| Titanic Hydra's splash | the target and one more dummy (1 hex apart) | a Hydra holder's hit on a target with two neighbours | I10 |
| Lich Bane on a ranged holder | procs on the first hit after the release that follows the cast | a ranged Lich Bane holder's damage numbers after a cast | I10 |
| Dawncore's per-cast cut | 5% of max mana after each cast's cost (the next cast is cheaper) | the max mana a Dawncore holder shows after each cast | I10 |
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
