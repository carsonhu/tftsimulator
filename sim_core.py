# sim_core.py

import copy
from typing import Any, Dict, List

import set16items
import set16buffs
from set16buffs import Buff, class_buffs  # or wherever Buff lives
from simulator import Simulator
from role import Role


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
        if isinstance(item, set16items.Emblem):
            # 0. Check if Emblem item is already on champion
            if any(i.name == item.name for i in champion.items):
                continue
            
            # 1. Check if trait is already on champion
            trait_cls = getattr(set16buffs, item.trait)
            existing_buffs = [b for b in champion.items if isinstance(b, trait_cls)]
            
            # Helper to get default params
            default_params = []
            if hasattr(trait_cls, "extraParameters"):
                try:
                    default_params = trait_cls.extraParameters()["Default"]
                except:
                    default_params = 0

            if not existing_buffs:
                # Case A: Trait not present. Add lowest non-zero level.
                default_level = [l for l in trait_cls.levels if l > 0][0]
                buff_instance = trait_cls(default_level, default_params)
                
                # Create display item with level info
                flavor_item = copy.deepcopy(item)
                flavor_item.name = f"{item.name} (Level {default_level})"
                
                champ = copy.deepcopy(champion)
                results = simulator.simulate(
                    [copy.deepcopy(item)],
                    [buff_instance], # Add buff
                    champ,
                    [copy.deepcopy(opponent) for _ in range(8)],
                    duration,
                    frameRate=frame_rate,
                )
                sim_list.append({"Champ": champ, "Extra": flavor_item, "Results": results})

            elif existing_buffs[0].level == 0:
                # Case B: Trait present but level 0 (NoBuff). Simulate ALL levels.
                for level in trait_cls.levels:
                    champ = copy.deepcopy(champion)
                    
                    # Remove existing buff
                    to_remove = [b for b in champ.items if b.name.startswith(item.trait)]
                    for b in to_remove:
                        champ.items.remove(b)
                        
                    buff_instance = trait_cls(level, default_params)
                    
                    # Create display item with level info
                    flavor_item = copy.deepcopy(item)
                    flavor_item.name = f"{item.name} ({item.trait} {level})"
                    
                    results = simulator.simulate(
                        [copy.deepcopy(item)],
                        [buff_instance],
                        champ,
                        [copy.deepcopy(opponent) for _ in range(8)],
                        duration,
                        frameRate=frame_rate,
                    )
                    sim_list.append({"Champ": champ, "Extra": flavor_item, "Results": results})
            else:
                # Case C: Trait present and active. Skip.
                continue

            continue 

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

    # HexMech Pilot toggles
    if any(buff.name.startswith("HexMech") for buff in champion.items):
        for role in Role:
            champ = copy.deepcopy(champion)
            champ.pilot = role
            
            results = simulator.simulate(
                [],
                [],
                champ,
                [copy.deepcopy(opponent) for _ in range(8)],
                duration,
                frameRate=frame_rate,
            )
            
            pilot_mode = PilotMode(f"Pilot: {role.value}")
            sim_list.append({"Champ": champ, "Extra": pilot_mode, "Results": results})

    return sim_list


class PilotMode:
    def __init__(self, name):
        self.name = name
