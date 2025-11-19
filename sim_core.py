# sim_core.py

import copy
from typing import Any, Dict, List

from set15buffs import Buff, class_buffs  # or wherever Buff lives
from simulator import Simulator


def do_experiment_one_extra(
    champion,
    opponent,
    item_list,
    buff_list,
    duration: float,
    frame_rate: int,
) -> List[Dict[str, Any]]:
    """
    Core sim logic, lifted from doExperimentOneExtraWrapped but with no Streamlit
    and no ObjectWrapper. All objects are the real champion/opponent/item instances.
    """
    simulator = Simulator()
    sim_list: List[Dict[str, Any]] = []

    # items first
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
        sim_list.append({"Champ": champ, "Extra": item, "Results": results})

    # then buffs
    for buff in buff_list:
        champ = copy.deepcopy(champion)

        equal_buffs = [
            champ_buff
            for champ_buff in champ.items
            if champ_buff.name.rsplit(" ", 1)[0] == buff.name.rsplit(" ", 1)[0]
            and (
                champ_buff.name.rsplit(" ", 1)[0].replace(" ", "") in class_buffs
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

        sim_list.append({"Champ": champ, "Extra": buff, "Results": results})

    # Star Guardian toggles
    if any(buff.name.startswith("Star Guardian") for buff in champion.items):
        for sg in champion.star_guardians:
            champ = copy.deepcopy(champion)
            champ.star_guardians[sg] = not champ.star_guardians[sg]

            results = simulator.simulate(
                [],
                [],
                champ,
                [copy.deepcopy(opponent) for _ in range(8)],
                duration,
                frameRate=frame_rate,
            )
            plus = "+" if champ.star_guardians[sg] else "-"
            sg_buff = Buff(f"Star Guardian ({plus}{sg})", 1, 0, None)
            sim_list.append({"Champ": champ, "Extra": sg_buff, "Results": results})

    return sim_list
