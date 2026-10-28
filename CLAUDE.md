# CLAUDE.md

A TFT (Teamfight Tactics) set 18 damage simulator: pick a champion, items,
traits and augments, simulate a 30s fight against dummies, and compare the
marginal DPS of one more item/buff. Live at <https://tftsimulator.app/>.

## Where you are

- **This directory (`set18/`) is its own git repo** (remote `origin`, default
  branch `main`). The folders above it (`tft_calculator/`, `tftSim/`) belong
  to a different, messy repo full of old sets. Commit here, never there.
- The parent `tft_calculator/` still holds set-5 `champion.py`, `status.py`
  and `buffs.py`. Anything run with a cwd outside `set18/` must put `set18/`
  first on `sys.path`, or imports silently pick up those stale files.
  `conftest.py` and `pytest.ini` (`--import-mode=importlib`) handle this for
  pytest.
- **Pushing to `main` deploys.** `.github/workflows/stlite-pages.yml`
  publishes the whole repo to GitHub Pages, so only push when the user asks.
- Files are CRLF. Edit tool calls keep that. A Python `read()`/`write()`
  round trip turns the whole file into a diff, so pass `newline=''` or
  avoid that route.
- `test_*.py` and `verify_*.py` are **gitignored on purpose**. The test suite
  is local-only. Do not force-add them.

## Commands

Use the venv interpreter: `.venv/Scripts/python` (Windows).

```bash
.venv/Scripts/python -m pytest -q --ignore=test_tank.py --ignore=test_tank_entry.py --ignore=test_tank_js.py
.venv/Scripts/python golden_harness.py --update   # after an intended output change
.venv/Scripts/python patch_check.py               # simulator numbers vs CommunityDragon
.venv/Scripts/python tft_data.py diff --refresh   # what moved on CommunityDragon
.venv/Scripts/python serve.py                     # static site on http://127.0.0.1:8618/
.venv/Scripts/python -m streamlit run app.py      # old Streamlit UI
```

The `test_tank*` files cover the survivability calculator, which lives only on
the unpublished `tank-calculator` branch (`tank_entry.py` is not on `main`).
`test_app_js.py` / `test_tank_js.py` shell out to `node` and are skipped
without it.

**Golden vectors** (`golden_harness.py`, `golden_vectors.json`,
`test_golden.py`) record every champion's exact damage vector. Any balance
change makes the touched champion's cases fail. That is them working. Check
that only the champions you meant to change failed, then run `--update`.
Per-champion tests sometimes hardcode the old number as well.

## Architecture

```
index.html + app.js  --postMessage-->  worker.js (Pyodide)  -->  sim_entry.py
   (UI, no Python)                     loads the .py files      catalog / champInfo / run
                                       listed in PY_FILES        |
                                                                 v
                              sim_core.do_experiment_one_extra -> simulator.Simulator
                                                                 |
                              set18champs / set18items / set18buffs / status
```

- **`sim_entry.py`** is the JSON boundary for the static site. `get_catalog()`
  builds every dropdown by *discovering* classes from the registry lists below.
  When you add a class to a list, it shows up in the UI with no JS change.
- **`worker.js` `PY_FILES`** lists every module the browser fetches. If you
  add a new module the simulator imports, add it there too, or the site
  breaks while the tests still pass.
- **`app.py`, `pages/`, `class_utilities.py`, `set18_streamlit_main.py`**
  make up the older Streamlit UI. `stlite.html` runs it in the browser, and
  the site only uses it for Mana Generation now. New pages need an entry in
  `app.py` `_DEEP_LINK_PAGES` and `404.html`.
- **`simulator.Simulator.simulate`** applies item stats, runs the
  `prePreCombat -> preCombat -> postPreCombat` phases, then steps
  `champion.update()` once per frame (30 fps by default). Opponents are
  dummies: they never attack or die and only tick their statuses.

### Registries: a class is not live until it is listed

| Kind | File | List(s) |
|---|---|---|
| Champion | `set18champs.py` | `champ_list` |
| Trait | `set18buffs.py` | `class_buffs` |
| Augment | `set18buffs.py` | `augments` (also `stat_buffs`, `wisps`, `no_buff`) |
| Item | `set18items.py` | `offensive_craftables`, `artifacts`, `radiants`, `emblems`, `mana_items`, ... |

### Champions (`set18champs.py`, base class `champion.py`)

- `__init__` passes the card's base stats (`hp, atk, curMana, fullMana, aspd,
  armor, mr`) plus a `Role`. Star scaling (AD x1.5, HP x1.8) happens in the
  base class.
- `self.default_traits = ["Riftbeast", "Ravager"]`: these traits are
  preselected in the buff bar and use the class names from `class_buffs`.
- Ability damage: `abilityScaling = create_ability_scaling([ad x3], [ap x3])`
  as a class attribute. A champion with several scalings passes `func_name`
  matching the attribute name, which keeps them picklable and visible to
  `patch_check.py`.
- `performAbility(self, opponents, items, time)` does the cast. Use
  `self.multiTargetSpell(...)` / `self.doDamage(...)` for damage and
  `self.applyStatus(status.X(), ...)` for timed effects (defined in
  `status.py`). `castTime` and `manalockDuration` control the lockouts.
- Always-on innate effects are an `Item`/`Buff` subclass appended to
  `self.items` in `__init__` (see Gromp's `AdaptorInnate`).
- Put balance numbers in **named class attributes**, never literals inside
  `performAbility`. `patch_hooks.py` can only check a number that has a name.
- Comments record the patch history of a number (`# 18.4b: 160/240/375 ->
  180/270/435`). Keep doing that.

### Items and buffs (`item.Item`, `set18buffs.Buff`)

- Flat stats go in the constructor. Behaviour goes in `performAbility(phase,
  time, champion, input_)`, which runs only for the phases listed in
  `phases=[...]`. Phases include `preCombat`, `postPreCombat`, `onUpdate`,
  `preAttack`, `onAttack`, `postAttack`, `onCrit`, `preAbility`,
  `postAbility`, `onDealDamage` and `onDealSpellDamage`.
- **Units differ per stat.** Item `crit=20` means 20%, divided by 100 in
  `addStats`. `omnivamp=0.15` is a fraction. `ad`, `ap` and `aspd` are percent
  points (`champion.bonus_ad.addStat(5)` is +5% AD, `ap.addStat(36)` is
  +36 AP). Inside a buff, `champion.crit.addStat(0.15)` is a fraction.
- Radiant items subclass the base item and override the stats
  (`RadiantHoJ(HoJ)`).
- A trait's `levels` lists its breakpoints. `extraParameters()` returns
  `{"Title", "Min", "Max", "Default"}` when the trait needs a per-champion
  input such as "Is Alpha". The value arrives as `self.params`.

## Balance patches

**Load the `tft-patch-update` skill** (`tft_calculator/.claude/skills/`)
before touching balance numbers. The short version:

- Precedence: **official patch notes** > lolchess card (the only source of
  AD/AP splits) > CommunityDragon, which lags on both channels.
- Do not guess the AD/AP split of a mixed ability from a total. Ask for the
  card's breakdown.
- When a note is ambiguous (for example, a single number for a per-star
  value), apply the most literal reading, say so in the code comment, and tell
  the user.
- Record what you followed in `patch_pin.json`: `patch`/`accepted`,
  `card_values` for ability scalings, and `acknowledged` when cdragon disagrees
  on purpose.
- Patch notes may mention a champion the simulator does not implement. Check
  `champ_list`, and report it as skipped instead of adding the champion.

## Conventions

- Commit messages: imperative subject, then a body that explains *why* and
  names the source of every balance number (see `git log`).
- The user wants the simplest control that works. Do not add realism
  toggles or extra modelling nobody asked for. When a mechanic is out of
  scope, say so in `self.notes` or a comment instead of half-modelling it.
