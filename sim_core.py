# sim_core.py

import copy
from typing import Any, Dict, List

from set19buffs import class_buffs
from layout import Layout
from simulator import Simulator


class ChampLabel:
    """The two fields a result row's champion is ever asked for.

    Each row used to carry its whole post-combat Champion -- item graph,
    effects and all -- but the only consumer (sim_entry._table_entries)
    reads only .name and .level.

    The cost of the trim is diagnostic -- per-row final stacks, effects and
    numCasts are gone. Per-instant AS and mana survive in Results, whose
    entries are (time, damage, aspd, curMana, fullMana).
    """

    __slots__ = ("name", "level")

    def __init__(self, name, level):
        self.name = name
        self.level = level

    def __repr__(self):
        return f"ChampLabel({self.name!r}, {self.level!r})"


def _drop_same_buff(champ, extra):
    """Remove the champion's copies of the trait or buff `extra` (the row's replaces them)."""
    equal_buffs = [
        champ_buff
        for champ_buff in champ.items
        if (
            champ_buff.name.rsplit(" ", 1)[0] == extra.name.rsplit(" ", 1)[0]
            or type(champ_buff) == type(extra)
        )
        and (
            champ_buff.name.rsplit(" ", 1)[0].replace(" ", "") in class_buffs
            or type(champ_buff).__name__ in class_buffs
            or (champ_buff.name == extra.name)
        )
    ]
    for equal_buff in equal_buffs:
        champ.items.remove(equal_buff)


def run_one(champion, opponent, extra, is_buff, duration, frame_rate=30, layout=None, setup=None):
    """One fight: a fresh copy of the configured champion with `extra` (an item, or a buff that replaces any copy of
    the same trait the champion already carries) against copies of the opponent placed by `layout`. `setup(champ,
    dummies)` runs before the fight (the fight viewer attaches its recorder there). Returns (champion, results)."""
    simulator = Simulator()
    layout = layout or Layout()
    champ = copy.deepcopy(champion)
    # An Emblem slice row brings its trait at the row's level (row_trait, sim_entry._slice_inputs): it replaces the
    # buff bar's copy as a buff extra would.
    trait = None if is_buff else getattr(extra, "row_trait", None)
    if is_buff or trait is not None:
        _drop_same_buff(champ, extra if is_buff else trait)
    dummies = [copy.deepcopy(opponent) for _ in range(layout.count)]
    if setup is not None:
        setup(champ, dummies)
    results = simulator.simulate(
        [] if is_buff else [copy.deepcopy(extra)],
        [copy.deepcopy(extra)] if is_buff else ([copy.deepcopy(trait)] if trait is not None else []),
        champ,
        dummies,
        duration,
        frameRate=frame_rate,
        layout=layout,
    )
    return champ, results


def do_experiment_one_extra(
    champion,
    opponent,
    item_list,
    buff_list,
    duration: float,
    frame_rate: int = 30,
    layout: Layout = None,
) -> List[Dict[str, Any]]:
    """One simulation per extra item, then per extra buff (run_one), each on a fresh copy of the configured champion
    against copies of the opponent placed by `layout` (layout.py)."""
    sim_list: List[Dict[str, Any]] = []
    for extras, is_buff in ((item_list, False), (buff_list, True)):
        for extra in extras:
            champ, results = run_one(champion, opponent, extra, is_buff, duration, frame_rate, layout)
            sim_list.append({"Champ": ChampLabel(champ.name, champ.level), "Extra": extra, "Results": results})
    return sim_list
