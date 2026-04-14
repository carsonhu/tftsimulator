# sim_core.py

import copy
from typing import Any, Dict, List

import set17items
import set17buffs
from set17buffs import Buff, class_buffs  # or wherever Buff lives
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
        if isinstance(item, set17items.Emblem):
            # 0. Check if Emblem item is already on champion
            if any(i.name == item.name for i in champion.items):
                continue
            
            # 1. Check if trait is already on champion
            trait_cls = getattr(set17buffs, item.trait)
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

        sim_list.append({"Champ": champ, "Extra": buff, "Results": results})

    # NOVA toggles
    if any(buff.name.startswith("N.O.V.A.") for buff in champion.items):
        for nova_unit in champion.novas:
            champ = copy.deepcopy(champion)
            champ.novas[nova_unit] = not champ.novas[nova_unit]

            results = simulator.simulate(
                [],
                [],
                champ,
                [copy.deepcopy(opponent) for _ in range(8)],
                duration,
                frameRate=frame_rate,
            )
            plus = "+" if champ.novas[nova_unit] else "-"
            nova_buff = Buff(f"NOVA ({plus}{nova_unit})", 1, 0, None)
            sim_list.append({"Champ": champ, "Extra": nova_buff, "Results": results})

    # Ezreal Takedown iterations
    if champion.name == "Ezreal":
        t_vals = [0, 25, 50, 100]
        current = getattr(champion, 'takedowns', 0)
        if current not in t_vals:
            t_vals.append(current)
        t_vals.sort()
        
        for t_val in t_vals:
            champ = copy.deepcopy(champion)
            champ.takedowns = t_val

            results = simulator.simulate(
                [],
                [],
                champ,
                [copy.deepcopy(opponent) for _ in range(8)],
                duration,
                frameRate=frame_rate,
            )
            tk_buff = Buff(f"Takedowns: {t_val}", 1, 0, None)
            sim_list.append({"Champ": champ, "Extra": tk_buff, "Results": results})

    # Arbiter iterations
    arbiter_trait = next((b for b in champion.items if b.name.startswith("Arbiter")), None)
    if arbiter_trait and arbiter_trait.level > 0:
        causes = [
            "When an Arbiter attacks 3 times",
            "Every 4 seconds",
            "Combat Start: For each interest you would gain",
            "Combat start: If you rerolled",
            "When an Arbiter spends 50 mana",
            "Combat Start: For each Arbiter star level",
            "When an Arbiter deals damage 10 times",
        ]
        effects = ["Gain AS", "Gain AP", "Gain mana", "Other"]
        
        cause_map = {
            "When an Arbiter attacks 3 times": "Attack 3 times",
            "Every 4 seconds": "Every 4 seconds",
            "Combat Start: For each interest you would gain": "Gain interest",
            "Combat start: If you rerolled": "Reroll",
            "When an Arbiter spends 50 mana": "Spend 50 mana",
            "Combat Start: For each Arbiter star level": "Star Level",
            "When an Arbiter deals damage 10 times": "Deal Damage 10 times",
        }
        
        seen_other = False
        for cause in causes:
            for effect in effects:
                # 1. Skip redundant "Other"
                if effect == "Other":
                    if seen_other: continue
                    seen_other = True
                
                # 2. Skip non-functional mana cases
                if effect == "Gain mana" and cause in [
                    "Combat Start: For each interest you would gain",
                    "Combat start: If you rerolled",
                    "When an Arbiter deals damage 10 times"
                ]:
                    continue
                
                champ = copy.deepcopy(champion)
                champ.cause = cause
                champ.effect = effect
                
                results = simulator.simulate(
                    [],
                    [],
                    champ,
                    [copy.deepcopy(opponent) for _ in range(8)],
                    duration,
                    frameRate=frame_rate,
                )
                
                if effect == "Other":
                    display_name = "Other"
                else:
                    short_cause = cause_map.get(cause, cause)
                    display_name = f"{short_cause} | {effect}"
                
                arb_buff = Buff(display_name, 1, 0, None)
                sim_list.append({"Champ": champ, "Extra": arb_buff, "Results": results})

    return sim_list

