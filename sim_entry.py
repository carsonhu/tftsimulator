# sim_entry.py
#
# JSON boundary between the static v2 frontend (v2/) and the simulator.
# The v2 page runs this file under Pyodide with *no* installed packages, so
# nothing here (or in anything it imports) may touch streamlit, numpy or
# pandas -- that restriction is the whole reason v2 boots in a couple of
# seconds instead of sitting through stlite's "Installing packages." phase.
#
# Three entry points, each taking/returning JSON strings so the JS side never
# holds a live PyProxy:
#   catalog_json()            -> everything needed to draw the sidebar
#   champ_info_json(config)   -> stat panel + per-champ UI hints for one config
#   run_json(config)          -> table rows + plot timelines for one slice
#
# The config schema is documented on _build_champion. Where this file mirrors
# the Streamlit pages (pages/ChampionSelector.py, set18_streamlit_main.py,
# class_utilities.py), it mirrors them *exactly* -- including the int()
# truncation in getDPS and np.unique's keep-first-duplicate behavior -- so the
# two frontends can never disagree about a number. test_sim_entry.py holds the
# side-by-side comparison.

import inspect
import json
from bisect import bisect_right

import set18buffs
import set18champs
import set18items
import sim_core
from helpers import buff_display_map, buff_display_names, item_display_map
from simulator import Simulator

DPS_TIMES = [5, 10, 15, 20, 25]

# The branch that computes one radio slice at a time added this kwarg to
# sim_core; on main it does not exist and the Blackthorn sweep simply runs
# whenever the champion carries the trait. Detecting it here means this file
# works unchanged on both sides of that merge.
_SUPPORTS_RUN_BLACKTHORN = (
    "run_blackthorn"
    in inspect.signature(sim_core.do_experiment_one_extra).parameters
)

# Stats a trait's team-wide half could plausibly move. Compared alongside the
# damage vector when deciding whether a team trait's level matters.
_PROBE_STATS = (
    "atk", "bonus_ad", "ap", "aspd", "crit", "critDmg",
    "dmgMultiplier", "manaRegen", "manaPerAttack", "fullMana",
)


def _team_level_matters(cls):
    """Does this trait's team-wide half change with its level?

    For most traits it does not: Rapidfire's aura is a flat 10% Attack Speed
    and Spellweaver's a flat 10 AP at every breakpoint -- only the members'
    own bonus scales, and a non-member never gets that. Lunar is the
    exception, where the shared aura itself steps 7/10/14/18. The UI shows a
    plain on/off checkbox for the flat ones and a level picker only where the
    level actually changes the answer.

    Decided by running the trait at each level with the membership flag off
    and comparing what came out, rather than by a hardcoded list, so a trait
    added later is classified correctly without touching this file. The
    reference champion is fixed (first in sorted order) because the question
    is about the trait, not about any particular unit.
    """
    reference = getattr(set18champs, sorted(set18champs.champ_list)[0])
    signatures = set()
    for level in cls.levels:
        if level == 0:
            continue
        try:
            champ = reference(1)
            results = Simulator().simulate(
                [],
                [cls(level, 0)],
                champ,
                [set18champs.DummyTank(1) for _ in range(8)],
                10,
                frameRate=30,
            )
        except Exception:
            # A trait that cannot run headless here is left as a level
            # picker: showing one control too many is the safe failure.
            return True
        signatures.add(
            (
                tuple(round(getattr(champ, s).stat, 9) for s in _PROBE_STATS),
                tuple((round(r[0], 9), round(r[1][0], 9), r[1][1]) for r in results),
            )
        )
        if len(signatures) > 1:
            return True
    return False


_ITEM_SLICES = {
    "Craftable": lambda: set18items.offensive_craftables,
    "Artifact": lambda: set18items.artifacts,
    "Radiant": lambda: set18items.radiants,
    "Emblem": lambda: set18items.emblems,
    "Anima": lambda: set18items.animas,
}


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def get_catalog():
    champions = []
    for name in sorted(set18champs.champ_list):
        cls = getattr(set18champs, name)
        levels = [1, 2, 3]
        if getattr(cls, "canFourStar", False):
            levels.append(4)
        champions.append({"name": name, "levels": levels})

    def item_group(class_names):
        # item_display_map returns {display: cls} in the order given; the
        # sidebar sorts by class name, same as pages/ChampionSelector.py.
        return [
            {"cls": cls, "name": disp}
            for disp, cls in item_display_map(sorted(class_names)).items()
        ]

    all_items = (
        set18items.offensive_craftables
        + set18items.artifacts
        + set18items.radiants
        + set18items.emblems
        + set18items.animas
        + set18items.no_item
    )

    all_buffs = sorted(
        set18buffs.class_buffs
        + set18buffs.augments
        + set18buffs.no_buff
        + set18buffs.stat_buffs
        + set18buffs.wisps
    )
    buffs = []
    for disp, cls_name in buff_display_map(all_buffs).items():
        cls = getattr(set18buffs, cls_name)
        try:
            extra = cls.extraParameters()
        except Exception:
            extra = 0
        buffs.append(
            {
                "cls": cls_name,
                "name": disp,
                "levels": list(cls.levels),
                # 0 means "no extra parameter"; otherwise
                # {"Title", "Min", "Max", "Default"} straight from the class.
                "extra": extra if extra else None,
            }
        )

    # Team traits: a trait your board runs that this champion is not part of.
    # Two shapes qualify, and both are discovered from the classes rather than
    # listed by name, so a trait added later turns up here on its own.
    #
    #   * an "Is X" 0/1 membership flag. Passing 0 is what "my team has this
    #     trait but this champion isn't one of them" means -- the aura half
    #     applies, the member-only half doesn't.
    #   * a named choice (Greenfather's Hex). There is no membership to
    #     disclaim: whoever stands on Ivern's hex gets what the hex gives,
    #     Ivern or not. The parameter is a real question rather than a flag to
    #     zero, so the panel has to ask it.
    team_buffs = []
    for cls_name in set18buffs.class_buffs:
        cls = getattr(set18buffs, cls_name)
        try:
            extra = cls.extraParameters()
        except Exception:
            continue
        if not extra:
            continue
        options = extra.get("Options")
        if not options and (extra.get("Min"), extra.get("Max")) != (0, 1):
            continue
        levels = list(cls.levels)
        # A trait that asks which variant is on always needs its level asked
        # too -- the probe below answers "does the team-wide half differ per
        # breakpoint", which is not the question when there is no team-wide
        # half to compare.
        scales = True if options else _team_level_matters(cls)
        team_buffs.append(
            {
                "cls": cls_name,
                "name": getattr(cls, "display_name", cls_name),
                # 0 is "trait not active" and is the off position, so it is
                # offered as a level like any other.
                "levels": levels,
                "paramTitle": extra["Title"],
                # None -> the param is the 0/1 flag and the panel passes 0.
                # A list -> the panel offers these and passes the index.
                "options": list(options) if options else None,
                "paramDefault": extra.get("Default", 0),
                # False -> the UI shows a checkbox and uses onLevel; True ->
                # it shows a level picker.
                "scales": scales,
                "onLevel": next((l for l in levels if l > 0), 0),
            }
        )

    blackthorn = None
    bt = getattr(set18buffs, "Blackthorn", None)
    if bt is not None:
        blackthorn = {
            "roles": list(bt.selectable_roles),
            "costs": [{"value": c, "label": bt.costLabel(c)} for c in bt.costs],
            "starsByCost": {
                str(c): [
                    {"value": s, "label": bt.starLabel(s)}
                    for s in bt.starLevels(c)
                ]
                for c in bt.costs
            },
        }

    return {
        "champions": champions,
        "sidebarItems": item_group(all_items),
        "buffs": buffs,
        "teamBuffs": team_buffs,
        "slices": [
            "Craftable",
            "Artifact",
            "Radiant",
            "Emblem",
            "Trait",
            "Augment/Buff",
            "Wisp",
        ],
        "blackthorn": blackthorn,
        "defaults": {
            "enemy": {"hp": 1800, "armor": 100, "mr": 100},
            "stages": ["2-1", "3-1", "4-1", "5-1", "6-1"],
            "stageDefault": "4-1",
            "tactician": {"min": 3, "max": 10, "default": 4},
            "frameRates": [30, 60],
            "duration": 30,
            "numItems": 3,
            "numBuffs": {"min": 1, "max": 10, "default": 2},
        },
        "dpsTimes": DPS_TIMES,
    }


# ---------------------------------------------------------------------------
# Config -> live objects
# ---------------------------------------------------------------------------

def _build_champion(cfg):
    """Mirror of the ChampionSelector sidebar, in its order.

    cfg = {
      "champ": "Ahri", "level": 1,
      "num_targets": int|null, "num_extra_targets": int|null,
      "takedowns": 0, "num_traits": 6,
      "bonus": {"ad","ap","as","manaregen","mpa","dmgamp","crit","critdmg"},
      "stage": "4-1", "tactician_level": 4,
      "blackthorn": {"role","star","cost"}|null,
      "items": ["NoItem","NoItem","NoItem"],       # class names
      "buffs": [["Blossom", 2, 0], ...],           # (class, level, params)
      "enemy": {"hp","armor","mr"},
      "frame_rate": 30, "t": 30, "slice": "Craftable",
    }
    """
    champ = getattr(set18champs, cfg["champ"])(int(cfg["level"]))

    # The sliders only exist for champs whose defaults are non-zero, so a
    # stored value is only applied where the page would have shown a slider.
    if champ.num_targets > 0 and cfg.get("num_targets") is not None:
        champ.num_targets = int(cfg["num_targets"])
    if champ.num_extra_targets > 0 and cfg.get("num_extra_targets") is not None:
        champ.num_extra_targets = int(cfg["num_extra_targets"])

    champ.takedowns = int(cfg.get("takedowns", 0))
    champ.num_traits = int(cfg.get("num_traits", 6))

    bonus = cfg.get("bonus", {})
    champ.bonus_ad.addStat(float(bonus.get("ad", 0)))
    champ.ap.addStat(float(bonus.get("ap", 0)))
    champ.aspd.addStat(float(bonus.get("as", 0)))
    champ.manaRegen.addStat(float(bonus.get("manaregen", 0)))
    champ.manaPerAttack.addStat(float(bonus.get("mpa", 0)))
    champ.dmgMultiplier.addStat(float(bonus.get("dmgamp", 0)) / 100)
    champ.crit.addStat(float(bonus.get("crit", 0)) / 100)
    champ.critDmg.addStat(float(bonus.get("critdmg", 0)) / 100)

    stage = cfg.get("stage", "4-1")
    champ.stage = int(str(stage).split("-")[0])
    champ.tactician_level = int(cfg.get("tactician_level", 4))

    bt = cfg.get("blackthorn")
    if bt:
        champ.blackthorn_role = bt["role"]
        champ.blackthorn_cost = int(bt["cost"])
        champ.blackthorn_star = int(bt["star"])

    for item_cls in cfg.get("items", []):
        if item_cls and item_cls != "NoItem":
            champ.items.append(getattr(set18items, item_cls)())
            champ.item_count += 1

    for name, level, params in cfg.get("buffs", []):
        if name != "NoBuff":
            champ.items.append(getattr(set18buffs, name)(level, params))

    return champ


def _build_enemy(cfg):
    enemy_cfg = cfg.get("enemy", {})
    enemy = set18champs.DummyTank(1)
    enemy.hp.base = float(enemy_cfg.get("hp", 1800))
    enemy.armor.base = float(enemy_cfg.get("armor", 100))
    enemy.mr.base = float(enemy_cfg.get("mr", 100))
    return enemy


# ---------------------------------------------------------------------------
# DPS math (pure-python mirror of set18_streamlit_main.getDPS)
# ---------------------------------------------------------------------------

def _cumulative_points(results):
    """(times, cumulative damage), duplicates collapsed to first occurrence.

    getDPSFunction cumsums in event order and then keeps np.unique's *first*
    index per duplicate timestamp; results arrive chronological so no sort is
    needed here, but the keep-first rule must match or interpolated values
    drift on frames with several damage instances.
    """
    xs, ys = [], []
    cum = 0.0
    for inst in results:
        cum += inst[1][0]
        t = float(inst[0])
        if xs and xs[-1] == t:
            continue
        xs.append(t)
        ys.append(cum)
    return xs, ys


def _interp(xs, ys, t):
    if not xs:
        return 0.0
    if t <= xs[0]:
        return ys[0]
    if t >= xs[-1]:
        return ys[-1]
    i = bisect_right(xs, t)
    x0, x1 = xs[i - 1], xs[i]
    y0, y1 = ys[i - 1], ys[i]
    return y0 + (y1 - y0) * (t - x0) / (x1 - x0)


def _dps_at(xs, ys, t):
    res = _interp(xs, ys, t) / t
    # Same presentation rule as getDPS's caller: big numbers lose the
    # fraction. The truncated value also feeds the ratio columns, so this is
    # arithmetic, not just formatting.
    if res > 10:
        res = int(res)
    return res


# ---------------------------------------------------------------------------
# Slices and rows
# ---------------------------------------------------------------------------

def _slice_inputs(slice_name, cfg):
    """(item objects, buff objects, run_blackthorn) for one radio option.

    Every slice carries NoItem because the "Extra DPS" columns are ratios
    against that row.
    """
    no_item = [set18items.NoItem()]

    if slice_name in _ITEM_SLICES:
        classes = list(_ITEM_SLICES[slice_name]())
        return [getattr(set18items, c)() for c in classes] + no_item, [], False

    if slice_name == "Trait":
        # Every *other* level of each buff currently in the buff bar.
        extra = []
        for name, level, params in cfg.get("buffs", []):
            cls = getattr(set18buffs, name)
            for lvl in cls.levels:
                if lvl != level:
                    extra.append(cls(lvl, params))
        return no_item, extra, False

    if slice_name == "Augment/Buff":
        classes = sorted(set18buffs.augments)
        return no_item, [getattr(set18buffs, c)() for c in classes], False

    if slice_name == "Wisp":
        classes = sorted(set18buffs.wisps)
        return no_item, [getattr(set18buffs, c)() for c in classes], False

    if slice_name == "Blackthorn":
        # The sweep lives in sim_core and keys off the champion carrying the
        # trait; NoItem still runs for the ratio denominator.
        return no_item, [], True

    return no_item, [], False


def _table_entries(sim_list):
    """Mirror of createSelectorDPSTable, minus pandas."""
    entries = []
    dps_dict = {}
    for idx, sim in enumerate(sim_list):
        entry = {
            "idx": idx,
            "name": sim["Champ"].name,
            "level": sim["Champ"].level,
            "extra": sim["Extra"].name,
            "extraCls": type(sim["Extra"]).__name__,
            # Which breakpoint a trait row is, so the page can colour its icon
            # by tier. Items are not levelled and report None.
            "extraLevel": getattr(sim["Extra"], "level", None),
            "blackthorn": sim.get("Blackthorn"),
        }
        xs, ys = _cumulative_points(sim["Results"])
        entry["dps"] = {str(t): _dps_at(xs, ys, t) for t in DPS_TIMES}
        entries.append(entry)
        key = (entry["name"], entry["level"], entry["extra"])
        dps_dict[key] = {t: entry["dps"][str(t)] for t in DPS_TIMES}

    for entry in entries:
        base = dps_dict.get((entry["name"], entry["level"], "NoItem"))
        own = dps_dict[(entry["name"], entry["level"], entry["extra"])]
        entry["ratio"] = {}
        for t in DPS_TIMES:
            if base is not None:
                entry["ratio"][str(t)] = round(
                    own[t] / base[t] if base[t] != 0 else 0, 2
                )
            else:
                entry["ratio"][str(t)] = 0

    entries.sort(key=lambda e: e["ratio"]["25"], reverse=True)
    return entries


def _timeline(results):
    """Raw per-event series for one trial: the chart and index log data."""
    t, dmg, typ, aspd, mana_cur, mana_full, cum = [], [], [], [], [], [], []
    total = 0.0
    for inst in results:
        total += inst[1][0]
        t.append(inst[0])
        dmg.append(inst[1][0])
        typ.append(inst[1][1])
        aspd.append(inst[2])
        mana_cur.append(inst[3])
        mana_full.append(inst[4])
        cum.append(total)
    return {
        "t": t,
        "dmg": dmg,
        "type": typ,
        "as": aspd,
        "manaCur": mana_cur,
        "manaFull": mana_full,
        "cum": cum,
    }


def run_slice(cfg):
    champ = _build_champion(cfg)
    enemy = _build_enemy(cfg)
    slice_name = cfg.get("slice", "Craftable")
    duration = float(cfg.get("t", 30))
    frame_rate = int(cfg.get("frame_rate", 30))

    items, buffs, want_blackthorn = _slice_inputs(slice_name, cfg)
    kwargs = {}
    if _SUPPORTS_RUN_BLACKTHORN:
        kwargs["run_blackthorn"] = want_blackthorn

    sim_list = sim_core.do_experiment_one_extra(
        champ, enemy, items, buffs, duration, frame_rate, **kwargs
    )

    entries = _table_entries(sim_list)

    # Same display rule as the page: the Blackthorn radio shows only the
    # sacrifice rows (its "None" row is the visible baseline; NoItem stays in
    # the ratio math above but leaves the table). Other slices hide any
    # sacrifice rows a main-style sim_core produced anyway.
    if slice_name == "Blackthorn":
        rows = [e for e in entries if e["extra"].startswith("Blackthorn: ")]
    else:
        rows = [e for e in entries if not e["extra"].startswith("Blackthorn: ")]

    timelines = {
        str(e["idx"]): _timeline(sim_list[e["idx"]]["Results"]) for e in rows
    }
    return {"slice": slice_name, "rows": rows, "timelines": timelines}


# ---------------------------------------------------------------------------
# Champ info / stats panel
# ---------------------------------------------------------------------------

def get_champ_info(cfg):
    # UI hints come from a fresh instance so slider defaults are the champ's
    # own values, not whatever the config already overrode them to.
    fresh = getattr(set18champs, cfg["champ"])(int(cfg["level"]))
    info = {
        "defaultTraits": {
            "classNames": list(fresh.default_traits),
            "displayNames": buff_display_names(fresh.default_traits),
        },
        "numTargets": fresh.num_targets,
        "numExtraTargets": fresh.num_extra_targets,
    }

    # The stat panel shows the configured champion *after* item/buff static
    # stats apply -- write_champion runs on a copy that went through
    # itemStats, and so does this.
    champ = _build_champion(cfg)
    Simulator().itemStats(champ.items, champ)

    def stat(s):
        return {
            "base": s.base,
            "add": s.add,
            "mult": s.mult,
            "stat": s.stat,
            "addMultiplier": getattr(s, "addMultiplier", 1),
        }

    info["stats"] = {
        "atk": stat(champ.atk),
        "bonusAd": stat(champ.bonus_ad),
        "ap": stat(champ.ap),
        "dmgAmp": stat(champ.dmgMultiplier),
        "curMana": champ.curMana,
        "fullMana": champ.fullMana.stat,
        "manaRegen": stat(champ.manaRegen),
        "castTime": champ.castTime,
        "aspd": stat(champ.aspd),
        "crit": stat(champ.crit),
        "critDmg": stat(champ.critDmg),
        "manaPerAttack": stat(champ.manaPerAttack),
        "role": champ.role.value,
        "canSpellCrit": bool(champ.canSpellCrit),
        "notes": champ.notes,
    }
    return info


# ---------------------------------------------------------------------------
# JSON wrappers -- what the worker actually calls
# ---------------------------------------------------------------------------

def catalog_json():
    return json.dumps(get_catalog())


def champ_info_json(config_json):
    return json.dumps(get_champ_info(json.loads(config_json)))


def run_json(config_json):
    return json.dumps(run_slice(json.loads(config_json)))
