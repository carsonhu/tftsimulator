# sim_entry.py
#
# JSON boundary between the static frontend (index.html + app.js) and the Set 19 simulator.
# The v2 page runs this file under Pyodide with *no* installed packages, so
# nothing here (or in anything it imports) may touch streamlit, numpy or
# pandas, so the page boots in a couple of seconds.
#
# Three entry points, each taking/returning JSON strings so the JS side never
# holds a live PyProxy:
#   catalog_json()            -> everything needed to draw the sidebar
#   champ_info_json(config)   -> stat panel + per-champ UI hints for one config
#   run_json(config)          -> table rows + plot timelines for one slice
#
# The config schema is documented on _build_champion. The DPS arithmetic keeps
# the old site's rules (int() truncation above 10, keep-first duplicates).

import datetime
import json
import re
from bisect import bisect_right

import set19buffs
import set19champs
import set19items
import sim_core
from buildstore import list_builds, load_build
from layout import Layout
from helpers import buff_display_map, buff_display_names, item_display_map
from simulator import Simulator

DPS_TIMES = [5, 10, 15, 20, 25]

# Stats a trait's team-wide half could plausibly move. Compared alongside the
# damage vector when deciding whether a team trait's level matters.
_PROBE_STATS = (
    "atk", "bonus_ad", "ap", "aspd", "crit", "critDmg",
    "dmgMultiplier", "manaRegen", "manaPerAttack", "fullMana",
)


def _team_level_matters(cls):
    """Does this trait's team-wide half change with its level?

    For most traits it does not: only the members' own bonus scales, and a
    non-member never gets that. The UI shows a plain on/off checkbox for the
    flat ones and a level picker only where the level actually changes the
    answer.

    Decided by running the trait at each level with the membership flag off
    and comparing what came out, rather than by a hardcoded list, so a trait
    added later is classified correctly without touching this file. The
    reference champion is fixed (first in sorted order) because the question
    is about the trait, not about any particular unit.
    """
    if not set19champs.champ_list:
        return True  # no champion to probe with: show the level picker
    reference = getattr(set19champs, sorted(set19champs.champ_list)[0])
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
                [set19champs.TrainingDummy(1) for _ in range(8)],
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
    "Craftable": lambda: set19items.offensive_craftables,
    "Artifact": lambda: set19items.artifacts,
    "Radiant": lambda: set19items.radiants,
    "Emblem": lambda: set19items.emblems,
}


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def get_catalog():
    champions = []
    for name in sorted(set19champs.champ_list):
        cls = getattr(set19champs, name)
        levels = [1, 2, 3]
        if getattr(cls, "canFourStar", False):
            levels.append(4)
        champions.append({"name": name, "levels": levels})

    def item_group(class_names):
        # item_display_map returns {display: cls} in the order given, and that
        # order is exactly what the sidebar shows -- see all_items below.
        return [
            {"cls": cls, "name": disp, "trait": emblem_traits.get(cls)}
            for disp, cls in item_display_map(class_names).items()
        ]

    # An emblem's trait, so picking one can put that trait in the buff bar.
    # None for every other item. Only traits the buff bar can show are kept.
    emblem_traits = {}
    for cls in set19items.emblems:
        trait = getattr(getattr(set19items, cls)(), "trait", None)
        if trait in set19buffs.class_buffs:
            emblem_traits[cls] = trait

    # Tier order, alphabetical within each tier -- NOT one global sort. The
    # sidebar combo's search filter preserves this order, so typing "spear" or
    # "shojin" surfaces the craftable Spear of Shojin ahead of the Radiant
    # one instead of alphabetically burying it.
    all_items = (
        set19items.no_item
        + sorted(set19items.offensive_craftables)
        + sorted(set19items.artifacts)
        + sorted(set19items.radiants)
        + sorted(set19items.emblems)
    )

    all_buffs = sorted(
        set19buffs.class_buffs
        + set19buffs.augments
        + set19buffs.no_buff
    )
    buffs = []
    for disp, cls_name in buff_display_map(all_buffs).items():
        cls = getattr(set19buffs, cls_name)
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
    # Three shapes qualify, all discovered from the classes rather than listed
    # by name, so a trait added later turns up here on its own.
    #
    #   * an "Is X" 0/1 membership flag. Passing 0 is what "my team has this
    #     trait but this champion isn't one of them" means -- the team-wide
    #     half applies, the member-only half doesn't.
    #   * a named choice (Illbeats' mix): a real question rather than a flag
    #     to zero, so the panel has to ask it.
    #   * tick boxes (Heartsteel's fielded members), below.
    team_buffs = []
    for cls_name in set19buffs.class_buffs:
        cls = getattr(set19buffs, cls_name)
        # team_trait = False opts a trait out even though its parameter shape
        # would qualify: Hitmaker's "Is Big Shot" is a champion-specific
        # question, not team membership.
        if not getattr(cls, "team_trait", True):
            continue
        try:
            extra = cls.extraParameters()
        except Exception:
            continue
        if not extra:
            continue
        options = extra.get("Options")
        # Tick boxes (Heartsteel's fielded members): the team-wide half is what
        # the ticked facts give, so the panel asks them. TeamFlags limits the
        # panel to the leading flags that matter to a non-member (not "Bias").
        flags = extra.get("Flags")
        if not options and not flags and (extra.get("Min"), extra.get("Max")) != (0, 1):
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
                # A list -> the panel shows these tick boxes and passes the bits.
                "flags": list(flags[: extra.get("TeamFlags", len(flags))]) if flags else None,
                "paramDefault": extra.get("Default", 0),
                # False -> the UI shows a checkbox and uses onLevel; True ->
                # it shows a level picker.
                "scales": scales,
                "onLevel": next((l for l in levels if l > 0), 0),
            }
        )

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
        ],
        # Client builds the numbers can come from (builds/index.json, newest first); the page sends the chosen
        # version as cfg["build"] and the worker loads that file into Pyodide before the run (B9).
        "builds": [_build_option(b) for b in list_builds()],
        "defaults": {
            "enemy": {"hp": 1800, "armor": 100, "mr": 100},
            "stages": ["2-1", "3-1", "4-1", "5-1", "6-1"],
            "stageDefault": "4-1",
            "tactician": {"min": 3, "max": 10, "default": 4},
            "frameRates": [30],  # the game runs at 30 Hz (T1)
            "duration": 30,
            "numItems": 3,
            "numBuffs": {"min": 1, "max": 10, "default": 2},
            "layout": {"adjacent": Layout().adjacent, "two_hex": Layout().two_hex},
        },
        "dpsTimes": DPS_TIMES,
    }


# ---------------------------------------------------------------------------
# Config -> live objects
# ---------------------------------------------------------------------------

def _build_champion(cfg):
    """The champion a config describes, with the sidebar's settings applied in its order.

    cfg = {
      "champ": "Ahri", "level": 1,
      "layout": {"adjacent": 1, "two_hex": 1},     # enemies next to the target / 2 hexes from it (layout.py)
      "takedowns": 0,
      "bonus": {"ad","ap","as","manaregen","mpa","dmgamp","crit","critdmg"},
      "stage": "4-1", "tactician_level": 4,
      "build": "<version>"|null,                   # client build (default: newest)
      "items": ["NoItem","NoItem","NoItem"],       # class names
      "buffs": [["Encore", 2, 0], ...],            # (class, level, params)
      "enemy": {"hp","armor","mr"},
      "frame_rate": 30, "t": 30, "slice": "Craftable",
    }
    """
    champ = _champion_class(cfg)(int(cfg["level"]), build=_build(cfg))

    champ.takedowns = int(cfg.get("takedowns", 0))

    # The page's + boxes, in its units: AD, AP, AS, damage amp, crit and crit damage in percent, mana as numbers.
    # Each becomes a Channel1 modifier in game units (AS: MultiplyAdditive, the rest added).
    bonus = cfg.get("bonus", {})
    for attr, key, per in (("bonus_ad", "ad", 100), ("ap", "ap", 100), ("manaRegen", "manaregen", 1),
                           ("manaPerAttack", "mpa", 1), ("dmgMultiplier", "dmgamp", 100), ("crit", "crit", 100),
                           ("critDmg", "critdmg", 100)):
        v = float(bonus.get(key, 0))
        if v:
            getattr(champ, attr).modify("+", v / per)
    if float(bonus.get("as", 0)):
        champ.aspd.modify("MultiplyAdditive", 1 + float(bonus["as"]) / 100)

    stage = cfg.get("stage", "4-1")
    champ.stage = int(str(stage).split("-")[0])
    champ.tactician_level = int(cfg.get("tactician_level", 4))

    for item_cls in cfg.get("items", []):
        if item_cls and item_cls != "NoItem":
            champ.items.append(getattr(set19items, item_cls)())
            champ.item_count += 1

    for name, level, params in cfg.get("buffs", []):
        if name != "NoBuff":
            champ.items.append(getattr(set19buffs, name)(level, params))

    return champ


def _build(cfg):
    return load_build(cfg.get("build") or None)


def _build_option(b):
    """A builds/index.json entry -> {version, label} for the build picker, e.g. 'PBE 19.1 #5973071 (Nov 17 13:28)'."""
    v = b["version"]
    m = re.match(r"rls-(\d+\.\d+)\.\d+\.(\d+)", v)
    name = f"{m.group(1)} #{m.group(2)}" if m else v
    when = ""
    if b.get("pak_mtime"):
        d = datetime.datetime.fromisoformat(b["pak_mtime"])
        when = f" ({d.strftime('%b')} {d.day} {d.strftime('%H:%M')})"
    return {"version": v, "label": f"{b.get('install') or ''} {name}{when}".strip()}


def _champion_class(cfg):
    if cfg["champ"] not in set19champs.champ_list:
        raise KeyError(f'{cfg["champ"]} is not a Set 19 champion in set19champs.champ_list')
    return getattr(set19champs, cfg["champ"])


def _layout(cfg):
    """Where the dummies stand: the page's 'Enemies next to the target' and 'Enemies 2 hexes away' (layout.py)."""
    lay = cfg.get("layout") or {}
    default = Layout()
    return Layout(int(lay.get("adjacent", default.adjacent)), int(lay.get("two_hex", default.two_hex)))


def _build_enemy(cfg):
    enemy_cfg = cfg.get("enemy", {})
    enemy = set19champs.TrainingDummy(1)
    enemy.hp.base = float(enemy_cfg.get("hp", 1800))
    enemy.armor.base = float(enemy_cfg.get("armor", 100))
    enemy.mr.base = float(enemy_cfg.get("mr", 100))
    return enemy


# ---------------------------------------------------------------------------
# DPS math
# ---------------------------------------------------------------------------

def _cumulative_points(results):
    """(times, cumulative damage), duplicates collapsed to first occurrence.

    Cumulative damage in event order, keeping the *first* value per duplicate
    timestamp (the old site's rule); results arrive chronological so no sort is
    needed, but the keep-first rule matters on frames with several damage
    instances.
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
    # Big numbers lose the fraction. The truncated value also feeds the ratio columns, so this is
    # arithmetic, not just formatting.
    if res > 10:
        res = int(res)
    return res


# ---------------------------------------------------------------------------
# Slices and rows
# ---------------------------------------------------------------------------

def _champion_specific_flag(cls):
    """True when a buff's 0/1 parameter asks about *this champion*.

    The Team Traits panel discovers the mirror image of this: 0/1 params that
    ask whether the board runs a trait this champion is not a member of. A
    trait setting team_trait = False has opted out of that panel precisely
    because its flag is not about membership -- Hitmaker's is whether this
    unit is the Big Shot, a fact about the unit in front of you.

    That opt-out left those toggles with nowhere at all to be explored: not in
    Team Traits, and not in the level sweep, which holds params fixed. So the
    Trait slice picks them up, and "is this the Big Shot?" becomes a row you
    can compare against instead of a checkbox you have to flip and re-run.
    """
    if getattr(cls, "team_trait", True):
        return False
    try:
        extra = cls.extraParameters()
    except Exception:
        return False
    if not extra or extra.get("Options"):
        return False
    return (extra.get("Min"), extra.get("Max")) == (0, 1)


def trait_sweep_buffs(buff_specs):
    """The buff rows the Trait slice runs, for a bar of (name, level, params)."""
    extra = []
    for name, level, params in buff_specs:
        cls = getattr(set19buffs, name)
        # Every *other* level of the buff, at the flag it is already on.
        for lvl in cls.levels:
            if lvl != level:
                extra.append(cls(lvl, params))
        # And for a champion-specific flag like Hitmaker's Big Shot, the
        # same levels with the flag flipped, so what the flag is worth is a
        # row you can read off against the others rather than something you
        # have to toggle and re-run to see.
        if _champion_specific_flag(cls):
            flipped = 0 if params else 1
            for lvl in cls.levels:
                # Level 0 is the trait switched off, where the flag changes
                # nothing: Buff.ability() returns before performAbility ever
                # sees it. A flipped level-0 row would duplicate the one just
                # added, differing only in a name that claims otherwise.
                if lvl != 0:
                    extra.append(cls(lvl, flipped))
    return extra


def _slice_inputs(slice_name, cfg):
    """(item objects, buff objects) for one radio option.

    Every slice carries NoItem because the "Extra DPS" columns are ratios
    against that row.
    """
    no_item = [set19items.NoItem()]

    if slice_name in _ITEM_SLICES:
        classes = list(_ITEM_SLICES[slice_name]())
        return [getattr(set19items, c)() for c in classes] + no_item, []

    if slice_name == "Trait":
        return no_item, trait_sweep_buffs(cfg.get("buffs", []))

    if slice_name == "Augment/Buff":
        classes = sorted(set19buffs.augments)
        return no_item, [getattr(set19buffs, c)() for c in classes]

    return no_item, []


def _table_entries(sim_list):
    """One row per trial: DPS at each time and the ratio against the NoItem row."""
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

    items, buffs = _slice_inputs(slice_name, cfg)
    sim_list = sim_core.do_experiment_one_extra(champ, enemy, items, buffs, duration, frame_rate,
                                                layout=_layout(cfg))
    rows = _table_entries(sim_list)

    timelines = {
        str(e["idx"]): _timeline(sim_list[e["idx"]]["Results"]) for e in rows
    }
    return {"slice": slice_name, "rows": rows, "timelines": timelines}


# ---------------------------------------------------------------------------
# Champ info / stats panel
# ---------------------------------------------------------------------------

def _panel(attr, kind="flat"):
    """How the Base stats panel writes an attribute (base, bonus, total), in the panel's units: AD and AP in points
    of 100 with Deathblade / Rabadon's factor on the bonus (addMultiplier), attack speed's bonus in percent, the rest
    as they are. Only Channel1 bonuses are shown; the total is the attribute's value."""
    ma = attr.total("MultiplyAdditive")
    view = {"stat": attr.stat, "mult": attr.total("MultiplyCompound", 2), "addMultiplier": 1}
    if kind == "multiplier":
        view.update(base=100, add=attr.total("+") * 100, addMultiplier=1 + ma)
    elif kind == "aspd":
        view.update(base=attr.base, add=ma * 100)
    else:
        view.update(base=attr.base, add=attr.total("+"))
    return view


def get_champ_info(cfg):
    # UI hints come from a fresh instance so the default traits are the champ's
    # own, not whatever the config already holds.
    fresh = _champion_class(cfg)(int(cfg["level"]), build=_build(cfg))
    info = {
        "defaultTraits": {
            "classNames": list(fresh.default_traits),
            "displayNames": buff_display_names(fresh.default_traits),
        },
    }

    # The stat panel shows the configured champion *after* item/buff static
    # stats apply -- write_champion runs on a copy that went through
    # itemStats, and so does this.
    champ = _build_champion(cfg)
    Simulator().itemStats(champ.items, champ)

    info["stats"] = {
        "atk": _panel(champ.atk),
        "bonusAd": _panel(champ.bonus_ad, "multiplier"),
        "ap": _panel(champ.ap, "multiplier"),
        "dmgAmp": _panel(champ.dmgMultiplier),
        "curMana": champ.curMana,
        "fullMana": champ.fullMana.stat,
        "manaRegen": _panel(champ.manaRegen),
        "castTime": champ.timing.cast_lock,  # cast start -> next attack (T5), from the build
        "aspd": _panel(champ.aspd, "aspd"),
        "crit": _panel(champ.crit),
        "critDmg": _panel(champ.critDmg),
        "manaPerAttack": _panel(champ.manaPerAttack),
        "role": champ.role.value if champ.role else None,
        "build": champ.build.version if getattr(champ, "build", None) else None,
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
