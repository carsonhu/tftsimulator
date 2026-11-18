# Restructuring the engine

A plan, not yet started (written 2026-11-17). The Set 19 simulator runs on an engine carried over from many earlier
sets (the first commit imported set18 verbatim). That engine was built for numbers typed in by hand; Set 19 reads
the game's own effects from a client build. Most of the friction in Set 19 work comes from translating between the
two. This document says what to change, why, and in what order, so the work can be done in small steps without
losing anything the VODs confirmed.

## What to keep

- **The timing core** ([timing.py](../timing.py), `Champion.update`, ledger T1-T13). It is already tick-based,
  built from the build's chronos, and checked against VODs. Nothing here changes it.
- **Build-driven numbers** (`buildstore`, `BuildChampion`, `BuildItem`, `BuildTrait`, ledger B1-B11, I1-I3). Every
  change below makes this layer *more* direct, not less.
- **The ledger and worksheets** (`docs/ASSUMPTIONS.md`, `docs/OPEN-QUESTIONS.md`, `champions/*.md`). Each change
  below updates the ledger entries it touches.
- **Pure Python with no dependencies**: the engine runs in the browser through Pyodide.

## Before starting: the regression net

The local tests (`test_*.py`, 139 at the time of writing) are the guard for everything below, and the VOD-confirmed
numbers are the part that must never move:

| What | Where it's checked |
|---|---|
| Guinsoo's and Quicksilver's AS steps | `test_items.py` (VOD2, VOD4) |
| Deathblade's panel AD % (63 / 103 / 189%) | `test_items.py` (VOD3) |
| Titan's Resolve stacks per release and per cast | `test_items.py` (VOD4) |
| Illbeats mixer readouts | `test_draven.py` (VOD4) |
| Release and cast ticks: Varus, Neeko, Ziggs, Senna, Ezreal, Kai'Sa, Yunara | `test_<champion>.py` |
| Ziggs's attack and bomb damage, True Damage (3) | `test_ziggs.py`, `test_senna.py` |

**Decided (owner, 2026-11-17):** the tests were gitignored, so they existed only on this PC. They are now committed on
branch `set19`, where the restructuring work continues; `main` still ignores them.

Each step below ends with: all tests pass unchanged (except tests that test the removed mechanism itself), both
browser checks pass (`tools/browser_check/`), and the tables for every champion give the same numbers as before, to
the decimal. `tools/table_dump.py` makes that last check cheap: run it before and after a step, then `--diff` the
two dumps (every slice for every champion at 1 and 2 stars, with each row's DPS, ratios and damage vector, and the
stats panel; about 2.5 minutes).

## The changes, in order

### 1. Delete the set18 leftovers (small, low risk)

**Now:** [app.js](../app.js) still has 36 references to set18 mechanics (Blossom, Greenfather, Blackthorn, Lunar,
Wisps) and [sim_entry.py](../sim_entry.py) 6 more, with comments describing Streamlit pages that no longer exist.
The Blackthorn panel is still in [index.html](../index.html) (always hidden). In [champion.py](../champion.py),
`doDamage` and `multiTargetSpell` carry hooks for set18 items and champions ("pass whether it's spell for holobow",
"Arcana Xerath", `luckyCrit`, the unused `onAttack` comment). The Team Traits panel's shape detection
(`_team_level_matters`, `option_stats`, `sweep_params`) exists mostly for set18 traits.

**Change:** delete what no Set 19 class uses; keep what one does (Ionic Spark and Illbeats use the Options path,
Heartsteel the Flags path).

**Done when:** a grep for those names finds nothing; the page looks the same.

**Done (2026-11-17).** Removed: the Blackthorn panel (HTML, JS, catalog key), the Wisp slice and the Blossom pill
marking, the Greenfather stat icons (`STAT_ICONS`, `statIcon`, `optionIcons`/`option_stats`, `trace_glyph.py`),
`sweep_params` in the Trait sweep, the empty `wisps`, `stat_buffs` and `animas` registries, the "lucky" crit
(`luckyCrit`, `luckyAbility`, `utils.py`) and the unused `onDealSpellDamage` / `PostOnDealSpellDamage` phases;
comments that described set18 traits or the Streamlit pages now describe Set 19 cases. Kept, because a Set 19 class
uses them: `_team_level_matters` (Heartsteel's Team Traits row), the Options path (Illbeats, Ionic Spark), the
champion-specific flag row (Hitmaker's Big Shot). Tests 139 pass, both browser checks pass, and `table_dump.py
--diff` finds no change except the removed Wisp slice (which only ever held the NoItem row).

### 2. Split the big modules; register classes with a decorator (small, low risk)

**Now:** [set19items.py](../set19items.py) is 1,073 lines (stats layer, debuffs, burns, 25 craftables, Radiant
generation, 20 artifacts) and [set19buffs.py](../set19buffs.py) is 546 and growing. Classes become live by being
named in hand-kept lists of strings (`offensive_craftables`, `class_buffs`, `artifacts`), looked up with `getattr`.

**Change:**

```
items/      stats.py (STAT_MAP, item_stats, BuildItem), debuffs.py (sunder, shred, burn),
            craftables.py, radiants.py, artifacts.py
traits/     one module per trait family, BuildTrait in base.py
```

and a decorator (`@register("craftable")`) instead of the lists. [worker.js](../worker.js) `PY_FILES` must list every
new module (the browser loads only what is listed).

**Done when:** the tables are unchanged; adding an item means writing one class in one file.

**Done (2026-11-17).** `items/` (`base.py`, `debuffs.py`, `craftables.py`, `radiants.py`, `artifacts.py`), `traits/`
(`base.py` and one module per trait) and `registry.py` (`@register(kind)`). Two changes from the plan: the stats
layer is `items/base.py`, not `items/stats.py`, so it can't be mistaken for the top-level `stats.py`; and
`set19items.py` / `set19buffs.py` stay as the modules that gather the packages, so every caller and test still names
classes as `set19items.<Class>` / `set19buffs.<Class>`. The import order in `set19buffs.py` keeps the old trait order,
which is also the order traits run in. Code moved verbatim; the only renames are private helpers (`_name` is now
`item_name`). The worker now creates each module's folder, and a test checks that it lists every module. Tests
(140) pass, both browser checks pass, the registries equal the old lists exactly, and `table_dump.py --diff` finds
the tables identical.

### 3. Attributes shaped like the game's (the big one)

**Now:** the game has one rule for every attribute: per evaluation channel, `((base + AddBase) × (1 + Σ
(MultiplyAdditive − 1)) / DivideAdditive × MultiplyCompound) + AddFinal`, with Override and Min/Max (ledger I5).
The engine has a different class per stat in [stats.py](../stats.py), in mixed units:

| Stat | Engine representation |
|---|---|
| AD, AP | percent points in `add`, plus a separate `addMultiplier` for Deathblade / Rabadon's |
| Attack speed | percent points in its own formula, a cap, and an `override` added for Silvermere Dawn |
| Crit, damage amp, omnivamp | fractions |
| Armor / MR shred | `mult` set by statuses |

So every effect needs a hand-written mapping (`STAT_MAP` and the per-trait `addStat(x * 100)` calls). That mapping
is where a 100× unit slip could happen, and where special cases pile up: the check that a Deathblade-style
`MultiplyAdditive` comes with `AddFinal` terms that cancel it on the base; the Channel2 Override exception; a flat
after-multiplier MR reduction (Blighting Jewel) that the engine can't express at all.

**Change:** one `Attribute` type that stores modifiers per channel and op and evaluates the game's formula. Every
champion stat becomes an `Attribute` in game units (AD as a flat number, AP 1.0 = 100, AS in attacks per second,
crit as a fraction). The item layer then applies an effect's modifiers as listed in the build: no unit table, no
cancelling check, no special cases. Traits apply their effects the same way instead of computing `× 100`.

**Risk:** this touches every champion, item and trait. Do it in two passes: first give `Attribute` an adapter that
answers `.stat` and `.addStat()` exactly as today, so nothing else changes; then move callers over one family at a
time (items, then traits, then champions), diffing the tables after each.

**Done when:** `STAT_MAP`, `BONUS_MULTIPLIERS`, `FINAL_OVERRIDES`, `Aspd.override` and `AD.addMultiplier` are gone;
the tables are unchanged.

**Done (2026-11-17)**, in four commits, each diffed: `Attribute` with an adapter (9c367df), items (2c25a2d), traits
(b978f31), champions and the page's inputs, adapter removed (48fd09c). `stats.Attribute` holds (channel, op, value,
key) modifiers and evaluates the game's formula; every champion stat is one, in game units. Items apply build
modifiers with their own op and channel; Stack-scaled item effects and K/DA's decaying AS are one keyed modifier
re-sized as they change. Also removed: the unused set18 statuses, `Champion.addStats` and the per-item stat fields.
Kept on purpose, so no number moves: Rapid Firecannon's amp stays additive (owner default; open in
docs/OPEN-QUESTIONS.md), the role's ManaMax "at least" still clamps the base, the armor/MR floor at 0 is an
explicit bound, and the old `Stat` class remains only for `Attack.multiplier` and the pierce stats (step 4). Tests
that read the old units (AS and AD bonuses in percent points, `armor.mult`, `as_cap`) now read the same numbers
from the attribute, and the two tests of the removed refusals check the formula instead. Tables: identical with
`--rel 1e-9`; summing bonuses as fractions instead of percent points moves raw damage numbers by at most 8.9e-16
relative, never a shown one. A run with every page bonus box set matched step 2's code the same way.

### 4. Timed effects and damage events modelled on the game's

**Effects now:** burn, sunder, shred, Striker's Flail, Titan's stacks, Ionic Spark letters and Swiftstriker stacks
are each "an effect with a duration, a period and a stacking rule", and the build states those rules (`StackLimitCount`,
`StackingType`, `StackDurationRefreshPolicy`, `Period`, `bExecutePeriodicEffectOnApplication`). In the engine each
is either one of 13 hand-written classes in [status.py](../status.py) (timed in float seconds, while everything else
runs on ticks) or a counter inside one item.

**Change:** one tick-based `ActiveEffect` that takes its modifiers, duration, period and stacking rule from the
build's effect record, applied to the champion or a dummy. The snapshot already records most of these fields; add
the rest in `tftDatamine/tools/set_dump.py` (re-snapshot with `--force`).

**Damage events now:** items react through 13 named phases (`preAttack`, `onAttack`, `postAttack`, `onCrit`,
`onDealDamage`, `PostOnDealDamage`, `onLaunch`, ...), each with its own payload: a damage tuple, an is-spell bool,
a target list, or the `lastDamagedOpponent` side channel. Choosing a phase is a judgement call each time (Lich Bane
in `postAttack`, Blighting Jewel in `PostOnDealDamage`, Titanic Hydra in `onAttack`).

**Change:** every damage instance becomes a `DamageEvent` carrying the game's tags (`Damage.Source.Unit/Item`,
`AppliesOnHit.IsAttack`, `AppliesOnSpell`, `Type.Physical/Magic/True`, `WasCrit`, `OnHitDamage`, `Debuff.Burn`), its
target and amount. Items subscribe with a tag filter and a moment (`PreApply`, `PostApply`), exactly as their scripts
call `WaitForDealDamage(required, ignored)`. Attack releases and casts become events the same way
(`Combat.Event.LaunchAttack`, with the simulated-attack variant). Then a class's subscription is read straight off
its script.

**Keep:** crits stay averaged (expected damage per hit), with on-crit triggers firing each time the accumulated
crit chance passes 1 (ledger I6). Move that counter into the event system so every on-crit listener shares it.

**Done when:** `status.py` is gone or holds only `ActiveEffect`; the phase strings are gone; the tables are
unchanged.

### 5. One explicit dummy layout

**Now:** where the dummies stand is assumed piece by piece:

| Assumption | Where |
|---|---|
| Dummies 1 hex apart in a line | `bounce_hexes` (Trickshot, B12), Titanic Hydra's splash (I10) |
| The target stands at the unit's own attack range | `Timing.flight_ticks(attack_range)` (every flight) |
| Adjacent enemies = targets − 1 | Varus, Ziggs, Senna, Ezreal (`num_targets`) |
| Enemies 2 hexes away | Ezreal's Heartsteel casts (`num_extra_targets`) |

**Change:** place the dummies on hexes once (a configurable layout, the current assumptions as the default), and
answer "who is within N hexes of X", "how far is the target", "next ricochet target" from it. The target-count
sliders become layout settings.

**Done when:** the four rows above read from one place; the default layout gives the same tables.

## What not to do

- **No rewrite from scratch.** Each step must leave the simulator working and the tables unchanged.
- **Don't change game rules while restructuring.** If a step turns up a rule that looks wrong, log it in
  `docs/OPEN-QUESTIONS.md` and fix it in its own commit afterwards, with evidence.
- **Don't generate classes for every item automatically.** Decision D6 stands: each item is reviewed (its script
  read, its status in `docs/ITEMS.md`). The Radiants are generated only because they run the base item's reviewed
  script.

## Status

| Step | Status |
|---|---|
| 0. Durable copy of the tests; table-diff script | done: `tools/table_dump.py`; tests committed on branch `set19` |
| 1. Delete set18 leftovers | done (2026-11-17) |
| 2. Split modules, decorator registration | done (2026-11-17) |
| 3. Game-shaped attributes | done (2026-11-17) |
| 4. Timed effects and damage events | timed effects done (2026-11-17: `effects.ActiveEffect`, whole-tick ends, T14); damage events not started |
| 5. Dummy layout | not started |
