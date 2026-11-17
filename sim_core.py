# sim_core.py

import copy
from typing import Any, Dict, List

from set19buffs import class_buffs
from simulator import Simulator


class ChampLabel:
    """The two fields a result row's champion is ever asked for.

    Each row used to carry its whole post-combat Champion -- item graph,
    statuses and all -- but every consumer (createSelectorDPSTable,
    createUnitDPSTable, class_utilities.plot_df) reads only .name and .level.
    Since st.cache_data pickles what it stores, keeping the full objects cost
    ~1.2MB and ~100ms of (un)pickling per cached sweep to serve two scalars.

    Note this is the *result* row, not the cache key: the key is the pickled
    input champion built in doExperimentOneExtra, which still carries every
    item, buff and bonus stat. Trimming here can't weaken it.

    The cost of the trim is diagnostic -- per-row final stacks, statuses and
    numCasts are gone. Per-instant AS and mana survive in Results, whose
    entries are (time, damage, aspd, curMana, fullMana).
    """

    __slots__ = ("name", "level")

    def __init__(self, name, level):
        self.name = name
        self.level = level

    def __repr__(self):
        return f"ChampLabel({self.name!r}, {self.level!r})"


def do_experiment_one_extra(
    champion,
    opponent,
    item_list,
    buff_list,
    duration: float,
    frame_rate: int = 30,
) -> List[Dict[str, Any]]:
    """One simulation per extra item, then per extra buff, each on a fresh copy of the configured champion
    against 8 copies of the opponent. A buff replaces any copy of the same trait the champion already carries.
    (set18's Emblem, N.O.V.A., Blackthorn and Arbiter sweeps were Set 18 traits and are gone, E16.)"""
    simulator = Simulator()
    sim_list: List[Dict[str, Any]] = []

    for item in item_list:
        champ = copy.deepcopy(champion)
        results = simulator.simulate(
            [copy.deepcopy(item)],
            [],
            champ,
            [copy.deepcopy(opponent) for _ in range(8)],
            duration,
            frameRate=frame_rate,
        )
        sim_list.append({"Champ": ChampLabel(champ.name, champ.level), "Extra": item, "Results": results})

    for buff in buff_list:
        champ = copy.deepcopy(champion)
        equal_buffs = [
            champ_buff
            for champ_buff in champ.items
            if (
                champ_buff.name.rsplit(" ", 1)[0] == buff.name.rsplit(" ", 1)[0]
                or type(champ_buff) == type(buff)
            )
            and (
                champ_buff.name.rsplit(" ", 1)[0].replace(" ", "") in class_buffs
                or type(champ_buff).__name__ in class_buffs
                or (champ_buff.name == buff.name)
            )
        ]
        for equal_buff in equal_buffs:
            champ.items.remove(equal_buff)
        results = simulator.simulate(
            [],
            [copy.deepcopy(buff)],
            champ,
            [copy.deepcopy(opponent) for _ in range(8)],
            duration,
            frameRate=frame_rate,
        )
        sim_list.append({"Champ": ChampLabel(champ.name, champ.level), "Extra": buff, "Results": results})

    return sim_list
