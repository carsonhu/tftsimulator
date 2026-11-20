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
#   trace_json(config)        -> one row's fight, tick by tick, for the fight viewer
#
# The config schema is documented on _build_champion. The DPS arithmetic keeps
# the old site's rules (int() truncation above 10, keep-first duplicates).

import datetime
import json
import math
import re

import set19buffs
import set19champs
import set19items
import sim_core
from buildstore import list_builds, load_build
from layout import MAX_TARGETS, TARGETS, Layout
from helpers import buff_display_map, buff_display_names, item_display_map
from simulator import Simulator

# The table's DPS columns (owner, 2026-11-18): the average DPS over fights ending anywhere in each window (s), not at
# one instant, so a cast landing just after a column's time no longer swings it. Most fights end between 20 and 30 s;
# 10-20 s shows ramp-up. The last window is the headline: rows are sorted by it and the DPS ÷ NoItem ratio is read there.
DPS_WINDOWS = [(10, 20), (20, 30)]
HEADLINE = "20-30"


def _window_key(window):
    return f"{window[0]}-{window[1]}"

# Stats a trait's team-wide half could plausibly move. Compared alongside the
# damage vector when deciding whether a team trait's level matters.
_PROBE_STATS = (
    "atk", "bonus_ad", "ap", "aspd", "crit", "critDmg",
    "dmgMultiplier", "manaRegen", "manaPerAttack", "fullMana",
)


_TEAM_LEVEL_MATTERS = {}


def _team_level_matters(cls):
    """Does this trait's team-wide half change with its level? (Probed once per class: the catalog and the Team
    Traits slice both ask.)"""
    if cls.__name__ not in _TEAM_LEVEL_MATTERS:
        _TEAM_LEVEL_MATTERS[cls.__name__] = _probe_team_level(cls)
    return _TEAM_LEVEL_MATTERS[cls.__name__]


def _probe_team_level(cls):
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

def _cost(cls, build):
    """The champion's shop cost in the build; a hero augment unit (cost 0) takes its base unit's (BASE_KEY)."""
    cost = build.champion(cls.KEY).d.get("cost") or 0
    if not cost and getattr(cls, "BASE_KEY", None):
        cost = build.champion(cls.BASE_KEY).d.get("cost") or 0
    return cost


def get_catalog():
    champions = []
    build = load_build()
    for name in sorted(set19champs.champ_list):
        cls = getattr(set19champs, name)
        levels = [1, 2, 3]
        if getattr(cls, "canFourStar", False):
            levels.append(4)
        # label: what the page shows (a hero augment unit is "Olaf (Hero)"); name: the class. A champion with forms
        # (Seraphine) is listed once in the menu: each form names the class it is a form of (variantOf, a parent class
        # in champ_list) and its mode, which the page offers as a switch once she's chosen (owner, 2026-11-19).
        parent = next((b.__name__ for b in cls.__mro__[1:] if b.__name__ in set19champs.champ_list), None)
        champions.append({"name": name, "label": getattr(cls, "display_name", name), "levels": levels,
                          "area": bool(getattr(cls, "AREA", False)), "cost": _cost(cls, build),
                          # the Targets buttons it gets (layout.py): its cap, and how its enemies stand
                          "targetsMax": getattr(cls, "TARGETS_MAX", MAX_TARGETS),
                          "targetsDefault": getattr(cls, "TARGETS_DEFAULT", TARGETS),
                          "targetsShape": getattr(cls, "TARGETS_SHAPE", "cluster"),
                          "variantOf": parent, "mode": getattr(cls, "MODE", None)})
    # the menu's order (owner, 2026-11-18): by cost, then name; the page opens on the first by name, as before
    default_champion = champions[0]["name"] if champions else None
    champions.sort(key=lambda c: (c["cost"], c["label"].lower()))

    def item_group(class_names):
        # item_display_map returns {display: cls} in the order given, and that
        # order is exactly what the sidebar shows -- see all_items below.
        # kind: the picker's section (the table's slice names, None for NoItem).
        return [
            {"cls": cls, "name": disp, "trait": emblem_traits.get(cls), "kind": item_kinds.get(cls)}
            for disp, cls in item_display_map(class_names).items()
        ]

    item_kinds = {}
    for kind, class_names in (("Craftable", set19items.offensive_craftables), ("Artifact", set19items.artifacts),
                              ("Radiant", set19items.radiants), ("Emblem", set19items.emblems)):
        for cls in class_names:
            item_kinds.setdefault(cls, kind)

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
                # the picker's section: Trait, Augment, or None (NoBuff)
                "kind": "Trait" if cls_name in set19buffs.class_buffs
                else "Augment" if cls_name in set19buffs.augments else None,
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
    #
    # And any trait that says team_trait = True: its effects reach units outside
    # it by membership alone (Arcanist's team AP, Swiftstriker's team AS), with
    # no question to ask, or a count to give (Composer's instruments, Jazz's
    # active traits) (owner, 2026-11-19).
    team_buffs = []
    for cls_name in set19buffs.class_buffs:
        cls = getattr(set19buffs, cls_name)
        # team_trait = False opts a trait out even though its parameter shape
        # would qualify: Hitmaker's "Is Big Shot" is a champion-specific
        # question, not team membership.
        declared = getattr(cls, "team_trait", None)
        if declared is False:
            continue
        try:
            extra = cls.extraParameters() or {}
        except Exception:
            continue
        if not extra and declared is not True:
            continue
        options = extra.get("Options")
        # Tick boxes (Heartsteel's fielded members): the team-wide half is what
        # the ticked facts give, so the panel asks them. TeamFlags limits the
        # panel to the leading flags that matter to a non-member (not "Bias").
        flags = extra.get("Flags")
        is_flag = (extra.get("Min"), extra.get("Max")) == (0, 1)
        if declared is not True and not options and not flags and not is_flag:
            continue
        # a count the team-wide half reads (Composer's instruments): the panel asks it in a number box
        number = ({"min": extra.get("Min", 0), "max": extra.get("Max"), "default": extra.get("Default", 0)}
                  if extra and not options and not flags and not is_flag else None)
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
                "paramTitle": extra.get("Title"),
                # None -> the param is the 0/1 flag and the panel passes 0.
                # A list -> the panel offers these and passes the index.
                "options": list(options) if options else None,
                # A list -> the panel shows these tick boxes and passes the bits.
                "flags": list(flags[: extra.get("TeamFlags", len(flags))]) if flags else None,
                # {min, max, default} -> the panel shows a number box and passes its value.
                "number": number,
                "paramDefault": extra.get("Default", 0),
                # False -> the UI shows a checkbox and uses onLevel; True ->
                # it shows a level picker.
                "scales": scales,
                "onLevel": next((l for l in levels if l > 0), 0),
            }
        )

    return {
        "champions": champions,
        "defaultChampion": default_champion,
        "sidebarItems": item_group(all_items),
        "buffs": buffs,
        "teamBuffs": team_buffs,
        "slices": [
            "Craftable",
            "Artifact",
            "Radiant",
            "Emblem",
            "Trait",
            "Team Traits",
            "Augment/Buff",
        ],
        # Client builds the numbers can come from (builds/index.json, newest first); the page sends the chosen
        # version as cfg["build"] and the worker loads that file into Pyodide before the run (B9).
        "builds": [_build_option(b) for b in list_builds()],
        "defaults": {
            "enemy": {"hp": 1800, "armor": 100, "mr": 100},
            "stages": ["2-1", "3-1", "4-1", "5-1", "6-1"],
            "stageDefault": "4-1",
            "frameRates": [30],  # the game runs at 30 Hz (T1)
            "duration": 30,
            "numItems": 3,
            "numBuffs": {"min": 1, "max": 10, "default": 2},
            "layout": {"targets": TARGETS, "max": MAX_TARGETS},
            "traceSeconds": list(TRACE_SECONDS),
        },
        "dpsWindows": [{"key": _window_key(w), "label": f"{w[0]}–{w[1]} s"} for w in DPS_WINDOWS],
        "headline": HEADLINE,
    }


# ---------------------------------------------------------------------------
# Config -> live objects
# ---------------------------------------------------------------------------

def _build_champion(cfg):
    """The champion a config describes, with the sidebar's settings applied in its order.

    cfg = {
      "champ": "Ahri", "level": 1,
      "layout": {"targets": 3},                    # the target and the enemies next to it (layout.py; AREA champions)
      "takedowns": 0,
      "bonus": {"ad","ap","as","manaregen","mpa","dmgamp","crit","critdmg"},
      "stage": "4-1",
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
    elif b.get("label"):  # a build made from patch notes (B33): the base's numbers with the notes' changes
        d = datetime.date.fromisoformat(b["date"]) if b.get("date") else None
        when = f" ({b['label']}{', ' + d.strftime('%b') + ' ' + str(d.day) if d else ''})"
    return {"version": v, "label": f"{b.get('install') or ''} {name}{when}".strip()}


def _champion_class(cfg):
    if cfg["champ"] not in set19champs.champ_list:
        raise KeyError(f'{cfg["champ"]} is not a Set 19 champion in set19champs.champ_list')
    return getattr(set19champs, cfg["champ"])


def _layout(cfg):
    """Where the dummies stand: the page's 'Number of targets' (layout.py), for a champion whose damage depends on it
    (AREA); any other gets the default, as the page shows it no slider."""
    cls = _champion_class(cfg)
    if not getattr(cls, "AREA", False):
        return Layout()
    # the champion's own cap and shape (TARGETS_MAX, TARGETS_SHAPE: Jhin's line of 3, owner 2026-11-19)
    asked = (cfg.get("layout") or {}).get("targets", getattr(cls, "TARGETS_DEFAULT", TARGETS))
    targets = min(int(asked), getattr(cls, "TARGETS_MAX", MAX_TARGETS))
    return Layout(targets, getattr(cls, "TARGETS_SHAPE", "cluster"))


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

def _dps_window(results, a, b):
    """The average of (damage dealt by T) / T over fight end times T spread evenly over [a, b] (a > 0): every hit
    counts, a hit at t weighing ln(b / max(t, a)) / (b - a): fully before the window, about the share of the window
    after it inside, nothing after b. Exact: damage dealt by T is a step in T."""
    total = 0.0
    for inst in results:
        t = float(inst[0])
        if t <= b + 1e-9:
            total += inst[1][0] * math.log(b / max(t, a))
    res = total / (b - a)
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


def _labelled(cls, rows):
    """Buff objects for a trait's own sweep_rows [(level, params, label)]."""
    out = []
    for lvl, params, label in rows:
        buff = cls(lvl, params)
        buff.row_label = label
        out.append(buff)
    return out


def trait_sweep_buffs(buff_specs, champ_key=None):
    """The buff rows the Trait slice runs, for a bar of (name, level, params). A trait that knows which of its rows
    matter (`sweep_rows`: Heartsteel) gives them itself."""
    extra = []
    for name, level, params in buff_specs:
        cls = getattr(set19buffs, name)
        if hasattr(cls, "sweep_rows"):
            extra += _labelled(cls, cls.sweep_rows(level, params, member=True, champ_key=champ_key))
            continue
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


def team_sweep_buffs(team_specs):
    """The rows the Team Traits slice runs, for the panel's (name, level, params): only what changes a non-member.

    * Heartsteel (tick boxes): each member fielded or not, one row per tick box flipped ("Heartsteel (+Kayn)"); the
      level itself changes nothing for a non-member.
    * a trait whose team-wide half steps per breakpoint (Arcanist, Illbeats; `_team_level_matters`): its other levels.
    * one whose team-wide half is the same at every breakpoint (Swiftstriker, Prodigy, Composer): only the other
      state, "Swiftstriker 0" when it is on, "Swiftstriker" when it is off.
    """
    rows = []
    for name, level, params in team_specs:
        cls = getattr(set19buffs, name)
        extra = cls.extraParameters() or {}
        on_level = next((lvl for lvl in cls.levels if lvl), 0)
        title = getattr(cls, "display_name", name)
        flags = extra.get("Flags")
        if hasattr(cls, "sweep_rows"):
            rows += _labelled(cls, cls.sweep_rows(level, params, member=False))
        elif flags:
            for bit, flag in enumerate(flags[: extra.get("TeamFlags", len(flags))]):
                flipped = int(params or 0) ^ (1 << bit)
                row = cls(level or on_level, flipped)
                row.row_label = f"{title} ({'+' if (flipped >> bit) & 1 else '-'}{flag})"
                rows.append(row)
        elif extra.get("Options") or _team_level_matters(cls):
            rows += [cls(lvl, params) for lvl in cls.levels if lvl != level]
        elif level:
            row = cls(0, params)
            row.row_label = f"{title} 0"
            rows.append(row)
        else:
            row = cls(on_level, params)
            row.row_label = title
            rows.append(row)
    return rows


def _slice_inputs(slice_name, cfg):
    """(item objects, buff objects) for one radio option.

    Every slice carries NoItem because the "DPS ÷ NoItem" columns are ratios
    against that row.
    """
    no_item = [set19items.NoItem()]

    # A row's own number, typed into the table (Hold the Line's units, Comeback Story's Health, Cappa Juice's
    # takedowns): cfg["rowInputs"] by class, else the parameter's default (Cappa Juice: the page's takedowns).
    typed = cfg.get("rowInputs") or {}

    if slice_name in _ITEM_SLICES:
        items = []
        for c in _ITEM_SLICES[slice_name]():
            item = getattr(set19items, c)()
            if _row_input_spec(item):
                item.row_value = int(typed.get(c, cfg.get("takedowns", 0)))
            items.append(item)
        return items + no_item, []

    # The page sends its Team Traits panel's traits merged into "buffs" and names them in "team": the Trait slice
    # sweeps the champion's own buff bar, the Team Traits slice those (owner, 2026-11-19).
    team = set(cfg.get("team") or [])
    if slice_name == "Trait":
        champ_cls = getattr(set19champs, cfg.get("champ") or "", None)
        return no_item, trait_sweep_buffs([b for b in cfg.get("buffs", []) if b[0] not in team],
                                          champ_key=getattr(champ_cls, "KEY", None))

    if slice_name == "Team Traits":
        return no_item, team_sweep_buffs([b for b in cfg.get("buffs", []) if b[0] in team])

    if slice_name == "Augment/Buff":
        buffs = []
        for c in sorted(set19buffs.augments):
            cls = getattr(set19buffs, c)
            spec = _row_input_spec(cls)
            buffs.append(cls(1, int(typed.get(c, spec["Default"]))) if spec else cls())
        return no_item, buffs

    return no_item, []


def _row_input_spec(extra):
    """The number a row takes in the table, if any: a buff's parameter that says how its row reads ("Row": "{} units")
    or an item's ROW_INPUT. Accepts a class or an instance."""
    cls = extra if isinstance(extra, type) else type(extra)
    spec = getattr(cls, "ROW_INPUT", None)
    if spec:
        return spec
    try:
        extra_params = cls.extraParameters() if issubclass(cls, set19buffs.Buff) else None
    except Exception:
        return None
    return extra_params if isinstance(extra_params, dict) and extra_params.get("Row") else None


def _row_input(extra):
    """{value, min, max, template} for the table's inline box ("Hold the Line ([7] units)"), or None."""
    spec = _row_input_spec(extra)
    if not spec:
        return None
    value = extra.params if isinstance(extra, set19buffs.Buff) else extra.row_value
    return {"value": int(value or 0), "min": spec.get("Min", 0), "max": spec.get("Max", 999),
            "template": spec["Row"], "title": spec.get("Title", "")}


def _row_label(extra):
    """The row's name: an item's or augment's own; a trait's with its level ("Trickshot 3"), and with its 0/1 flag
    when the Trait slice runs it both ways (Hitmaker's Big Shot: "Hitmaker 2 (Is Big Shot: no)")."""
    if getattr(extra, "row_label", None):  # a Team Traits row names itself ("Heartsteel (+Kayn)", "Swiftstriker 0")
        return extra.row_label
    typed = _row_input(extra)
    if typed:  # "Hold the Line (7 units)": the page draws the number as a box
        return f"{extra.name} ({typed['template'].format(typed['value'])})"
    cls = type(extra)
    levels = [lvl for lvl in getattr(cls, "levels", []) if lvl]
    if not isinstance(extra, set19buffs.Buff) or len(levels) < 2:
        return extra.name
    label = f"{extra.name} {extra.level}"
    if _champion_specific_flag(cls):
        label += f" ({cls.extraParameters().get('Title', 'Flag')}: {'yes' if extra.params else 'no'})"
    return label


def _row_params(extra):
    p = getattr(extra, "params", None)
    return p if isinstance(p, (int, float)) and not isinstance(p, bool) else None


def _table_entries(sim_list):
    """One row per trial: DPS over each window (DPS_WINDOWS) and the ratio against the NoItem row (each row's own
    numbers: rows can share a name, e.g. a trait at several levels)."""
    entries = []
    for idx, sim in enumerate(sim_list):
        entry = {
            "idx": idx,
            "name": sim["Champ"].name,
            "level": sim["Champ"].level,
            "extra": _row_label(sim["Extra"]),
            "extraCls": type(sim["Extra"]).__name__,
            # Which breakpoint a trait row is, so the page can colour its icon
            # by tier. Items are not levelled and report None.
            "extraLevel": getattr(sim["Extra"], "level", None),
            # a buff row's parameter (Hitmaker's Is Big Shot, Heartsteel's ticked units), so the page can add the
            # row to the setup exactly as it ran; None for items
            "extraParams": _row_params(sim["Extra"]),
            # the row's own number, which the page draws as a box in the name (_row_input); None for most rows
            "input": _row_input(sim["Extra"]),
        }
        entry["dps"] = {_window_key(w): _dps_window(sim["Results"], *w) for w in DPS_WINDOWS}
        entries.append(entry)

    for entry in entries:
        base = next((e["dps"] for e in entries if (e["name"], e["level"], e["extra"])
                     == (entry["name"], entry["level"], "NoItem")), None)
        own = entry["dps"]
        entry["ratio"] = {}
        for t in entry["dps"]:
            if base is not None:
                entry["ratio"][t] = round(own[t] / base[t] if base[t] != 0 else 0, 2)
            else:
                entry["ratio"][t] = 0

    entries.sort(key=lambda e: e["ratio"][HEADLINE], reverse=True)
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
    duration = max(float(cfg.get("t", 30)), DPS_WINDOWS[-1][1])  # the fight runs at least to the last window's end
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
# The fight viewer
# ---------------------------------------------------------------------------

TRACE_SECONDS = (30, 60, 90)


def run_trace(cfg):
    """One table row's fight, recorded tick by tick for the page's fight viewer (fight_trace.Tracer).

    cfg is a run config plus "row": the row's idx in its slice (sim_core's order: the slice's items, then its buffs)
    and "seconds": the fight's length (TRACE_SECONDS). The fight is the very one the row's numbers come from."""
    from fight_trace import Tracer

    champ = _build_champion(cfg)
    enemy = _build_enemy(cfg)
    items, buffs = _slice_inputs(cfg.get("slice", "Craftable"), cfg)
    idx = int(cfg.get("row", len(items) - 1))  # default: NoItem, the last item
    extras = [(x, False) for x in items] + [(x, True) for x in buffs]
    extra, is_buff = extras[idx]
    seconds = float(cfg.get("seconds", TRACE_SECONDS[0]))
    holder = {}

    def attach(c, dummies):
        c.tracer = holder["tracer"] = Tracer(c, dummies)

    c, results = sim_core.run_one(champ, enemy, extra, is_buff, seconds, int(cfg.get("frame_rate", 30)),
                                  _layout(cfg), setup=attach)
    out = holder["tracer"].to_dict(math.ceil(seconds * 30 - 1e-9))
    out["extra"] = _row_label(extra)
    out["champion"] = {"cls": cfg["champ"], "label": getattr(type(c), "display_name", c.name), "level": c.level,
                       "range": c.attack_range}
    out["enemy"] = {"hp": enemy.hp.stat, "armor": enemy.armor.stat, "mr": enemy.mr.stat}
    return out


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
        # crit chance over 1 is crit damage instead (champion.critDamage): the panel shows the cap and the sum
        "excessCritRatio": champ.excess_crit_ratio,
        "manaPerAttack": _panel(champ.manaPerAttack),
        "role": champ.role.name if champ.role else None,  # the game's display name ('Magic Caster')
        "build": champ.build.version if getattr(champ, "build", None) else None,
        "canSpellCrit": bool(champ.canSpellCrit),
        "notes": champ.notes,
    }
    return info


# ---------------------------------------------------------------------------
# Cards: the in-game text of every item, augment and trait the page can show
# ---------------------------------------------------------------------------

def _stat_part(token):
    m = re.fullmatch(r"([-+]?[\d.]+%?)([A-Za-z]\w*)?", token)
    return [m.group(1), m.group(2)] if m else [token, None]


def _tag_tier(text, cls):
    """A tier line whose numbers carry no stat tag in the build ("(2) 1.5% , 1%"): the class's TIER_TAGS appended to
    them in order ("1.5%Health , 1%DamageAmp"), so the card draws their glyphs as it does "12%AP"."""
    tags = list(getattr(cls, "TIER_TAGS", ()) or ())
    if not tags:
        return text
    return re.sub(r"(?<=\d%)(?![A-Za-z])", lambda m: tags.pop(0) if tags else "", text, count=len(tags))


# A tooltip's placeholders the game fills in live (counters, its own calc slots, localisation keys): a card shows
# none of them (owner, 2026-11-19: "Current Hats: (live)").
_PLACEHOLDER = r"(?:⟨[^⟩]*⟩|\{[^}]*\}|<[^>]*>|\[[^\]]*\?\])"
# a line that is only a label and a placeholder ("Current Hats: <live>", "Gold collected: <live>Coin"): dropped
_PLACEHOLDER_LINE = re.compile(r"^[^\n:]*:[ \t]*" + _PLACEHOLDER + r"\w*[ \t]*$", re.M)
# a parenthesis around one ("(Total: <live>)"): dropped
_PLACEHOLDER_PAREN = re.compile(r"\s*\([^()]*" + _PLACEHOLDER + r"[^()]*\)")


def _clean_card_text(text):
    """A tooltip without the placeholders only the game can fill in: label-and-placeholder lines and parentheses
    around one go, any other placeholder is cut out, and the blank lines left behind collapse."""
    text = _PLACEHOLDER_LINE.sub("", text)
    text = _PLACEHOLDER_PAREN.sub("", text)
    text = re.sub(_PLACEHOLDER, "", text)
    text = re.sub(r"[ \t]+\n", "\n", re.sub(r"[ \t]{2,}", " ", text))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def get_cards(cfg):
    """{class name: card} for every item and buff class with a build key: the build's name, kind (item kind, augment
    tier or trait kind), stat line, text and (traits) breakpoints, all from the selected build. The page shows one
    when a row or a menu entry is hovered. The stat line is [[value, tag], ...]: "15%AD" -> ["15%", "AD"], the tag
    the client's rich-text icon (icons/stats/<tag>.png, lower-cased); None when the line has no icon ("250")."""
    build = _build(cfg)
    cards = {}
    for module, group in ((set19items, "items"), (set19buffs, "augments"), (set19buffs, "traits")):
        for name, cls in vars(module).items():
            key = getattr(cls, "KEY", None) if isinstance(cls, type) else None
            entry = build.data[group].get(key) if isinstance(key, str) else None
            if entry is None or name in cards:
                continue
            cards[name] = {
                "key": key,
                "name": entry.get("name") or key,
                "kind": entry.get("kind") or entry.get("tier") or "",
                "stats": [_stat_part(s) for s in (entry.get("stat_text") or "").split()],
                "text": _clean_card_text(entry.get("text") or ""),
                "tiers": [{"threshold": t.get("threshold"), "text": _tag_tier(_clean_card_text(t.get("text") or ""), cls)}
                          for t in entry.get("tiers") or []],
            }
            # what the simulator knows that the tooltip doesn't say: CARD_NOTE = (tag, text), e.g. Comeback Story's
            # [Multiplicative]
            note = getattr(cls, "CARD_NOTE", None)
            if note:
                cards[name]["note"] = {"tag": note[0], "text": note[1]}
            # a team trait's card in Team Traits: only what reaches a non-member (BuildTrait.team_card)
            if group == "traits" and hasattr(cls, "team_card"):
                try:
                    cards[name]["team"] = cls.team_card(build)
                except Exception:  # a build without one of its rows: the full card still shows
                    pass
    return cards


# ---------------------------------------------------------------------------
# JSON wrappers -- what the worker actually calls
# ---------------------------------------------------------------------------

def catalog_json():
    return json.dumps(get_catalog())


def champ_info_json(config_json):
    return json.dumps(get_champ_info(json.loads(config_json)))


def run_json(config_json):
    return json.dumps(run_slice(json.loads(config_json)))


def cards_json(config_json):
    return json.dumps(get_cards(json.loads(config_json)))


def trace_json(config_json):
    return json.dumps(run_trace(json.loads(config_json)), separators=(",", ":"))
