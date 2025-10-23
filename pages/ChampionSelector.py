import sys

sys.path.append("..")
import copy
import inspect
import itertools

import class_utilities
import numpy as np
import pandas as pd
import set15_streamlit_main
import set15buffs
import set15champs
import set15items
import streamlit as st
import utils

st.set_page_config(layout="wide")

t = 30
simLists = []
simDict = {}


champ_list = sorted(set15champs.champ_list)

# all_items = []
all_buffs = sorted(
    set15buffs.class_buffs
    + set15buffs.augments
    + set15buffs.no_buff
    + set15buffs.stat_buffs
)

all_items = sorted(
    set15items.offensive_craftables
    + set15items.artifacts
    + set15items.radiants
    + set15items.no_item
)

craftables = set15items.offensive_craftables

aug_buffs = sorted(set15buffs.augments)

powerups = sorted(set15buffs.powerups + set15buffs.no_buff)
valid_powerups = powerups

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

    with st.popover("Extra options / bonus stats"):
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
        all_buffs, max_buffs=10, num_buffs=2, starting_buffs=champ.default_traits
    )
    buffs.append(("MentorBuff", 1, []))

    # get power ups
    valid_powerups = class_utilities.get_valid_powerups(champ, powerups)
    chosen_powerup = class_utilities.powerup_bar(valid_powerups)

    if chosen_powerup != "NoBuff":
        class_utilities.add_powerup(champ, chosen_powerup)

    extra_buffs = []
    for buff in buffs:
        # Buff: ("Name", level, param)
        levels = utils.class_for_name("set15buffs", buff[0]).levels
        for level in levels:
            if level != buff[1]:
                extra_buffs.append(
                    utils.class_for_name("set15buffs", buff[0])(level, buff[2])
                )

    class_utilities.mentor_selector(champ)

    if "StarGuardian" in [b[0] for b in buffs]:
        class_utilities.starguardian_selector(champ)

    enemy = class_utilities.enemy_list("Champ selector")

    framerate = class_utilities.frameRate("Frame Rate")

    # Add items to Champion
    for item in items:
        if item != "NoItem":
            champ.items.append(utils.class_for_name("set15items", item)())
            champ.item_count += 1
    class_utilities.add_buffs(champ, buffs)

    champ_before_sims = copy.deepcopy(champ)

    print("Champ buffs: ", champ_before_sims.items)

if chosen_powerup == "NoBuff":
    for powerup in powerups:
        if powerup != "NoBuff":
            extra_buffs.append(utils.class_for_name("set15powerups", powerup)(1, []))

simLists = set15_streamlit_main.doExperimentOneExtra(
    champ,
    enemy,
    utils.convertStrList("set15items", all_items),
    utils.convertStrList("set15buffs", aug_buffs) + extra_buffs,
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

    itemSimulator = set15_streamlit_main.Simulator()
    itemSimulator.itemStats(champ_before_sims.items, champ_before_sims)

    class_utilities.write_champion(champ_before_sims)

    # checkboxes

    display_dps = st.checkbox("Display DPS", value=False)

    options = ["Craftable", "Artifact", "Radiant", "Trait", "Augment/Buff"]
    if len([item for item in items if item != "NoItem"]) >= 3:
        options = ["Trait", "Augment/Buff"]

    # if "Star Guardian" in buffs, add "star Guardian" option
    if any(buff.name.startswith("Star Guardian") for buff in champ_before_sims.items):
        options.append("Star Guardian")
    if chosen_powerup == "NoBuff":
        options.append("Powerup")

    radio_value = st.radio("", options, index=0, horizontal=True)

    df = set15_streamlit_main.createSelectorDPSTable(simLists)
    df_flt = df

    # starguardian filter
    star_guardians = list(champ.star_guardians.keys())
    sg_list = []
    for sign in ["+", "-"]:
        for sg in star_guardians:
            sg_list.append("Star Guardian ({}{})".format(sign, sg))

    if radio_value == "Craftable":
        df_flt = df_flt[df_flt["Extra class name"].isin(craftables + ["NoItem"])]
    if radio_value == "Artifact":
        df_flt = df_flt[
            df_flt["Extra class name"].isin(set15items.artifacts + ["NoItem"])
        ]
    if radio_value == "Radiant":
        df_flt = df_flt[
            df_flt["Extra class name"].isin(set15items.radiants + ["NoItem"])
        ]
    if radio_value == "Trait":
        df_flt = df_flt[
            df_flt["Extra class name"].isin([x[0] for x in buffs] + ["NoItem"])
        ]
    if radio_value == "Augment/Buff":
        df_flt = df_flt[
            df_flt["Extra class name"].isin(set15buffs.augments + ["NoItem"])
        ]
    if radio_value == "Powerup":
        df_flt = df_flt[df_flt["Extra class name"].isin(valid_powerups + ["NoItem"])]
    if radio_value == "Star Guardian":
        df_flt = df_flt[df_flt["Extra"].isin(sg_list + ["NoItem"])]

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
