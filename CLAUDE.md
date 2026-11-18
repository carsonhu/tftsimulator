# CLAUDE.md

The TFT **Set 19** damage simulator, being set up. It started from set18's engine (verbatim import at set18
859db43, this repo's first commit) and differs in one governing way: **every number comes from a client build the
user selects**, and every rule about game behaviour is written down with its evidence.

Read `docs/ASSUMPTIONS.md` before changing any game rule, and the champion's worksheet before touching a champion.

## Where you are

- This directory is its own git repo (branch `main`, **no remote yet**). The folders above belong to another,
  messy repo. Commit here, never there.
- set18 is a separate, live repo (tftsimulator.app). Don't edit it from here and don't import from it.
- The parent `tft_calculator/` holds old set-5 `champion.py`, `status.py`, `buffs.py`; anything run with a cwd
  outside `set19/` must put `set19/` first on `sys.path`. `conftest.py` / `pytest.ini` handle this for pytest.
- Files carried over from set18 are CRLF; new files are LF. Keep each file's existing endings (Edit preserves
  them; a Python read/write round trip without `newline=''` rewrites every line).
- `test_*.py` and `verify_*.py` are gitignored on purpose (local-only tests).

## How the work is organised

| What | Where |
|---|---|
| Assumptions and decisions, with status and evidence | `docs/ASSUMPTIONS.md` |
| How to measure timing from VODs | `docs/evidence-method.md` |
| Which units are in scope (65 non-tanks) and removals with reasons | `roster.json` (hand-edited) |
| One worksheet per in-scope champion: build data, questions, evidence log, decisions | `champions/<Name>.md` |
| One row per item: stats effect, script, status, evidence (worksheet only when timing needs a VOD) | `docs/ITEMS.md` |
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
                              set19champs / set19items / set19buffs / status
```

- `simulator.Simulator.simulate` runs `prePreCombat -> preCombat -> postPreCombat`, then calls
  `champion.update()` once per 30 Hz tick. Opponents are `set19champs.TrainingDummy`: they never attack or die.
- **Timing core** (`timing.py`, `champion.py` `update`, rules T1-T9 in `docs/ASSUMPTIONS.md`, tests in
  `test_timing.py`): everything is decided in whole ticks. `BuildChampion` sets `self.timing =
  Timing.from_build(...)`; override a field only with cited evidence and record it in `Timing.source`. Delayed
  spell effects go through `self.schedule(seconds, fn)`, never a hand-made status. Attack damage and on-attack item
  effects happen when the attack lands.
- Registries: a class is live only when listed (`set19champs.champ_list`, `set19buffs.class_buffs` /
  `augments` / ..., `set19items` lists); champions so far: Neeko; the others are empty. `worker.js` `PY_FILES`
  lists every module the browser loads; a new module must be added there too. Builds reach the browser through
  the worker (B9): the newest at boot, others when the page's "Game build" picker names one. After changing the
  worker, the page or build loading, run `tools/browser_check/` (`npm install` there once; `node worker_e2e.js`,
  and `node page_e2e.js` with `python serve.py 8619` running).
- Items/buffs: behaviour in `performAbility(phase, time, champion, input_)` for the phases listed in `phases`
  (`preCombat`, `onUpdate`, `preAttack`, `onAttack`, `postAttack`, `onCrit`, `preAbility`, `postAbility`,
  `onDealDamage`, ...). Units differ per stat (item `crit=20` is 20%; `omnivamp=0.15` is a fraction; `ad`, `ap`,
  `aspd` are percent points).
- Tests (local, gitignored): `python -m pytest -q` with set18's venv (`../set18/.venv/Scripts/python`) until this
  repo has its own.

## Conventions

- Commit messages: imperative subject; the body explains why and names the source of every number (build version,
  VOD + timestamp, or ledger entry).
- The user wants the simplest control that works. When a mechanic is out of scope, say so in the worksheet and in
  `self.notes`, instead of half-modelling it.
- Don't push: there is no remote, and set18's GitHub Pages workflow (copied here) would publish if one were added.
