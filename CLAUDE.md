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
  in 10-20 s and 20-30 s, every hit counted (`_dps_window`); rows sort by the 20-30 s ratio (Extra DPS). Not DPS at
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
  Karthus, Ashe, Viego, Kayle, Lucian, RenataGlasc, Zoe, Bard, Syndra, Briar, OlafHeroAugment (hero augment units are separate champions: `roster.json` `hero_augments`);
  traits: Encore, Trickshot, K/DA, Swiftstriker, Arcanist, Hitmaker, True Damage, Illbeats, Heartsteel, Hyperpop, Ionic
  Spark, Prodigy, Pentakill, Composer, Renegade, Classical, Slayer, Choreographer, Jazz, Beach Pop). A debuff a spell applies uses the shared helpers in `items/debuffs.py`
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
