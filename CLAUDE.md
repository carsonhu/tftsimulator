# CLAUDE.md

The TFT **Set 19** damage simulator, being set up. It started from set18's engine (verbatim import at set18
859db43, this repo's first commit) and differs in one governing way: **every number comes from a client build the
user selects**, and every rule about game behaviour is written down with its evidence.

Read `docs/ASSUMPTIONS.md` before changing any game rule, and the champion's worksheet before touching a champion.

## Where you are

- This directory is its own git repo. Work happens on branch `set19`, which tracks `origin/set19` on
  github.com/carsonhu/tftsimulator (set18's repo, beside its `set16`-`set18` branches). Local `main` is never
  pushed: `origin/main` is set18's live site, and this repo shares no history with it. The folders above belong
  to another, messy repo. Commit here, never there.
- set18 is a separate, live repo (tftsimulator.app). Don't edit it from here and don't import from it, but **use it
  as the reference for how things are done**, ordering above all: before writing a mechanic, read the set18
  equivalent and follow its phase unless evidence says otherwise; list every deviation in the ledger (O1-O5).
- The parent `tft_calculator/` holds old set-5 `champion.py`, `status.py`, `buffs.py`; anything run with a cwd
  outside `set19/` must put `set19/` first on `sys.path`. `conftest.py` / `pytest.ini` handle this for pytest.
- Files carried over from set18 are CRLF; new files are LF. Keep each file's existing endings (Edit preserves
  them; a Python read/write round trip without `newline=''` rewrites every line).
- `test_*.py` are committed on branch `set19` (2026-11-17: the restructure needs a durable copy, docs/RESTRUCTURE.md);
  on `main` they are still gitignored. `verify_*.py` stay gitignored (local-only).

## How the work is organised

| What | Where |
|---|---|
| Assumptions and decisions, with status and evidence | `docs/ASSUMPTIONS.md` |
| Every open question, grouped by the clip that would answer it (add a row with each new assumption; delete it when answered) | `docs/OPEN-QUESTIONS.md` |
| How to measure timing from VODs | `docs/evidence-method.md` |
| The plan for restructuring the engine (set18 leftovers, attributes, effects, damage events, dummy layout) | `docs/RESTRUCTURE.md` |
| Which units are in scope (65 non-tanks) and removals with reasons | `roster.json` (hand-edited) |
| One worksheet per in-scope champion: build data, questions, evidence log, decisions | `champions/<Name>.md` |
| One row per item: stats effect, script, status, evidence (worksheet only when timing needs a VOD) | `docs/ITEMS.md`, `items/<Name>.md` |
| Client builds the simulator can use | `builds/<version>.json`, `builds/index.json` (newest first) |
| Reading a build from Python | `buildstore.py` (`load_build`, `.champion(key).row(name)`, `.role(name).modifier(attr)`) |

Champions are done **one at a time** (decision D5): fill the worksheet's questions with evidence, then implement.
A Set 19 champion subclasses `build_champion.BuildChampion` with `KEY = 'DA_<Name>19'`: HP/AD per star, mana,
attack speed and cap, range, role mana and timing all come from the selected build (ledger B1-B9), and ability
numbers are read by curve-row name (`self.row('APDamage')`), never typed in. A missing value raises
`BuildDataError` naming the build; don't catch it to default to 0. Spell effects are timed from the build's chronos
(`self.chrono_event(...)`, `self.chrono_projectile_speed(...)`, B10) and scheduled with `self.schedule_tick`; trait
values a spell reads come from `self.trait_value(...)` at the tier the board's trait buff set (B11; traits are
`set19buffs.BuildTrait` subclasses with a `KEY`, levels = units on the board). `set19champs.Neeko` is the worked example: its
docstring and worksheet decision D1 cite the script for each structural fact.

## Commands

```bash
python tools/import_build.py         # copy new snapshots from tftDatamine/builds into builds/
python tools/patch_notes_build.py builds/patch_notes/<file>.json
                                     # a build from patch notes when the client can't be read (B33: PBE's
                                     # archives are encrypted since 2026-11-18); checks every old value.
                                     # An encrypted build can also be read from an FModel raw export (B34):
                                     # tftDatamine snapshot_build.py with TFT_LOOSE=F:/tft_projects/Output/Exports
python tools/new_build_report.py     # a report on each snapshot not imported yet (builds/<version>/sim_report.md
                                     # in tftDatamine): data changes, every table on both builds, failures, read
                                     # problems; changes nothing here. The snapshot task runs it every 3 hours
python tools/worksheets.py           # refresh the AUTO block of each worksheet from the newest build;
                                     # also warns if a build disagrees with roster.json
python tools/worksheets.py --build <version>
python tools/table_dump.py out.json  # every table for every champion; --diff a.json b.json before/after a refactor
python tools/icons.py                # icons/ for every registered item, augment and trait, from the client's art
                                     # (tftDatamine runs/set19: data.json + TftExport textures); rerun after adding one
python serve.py                      # the page on http://127.0.0.1:8618/
```

Snapshots are made on the datamining side: `F:/tft_projects/tftDatamine/tools/snapshot_build.py`, run every 3 hours
by the Windows scheduled task "TFT build snapshot" (`tools/snapshot_task.bat` there; log in
`tftDatamine/builds/snapshot_task.log`). A snapshot is never overwritten except with `--force` after a tool fix.
If a new build shows many `read_problems` in its manifest, its class layouts changed: re-dump the usmap with
`tftDatamine/tools/usmap_no_replay.ps1 -Install PBE` (admin PowerShell; the user runs it).

## Worksheets

`champions/<Name>.md` has a generated block between `<!-- AUTO BEGIN` and `<!-- AUTO END -->` (build data,
predicted timing, every timeline in the champion's folder, script hints, changes since the previous build). It is
rewritten by `tools/worksheets.py`. **Everything outside it is human-written and is never regenerated**: status,
the question table, the evidence log, decisions. Put findings there, never inside the AUTO block.

Question statuses: open / predicted (client data only) / confirmed / refuted / not applicable. Only evidence
moves a status (see `docs/evidence-method.md`).

## Engine

The engine started as set18's (first commit). Set 18's champions, traits, augments, items, roles, Streamlit pages
and CommunityDragon patch tools are removed (E16); everything Set 19 is written from the build, one at a time.

```
index.html + app.js  --postMessage-->  worker.js (Pyodide)  -->  sim_entry.py
                                                                 |
                              sim_core.do_experiment_one_extra -> simulator.Simulator
                                                                 |
                              set19champs / set19items (items/) / set19buffs (traits/) / status
```

- Where code lives: augments in `augments/` (`base.py`: BuildAugment; `combat.py`: the offensive combat augments and
  the Sunder30 / Shred30 entries; ledger A1-A8), items in `items/` (`base.py`: NoItem, the stats layer, BuildItem, StackingItem, item_name;
  `debuffs.py`: sunder, shred (burn is not simulated: owner); `craftables.py`, `radiants.py`, `artifacts.py`,
  `emblems.py`: Spatula items and plain-stat emblems), traits in `traits/` (one module
  per trait, `base.py`: Buff, NoBuff, BuildTrait). `set19items` and `set19buffs` gather them, so every class is still
  `set19items.<Class>` / `set19buffs.<Class>`; the import order in `set19buffs` is the order traits are offered and
  run in. `items/` also holds the item worksheets (`items/<Name>.md`).

- The table's DPS columns (`sim_entry.DPS_WINDOWS`, owner 2026-11-18): the average DPS over fights ending anywhere
  in 10-20 s and 20-30 s, every hit counted (`_dps_window`); rows sort by the 20-30 s ratio (the "DPS ÷ NoItem" column; it was "Extra DPS" until 2026-11-19: owner, misleading beside the DPS columns). Not DPS at
  one instant: a cast just after it would swing the number.
- `simulator.Simulator.simulate` runs `prePreCombat -> preCombat -> postPreCombat`, then calls
  `champion.update()` once per 30 Hz tick. Opponents are `set19champs.TrainingDummy`: they never attack or die.
- **Timing core** (`timing.py`, `champion.py` `update`, rules T1-T9 in `docs/ASSUMPTIONS.md`, tests in
  `test_timing.py`): everything is decided in whole ticks. `BuildChampion` sets `self.timing =
  Timing.from_build(...)`; override a field only with cited evidence and record it in `Timing.source`. Delayed
  spell effects go through `self.schedule(seconds, fn)`, never a hand-made status. Attack damage and on-attack item
  effects happen when the attack lands.
- Registries: an item or buff is live only when decorated `@register(kind)` (`registry.py`; kinds craftable,
  radiant, artifact, emblem, trait, augment), which fills `set19items.offensive_craftables` / `radiants` /
  `artifacts` / `emblems` and `set19buffs.class_buffs` / `augments`; champions are live when listed in
  `set19champs.champ_list` (Neeko, Varus, Draven, Kai'Sa, Yunara, Ziggs, Senna, Ezreal, Lux, Gnar, Malzahar, Samira,
  Karthus, Ashe, Viego, Kayle, Lucian, RenataGlasc, Zoe, Bard, Syndra, Briar, Xayah, Katarina, Kayn, Qiyana, Seraphine (+ SeraphineRisingStar, SeraphineSuperstar), Yuumi, Yone, Tristana, Mel, Jinx, Ahri, Jhin, OlafHeroAugment (hero augment units are separate champions: `roster.json` `hero_augments`);
  traits: Encore, Trickshot, K/DA, Swiftstriker, Arcanist, Hitmaker, True Damage, Illbeats, Heartsteel, Hyperpop, Ionic
  Spark, Prodigy, Pentakill, Composer, Renegade, Classical, Slayer, Choreographer, Jazz, Beach Pop, Gu Feng). A debuff a spell applies uses the shared helpers in `items/debuffs.py`
  (`apply_shred`, `apply_sunder`). A new trait is
  a module in `traits/` plus its import line in `set19buffs.py`. `worker.js` `PY_FILES` lists every module the
  browser loads; a new module must be added there too (`test_sim_entry.py` checks the `items/` and `traits/` ones). Builds reach the browser through
  the worker (B9): the newest at boot, others when the page's "Game build" picker names one. After changing the
  worker, the page or build loading, run `tools/browser_check/` (`npm install` there once; `node worker_e2e.js`,
  and `node page_e2e.js` / `node viz_e2e.js` (the fight viewer) with `python serve.py 8619` running).
- Items: `set19items.BuildItem` subclasses with `KEY` and `STATS` (the effects reviewed as the item's unconditional
  stats, `docs/ITEMS.md`); stats and tags are applied at combat start from the champion's build (ledger I1-I3), and
  anything the layer can't apply exactly raises. A scripted item is registered only once its script is implemented.
- Items/buffs: lifecycle behaviour in `performAbility(phase, time, champion, input_)` for the phases listed in
  `phases` (`prePreCombat`, `preCombat`, `postPreCombat`, `onUpdate`, `preAbility`, `postAbility`). Combat events
  (`events.py`: `LAUNCH` (attack release and simulated attacks, G11), `ONHIT_PRE`, `CRIT`, `DAMAGE_POST`,
  `ONHIT_AFTER`) are heard by declaring `LISTENS = {moment: tags}`, the tags the script waits for (e.g.
  `{DAMAGE_POST: {UNIT}}` for WaitForDealDamage(Damage.Source.Unit)); the handler gets a `CombatEvent` (source,
  target, amount, type, tags) as `input_`. Damage an item or debuff deals itself is tagged `Damage.Source.Item`.
  Timed effects on a unit are `effects.ActiveEffect`s (`apply_effect`, whole-tick ends, T14). A trait's parameter (`extraParameters`) is a number, a named choice (`Options`) or tick
  boxes (`Flags`: bit i is Flags[i]; `TeamFlags` limits the Team Traits panel to the leading ones; Heartsteel).
  Team Traits lists a trait with an "Is X" flag, `Options` or `Flags`, or one that says `team_trait = True` (its
  team-wide half reaches non-members: Arcanist, Choreographer, Swiftstriker, Composer, Prodigy, Jazz, Manager; owner,
  2026-11-19); a plain number parameter there is a number box (Composer's instruments, Jazz's active traits).
  `team_trait = False` opts one out (Hitmaker, Beach Pop). The panel works like the buff bar (owner, 2026-11-19):
  empty until "+ Add" picks a trait (`teamTraitChoices`), each added one a row (`teamTraitRow`: level where `scales`,
  its option / count / tick boxes underneath, × removes it); `state.teamBuffs` holds exactly the added rows.
  Heartsteel, nothing ticked, is always there to start (`ensureDefaultTeamTraits`, unless it is the champion's own).
  The page names the panel's traits in cfg["team"]: the Trait slice sweeps the buff bar only, the "Team Traits"
  slice (`team_sweep_buffs`) the panel's, and only what changes a non-member: Heartsteel one row per member flipped
  ("Heartsteel (+Kayn)"), a level-scaling trait its other levels, a flat one its other state ("Swiftstriker 0").
  A trait can name its own sweep (`sweep_rows(level, params, member, champ_key)`, used by both slices): Heartsteel's
  member rows are levels 0 / 3 / 7 only ((1)-(5) differ only by the Bias; (7) adds 150%), the Bias flipped, and
  each other member fielded or not ("Heartsteel 3 (+Kayn)"; never the unit's own box) (owner, 2026-11-19).
  A team trait's hover card there (panel rows, its + Add picker, the Team Traits tab's rows) shows only the
  team-wide half: `BuildTrait.team_card(build)` (text + rows of [value, stat tag] per breakpoint, from the build;
  Heartsteel's four damage members), sent as the card's "team" by `sim_entry.get_cards`.
  Stats are `stats.Attribute`s in game units, changed only with modifiers: `champion.aspd.modify("MultiplyAdditive",
  1.1)`, `champion.ap.modify("+", 0.2)`, keyed when the effect is later removed or re-sized. AD and AP are
  multipliers from 1.0, AS is attacks per second, crit / crit damage / omnivamp / amp are fractions; ops and
  channels are the build's (`+` AddBase, MultiplyAdditive, MultiplyCompound, AddFinal, `=` Override, bounds), and
  `champion.attribute("AttackSpeed")` finds one by the game's name (ledger I1, I5).
- Where the dummies stand is `layout.py` (the page's 'Number of targets', default 2: the target and the others next
  to it, plus one more 2 hexes behind the target in a line, G22; shown only for champions with `AREA = True`, whose damage depends on it). Ask it, never index `opponents[1:]`: `self.target_hexes()` for a flight,
  `self.nearby(target, hexes)` for a splash (the script's HexRange), `self.ricochet(previous, hit)` for a bounce, `self.line(target, length, width)` for a
  line (Bard's wave).
  `opponents[0]` is the target.
- The page (owner, 2026-11-19): a top bar (champion portrait + stars, enemy HP/armor/MR, build, stage, tactician,
  targets, takedowns), then three columns that fill the window and scroll on their own: setup (item slots, buff
  rows, stats grid, team traits), the table, and a pane with the fight viewer on top and the damage chart under it, both always visible (owner: no tabs); the chart heading pictures the run's setup (`renderPlotSummary`: portrait + stars, items, active traits with levels, augments, bonuses), drawn from `state.currentCfg`; the viewer's playhead is a line + per-row readout on the chart (`placePlayhead`, an HTML overlay; hovering the plot moves the same line and card to the pointer's time, Plotly's hover is off). The viewer heading has the same pictures plus a dropdown of the plotted rows (`renderVizPicker`): plotting a row shows its fight, un-plotting the one on view falls back to the last plotted row. The table's "Show: DPS | Ratio vs NoItem" switch (`#valueMode`; `state.displayDps` true = ratios) replaced the "Display DPS" checkbox, whose name said the opposite of what it did. A champion with forms (Seraphine: `MODE` on each class; the catalog's `variantOf` / `mode`) is one menu entry, its form a switch beside the stars that keeps items and buffs (`renderChampModes`); hero augment units read "Olaf (Hero)". Trait levels show 0, never "off" or "—" (owner). The champion's own traits (`state.ownTraits`) never leave the buff bar: × sets one to 0 and hides while it is 0. The ratio is "DPS ÷ Base" / "Ratio vs Base" (owner: Base, not NoItem, in names). The table takes 44% of the width at a larger font. Bonus tags in the headings use the icons/stats glyphs (`BONUS_GLYPHS`). Each table row has a "+" (on hover) that adds its extra to the setup (`rowAddPlan`: an item to the first empty slot; a trait or augment in the buff bar set to the row's level and parameter, the row's `extraParams` from sim_entry; a team trait in Team Traits; else a new buff row). The chart's legend is HTML (`renderChartLegend`: colour, row art, name; a click shows that fight), Plotly's is off. The Stats panel and the viewer card show AP, crit, crit damage and amp as percentages and say "Mana regen" (owner). The Stats panel shows crit capped at 1 and crit damage including the excess (`excessCritRatio`, as `champion.critDamage` computes it). With no row plotted the chart draws NoItem alone (`plottedSlots`); the first row plotted replaces it, and NoItem clicked on purpose stays with the others; NoItem always draws in its own grey (`BASE_SLOT`/`BASE_COLOR`), outside the palette, so the row that replaces it never inherits its colour. A row whose result hangs on its own number reads "Hold the Line ([7] units)" with the number a box (`rowNameWithInput`, `cfg.rowInputs` by class; sim_entry `_row_input_spec`: a buff parameter with a `"Row"` template, or an item's `ROW_INPUT`): Hold the Line (front-row allies 0-7, default 7; one augment, not one class per count; a one-digit box takes each keystroke as the value), Comeback Story (Health, 50), Cappa Juice (takedowns: follows the top bar's Takedowns until typed over, and again after Takedowns changes). Artifacts and radiants wear the client's item frames (`icons/frames`, `tools/icons.py item_frames`, CSS `.item-framed`). Below 1320 px the pane
  drops under the table; below 900 px setup is a drawer. Champions, items and buffs are chosen in `Picker` icon grids
  (by cost / item kind / trait-augment, search, arrow keys); each choice is still a hidden `<select>` (`hookValue`,
  `pickInto`), which the browser checks drive directly. The catalog's `kind` on items and buffs names the grid's
  sections. The Index Log and pie are gone: the viewer's log and its card's damage split replace them.
- The fight viewer (the panel beside the table: `viz.js`, `fight_trace.py`, `sim_entry.run_trace`) replays one row's
  fight. A `fight_trace.Tracer` on `champion.tracer` records every hit, cast, attack launch and a stat snapshot per
  tick; table runs have none, and every engine hook is one `is not None` check (`test_fight_trace.py`: a recorded
  fight equals the unrecorded one). A spell projectile is scheduled with `self.fly(launch_tick, flight_ticks, target,
  fn, source=..., name=...)` (the same as `schedule_tick(launch + flight, fn)`, plus the drawing); a visual-only one
  with `self.trace_projectile(...)`; an area, beam or dash with `self.trace('area', at=target, hit=[...])`. Add these
  with each new champion so its spell shows.
- Tests (committed on `set19`): `python -m pytest -q` with set18's venv (`../set18/.venv/Scripts/python`) until this
  repo has its own.

## Conventions

- Commit messages: imperative subject; the body explains why and names the source of every number (build version,
  VOD + timestamp, or ledger entry).
- The user wants the simplest control that works. When a mechanic is out of scope, say so in the worksheet and in
  `self.notes`, instead of half-modelling it.
- Push `set19` (`git push origin set19`) after each restructure step and each champion lands (owner, 2026-11-17 / 18).
  The Pages workflow publishes on a push to `main` only, which is set18's live site: never push to `main` from here.
