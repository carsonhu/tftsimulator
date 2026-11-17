# CLAUDE.md

The TFT **Set 19** damage simulator, being set up. It starts from set18's engine (verbatim import at set18
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
| Client builds the simulator can use | `builds/<version>.json`, `builds/index.json` (newest first) |
| Reading a build from Python | `buildstore.py` (`load_build`, `.champion(key).row(name)`, `.role(name).modifier(attr)`) |

Champions are done **one at a time** (decision D5): fill the worksheet's questions with evidence, then implement.
A Set 19 champion subclasses `build_champion.BuildChampion` with `KEY = 'DA_<Name>19'`: HP/AD per star, mana,
attack speed and cap, range, role mana and timing all come from the selected build (ledger B1-B9), and ability
numbers are read by curve-row name (`self.row('APDamage')`), never typed in. A missing value raises
`BuildDataError` naming the build; don't catch it to default to 0.

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

## Engine (inherited from set18)

The architecture, registries and conventions below are set18's and still describe the code until adapted.
Adapting them is tracked in `docs/ASSUMPTIONS.md` (E-entries).

```
index.html + app.js  --postMessage-->  worker.js (Pyodide)  -->  sim_entry.py
                                                                 |
                              sim_core.do_experiment_one_extra -> simulator.Simulator
                                                                 |
                              set18champs / set18items / set18buffs / status
```

- `simulator.Simulator.simulate` runs `prePreCombat -> preCombat -> postPreCombat`, then calls
  `champion.update()` once per 30 Hz tick. Opponents are dummies: they never attack or die.
- **Timing core** (`timing.py`, `champion.py` `update`, rules T1-T9 in `docs/ASSUMPTIONS.md`, tests in
  `test_timing.py`): everything is decided in whole ticks. A Set 19 champion sets `self.timing =
  Timing.from_build(build.champion(key))` and overrides fields only with cited evidence (record it in
  `Timing.source`). Delayed spell effects go through `self.schedule(seconds, fn)`, never a hand-made status.
  Attack damage and on-attack item effects happen when the attack lands. The old set18 timing attributes
  (`castTime`, `manalockDuration`, `attackWindup`, `nextAttackTime`, `manalockTime`) work only as compatibility
  for the Set 18 content (C1).
- Registries: a class is live only when listed (`champ_list`, `class_buffs`, `augments`, item lists).
  `worker.js` `PY_FILES` lists every module the browser loads; a new module must be added there too.
- Items/buffs: behaviour in `performAbility(phase, time, champion, input_)` for the phases listed in `phases`.
  Units differ per stat (item `crit=20` is 20%; `omnivamp=0.15` is a fraction; `ad`, `ap`, `aspd` are percent
  points).

## Conventions

- Commit messages: imperative subject; the body explains why and names the source of every number (build version,
  VOD + timestamp, or ledger entry).
- The user wants the simplest control that works. When a mechanic is out of scope, say so in the worksheet and in
  `self.notes`, instead of half-modelling it.
- Don't push: there is no remote, and set18's GitHub Pages workflow (copied here) would publish if one were added.
