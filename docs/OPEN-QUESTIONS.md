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
| Do fresh attacks start one tick later than the engine starts them? | no; every precise sighting says +1 tick (4 Varus, 2 Neeko), Draven by eye at 30 fps said the opposite | first attack's mana step after combat start; first attack after a cast lock | T10 |
| When does the first mana-regen step come? | at combat start (tick 0); two sightings say ~4 ticks after | the first +regen step of a caster after combat start | G17, T7 |
| Must a unit attack between casts? | yes (set18's rule) | a unit whose regen + items refill the bar during its own cast lock | G18, T8 |

### 3. Kai'Sa again (or any unit gaining attack speed every cast)

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Why do releases drift late as Kai'Sa's AS climbs? | the attack after a cast keeps the period it was timed with; the engine runs up to +4 ticks late by the 20th attack (exact for 11) | another long Kai'Sa fight (panel mana text), ideally without crowd control | T13, champions/Kaisa.md E2 |
| Missile damage | 36/54/85 × AD + 6/9/15 × AP each; physical; 3 every 3 attacks | damage numbers on a target of known armor | champions/Kaisa.md Q13 |
| First attack at combat start | Attack1LowAS: 0.3255 s → tick 10 | first +10 after combat start (needs a Blue Buff elsewhere) | B13, Kai'Sa Q3 |

### 4. Spell projectiles and damage numbers

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Do arcing missiles take longer than straight ones? | no: straight-line time (Neeko's 400-height arc 13 ticks, not ~20) | Neeko's damage numbers vs her cast | G4, Neeko Q6 |
| Draven's record flight | 14 ticks at 4 hexes; VOD1 showed 16 (5 hexes would give 16) | a Draven cast at a target at a known distance | P12, Draven E4 |
| Trickshot ricochet distance between dummies | the next dummy is 1 hex away (timing only; damage unchanged) | a ricochet's travel between two adjacent enemies | B12 |

### 5. Items

| Question | What the simulator assumes now | What the clip shows | Ledger |
|---|---|---|---|
| Rabadon's Deathcap | every bonus AP × 1.15 (same structure as Deathblade, which VOD3 confirmed); panel 63% alone, 104% with Jeweled Gauntlet | panel AP % with a Rabadon's | I5, docs/ITEMS.md |
| Archangel's Staff stacks | first stack 5 s after combat start, then every 5 s | panel AP over the first ~15 s | I4 |
| Spear of Shojin's mana | its 5 mana per attack is paid with the role's attack mana, at the same moment | a Shojin holder's mana steps (+12 for a caster) | I3 |

## No clip needed

| Question | Status | Where |
|---|---|---|
| Draven's vortex: the decoded damage effect has no tick-rate factor, yet each 0.5 s hit is half the per-second value (owner's ruling). Where does the game halve it? | implemented as the owner ruled; the decode is incomplete somewhere (calc component or attribute) | champions/Draven.md D1 |
| Crit-conditioned attack animations (Senna's crit attack winds up 0.636 s vs 0.531 s; Varus, Jinx, ... have CritAttack / SequentialAttack groups) | not modelled: the single launch time is used. Needed before Senna. | B13, P13 |
| Trickshot ricochets' on-hit effects (at RichochetDamage^k) | not modelled; no listed item has an on-hit effect yet | B12 |
| Illbeats (Draven's second trait) | not implemented | - |
