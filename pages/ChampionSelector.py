import sys

sys.path.append("..")
import copy
import inspect
import itertools

import class_utilities

# import metrics_panel
import numpy as np
import pandas as pd
import set16_streamlit_main
import set16buffs
import set16champs
import set16items
import streamlit as st
import utils

st.set_page_config(page_title="TFT Simulator", layout="wide")

t = 30
simLists = []
simDict = {}


champ_list = sorted(set16champs.champ_list)

# all_items = []
all_buffs = sorted(
    set16buffs.class_buffs
    + set16buffs.augments
    + set16buffs.no_buff
    + set16buffs.stat_buffs
)

all_items = sorted(
    set16items.offensive_craftables
    + set16items.artifacts
    + set16items.radiants
    + set16items.emblems
    + set16items.no_item
)

craftables = set16items.offensive_craftables

aug_buffs = sorted(set16buffs.augments)
void_buffs = sorted(set16buffs.void_buffs)

selected_void_buff = None

champ_before_sims = None

with st.sidebar:

    champ = class_utilities.champ_selector(champ_list)

    if hasattr(champ, "num_targets") and champ.num_targets > 0:
        targets = st.slider(
            "number of targets",
            min_value=1,
            max_value=max(3, champ.num_targets + 1),
            value=champ.num_targets,
        )
        champ.num_targets = targets
    if hasattr(champ, "num_extra_targets") and champ.num_extra_targets > 0:
        targets = st.slider(
            "number of extra targets",
            min_value=1,
            max_value=max(3, champ.num_extra_targets + 1),
            value=champ.num_extra_targets,
        )
        champ.num_extra_targets = targets
    # TF-only:
    if hasattr(champ, "percent_popped_marks") and champ.percent_popped_marks > -1:
        popped_marks = st.slider(
            "% of Marks that Get Popped",
            min_value=0.0,
            max_value=1.0,
            value=1.0,
            step=0.1,
        )
        champ.percent_popped_marks = popped_marks

    with st.expander("Extra options / bonus stats"):
        # class_utilities.first_takedown("First Takedown", champ)
        class_utilities.total_takedowns("takedowns", champ)
        class_utilities.num_traits("Num traits", champ)
        class_utilities.bonus_stats("Bonus Stats", champ)
    stage = class_utilities.stage_selector()
    tactician_level = class_utilities.level_selector()
    champ.stage = stage
    champ.tactician_level = tactician_level

    st.header("Global Items")

    items = class_utilities.items_list(all_items)

    buffs = class_utilities.buff_bar(
        all_buffs, max_buffs=10, num_buffs=2, starting_buffs=champ.default_traits, champ_name=champ.name
    )

    extra_buffs = []
    for buff in buffs:
        # Buff: ("Name", level, param)
        levels = utils.class_for_name("set16buffs", buff[0]).levels
        for level in levels:
            if level != buff[1]:
                extra_buffs.append(
                    utils.class_for_name("set16buffs", buff[0])(level, buff[2])
                )

    # Void buff selector
    if "Void" in [b[0] for b in buffs]:
        selected_void_buff = class_utilities.void_buff_selector(champ)
        if selected_void_buff != "NoBuff":
            champ.items.append(utils.class_for_name("set16buffs", selected_void_buff)(1, []))
        else:
            for void_buff in void_buffs:
                if void_buff != "NoBuff":
                    extra_buffs.append(utils.class_for_name("set16buffs", void_buff)(1, []))

    # HexMech Pilot selector
    if "HexMech" in [b[0] for b in buffs]:
        st.header("Pilot")
        pilot_role_name = st.selectbox(
            "Select Pilot Role",
            ["Tank", "Fighter", "Caster", "Marksman", "Assassin"],
            index=0,
            key="pilot_selector"
        )
        # Map string to Role enum
        role_map = {
            "Fighter": set16champs.Role.FIGHTER,
            "Tank": set16champs.Role.TANK,
            "Caster": set16champs.Role.CASTER,
            "Marksman": set16champs.Role.MARKSMAN,
            "Assassin": set16champs.Role.ASSASSIN
        }
        champ.pilot = role_map[pilot_role_name]

    enemy = class_utilities.enemy_list("Champ selector")

    framerate = class_utilities.frameRate("Frame Rate")

    # Add items to Champion
    for item in items:
        if item != "NoItem":
            champ.items.append(utils.class_for_name("set16items", item)())
            champ.item_count += 1
    class_utilities.add_buffs(champ, buffs)

    champ_before_sims = copy.deepcopy(champ)

    print("Champ buffs: ", champ_before_sims.items)

# # Metrics

# if "show_metrics" not in st.session_state:
#     st.session_state.show_metrics = False

# st.sidebar.toggle("Show server metrics", key="show_metrics")
# if st.session_state.show_metrics:
#     # Run once per render; use a placeholder so it doesn't block the rest of the UI
#     with st.sidebar:
#         st.session_state["_metrics_live"] = True
#         metrics_panel(poll_every=2.0)

# # End metrics

simLists, source = set16_streamlit_main.doExperimentOneExtra(
    champ,
    enemy,
    utils.convertStrList("set16items", all_items),
    utils.convertStrList("set16buffs", aug_buffs) + extra_buffs,
    t,
    framerate,
)

tab1, tab2 = st.tabs(["Items", "Radiant Refractor"])

with tab2:
    st.write("TODO: add radiant refractor table")
    # time to radiant refract things

with tab1:
    # Header
    st.header(
        "{} {} vs {} HP, {} Armor, {} MR".format(
            champ_before_sims.name,
            champ_before_sims.level,
            enemy.hp.stat,
            enemy.armor.stat,
            enemy.mr.stat,
        )
    )

    st.write(
        r"Most cast times/manalock times are guesses. Units can cast after they have completed 30% of an autoattack. Champs must attack at least once between casts (should only affect Samira). Simulator is probably not very accurate to true gameplay at high attack speeds."
    )

    itemSimulator = set16_streamlit_main.Simulator()
    itemSimulator.itemStats(champ_before_sims.items, champ_before_sims)

    class_utilities.write_champion(champ_before_sims)

    # checkboxes

    display_dps = st.checkbox("Display DPS", value=False)

    options = ["Craftable", "Artifact", "Radiant", "Emblem", "Trait", "Augment/Buff"]
    if len([item for item in items if item != "NoItem"]) >= 3:
        options = ["Trait", "Augment/Buff"]
    if selected_void_buff == "NoBuff":
        options.append("Void")
    if "HexMech" in [b[0] for b in buffs]:
        options.append("Pilot")

    radio_value = st.radio("", options, index=0, horizontal=True)

    df = set16_streamlit_main.createSelectorDPSTable(simLists)
    df_flt = df


    if radio_value == "Craftable":
        df_flt = df_flt[df_flt["Extra class name"].isin(craftables + ["NoItem"])]
    if radio_value == "Artifact":
        df_flt = df_flt[
            df_flt["Extra class name"].isin(set16items.artifacts + ["NoItem"])
        ]
    if radio_value == "Radiant":
        df_flt = df_flt[
            df_flt["Extra class name"].isin(set16items.radiants + ["NoItem"])
        ]
    if radio_value == "Emblem":
        df_flt = df_flt[
            df_flt["Extra class name"].isin(set16items.emblems + ["NoItem"])
        ]
    if radio_value == "Trait":
        df_flt = df_flt[
            df_flt["Extra class name"].isin([x[0] for x in buffs] + ["NoItem"])
        ]
    if radio_value == "Augment/Buff":
        df_flt = df_flt[
            df_flt["Extra class name"].isin(set16buffs.augments + ["NoItem"])
        ]
    if radio_value == "Void":
        df_flt = df_flt[
            df_flt["Extra class name"].isin(void_buffs + ["NoItem"])
        ]
    if radio_value == "Pilot":
        df_flt = df_flt[
            df_flt["Extra"].str.startswith("Pilot")
        ]

    new_df = df_flt.drop(["Extra class name", "Name", "Level"], axis=1)

    if not display_dps:
        new_df = new_df.drop(
            ["Extra DPS ({}s)".format(i) for i in [5, 10, 15, 20]], axis=1
        )
    else:
        new_df = new_df.drop(
            ["DPS at {}".format(i) for i in [5, 10, 15, 20, 25]], axis=1
        )

    class_utilities.plot_df(new_df, simLists)

st.caption(f"Simulation computed via: {source}")