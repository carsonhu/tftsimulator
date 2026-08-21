import sys

sys.path.append("..")
import copy
import inspect
import itertools

import class_utilities

# import metrics_panel
import numpy as np
import pandas as pd
import set18_streamlit_main
import set18buffs
import set18champs
import set18items
import streamlit as st
import utils

st.set_page_config(page_title="TFT Simulator", layout="wide")

t = 30
simLists = []
simDict = {}

# Shared between the pre-render "which slice do I simulate?" read in the
# sidebar and the st.radio call in tab1 that actually draws the control.
RESULTS_RADIO_KEY = "results_radio"


champ_list = sorted(set18champs.champ_list)

# all_items = []
all_buffs = sorted(
    set18buffs.class_buffs
    + set18buffs.augments
    + set18buffs.no_buff
    + set18buffs.stat_buffs
    + set18buffs.wisps
)

all_items = sorted(
    set18items.offensive_craftables
    + set18items.artifacts
    + set18items.radiants
    + set18items.emblems
    + set18items.animas
    + set18items.no_item
)

sidebar_items = sorted(all_items)

craftables = set18items.offensive_craftables

aug_buffs = sorted(set18buffs.augments)

wisp_buffs = sorted(set18buffs.wisps)

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


    with st.expander("Extra options / bonus stats"):
        # class_utilities.first_takedown("First Takedown", champ)
        class_utilities.total_takedowns("takedowns", champ)
        class_utilities.num_traits("Num traits", champ)
        class_utilities.bonus_stats("Bonus Stats", champ)

    def clear_stat(k, d):
        st.session_state[k] = d

    active_filters = []
    check_stats = [
        ("takedowns", "takedowns", 0, "{} takedowns"),
        ("Num traits", "Num traits", 6, "{} active traits"),
        ("Bonus AD", "Bonus Statsad", 0, "{} bonus AD"),
        ("DmgAmp", "Bonus Statsdmgamp", 0, "{} DmgAmp"),
        ("ManaRegen", "Bonus Statsmanaregen", 0, "{} ManaRegen"),
        ("Bonus AP", "Bonus Statsap", 0, "{} bonus AP"),
        ("Bonus Crit", "Bonus Statscrit", 0, "{} Bonus Crit"),
        ("ManaPerAuto", "Bonus Statsmpa", 0, "{} ManaPerAuto"),
        ("Bonus AS", "Bonus StatsAS", 0, "{} Bonus AS"),
        ("CritDmg", "Bonus Statscritdmg", 0, "{} CritDmg")
    ]
    
    for label, key, default, fmt in check_stats:
        if key in st.session_state and st.session_state[key] != default:
            active_filters.append((key, default, fmt.format(st.session_state[key])))

    if active_filters:
        for i in range(0, len(active_filters), 2):
            cols = st.columns(2)
            chunk = active_filters[i:i+2]
            for j, (key, default, text) in enumerate(chunk):
                with cols[j]:
                    st.button(f"✖ {text}", key=f"clear_{key}", on_click=clear_stat, args=(key, default))

    stage = class_utilities.stage_selector()
    tactician_level = class_utilities.level_selector()
    champ.stage = stage
    champ.tactician_level = tactician_level

    st.header("Global Items")

    items = class_utilities.items_list(sidebar_items)

    buffs = class_utilities.buff_bar(
        all_buffs, max_buffs=10, num_buffs=2, starting_buffs=champ.default_traits, champ_name=champ.name
    )

    extra_buffs = []
    for buff in buffs:
        # Buff: ("Name", level, param)
        levels = utils.class_for_name("set18buffs", buff[0]).levels
        for level in levels:
            if level != buff[1]:
                extra_buffs.append(
                    utils.class_for_name("set18buffs", buff[0])(level, buff[2])
                )

    class_utilities.blackthorn_selector(champ, buffs)

    enemy = class_utilities.enemy_list("Champ selector")

    framerate = class_utilities.frameRate("Frame Rate")

    # Add items to Champion
    for item in items:
        if item != "NoItem":
            champ.items.append(utils.class_for_name("set18items", item)())
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

    # The table only ever shows one radio slice at a time, so only the visible
    # slice is simulated up front. Sweeping everything was ~135 sims per widget
    # change; a slice is at most ~30. Every slice carries NoItem, because
    # createSelectorDPSTable's "Extra DPS" column is a ratio against that row.
    #
    # WARM_OTHER_SLICES (bottom of this file) then fills the cache with the
    # rest *after* the visible table has rendered, so clicking another radio
    # option is a cache hit rather than a fresh sweep. That moves the wait
    # after first paint rather than removing it -- set it False to genuinely
    # do less work per interaction, at the cost of a pause on each radio
    # click. That is the better setting for low-end phones under stlite.
    WARM_OTHER_SLICES = True

    def slice_inputs(name):
        """(item names, buff objects, run_blackthorn) for one radio option."""
        if name == "Craftable":
            return craftables, [], False
        if name == "Artifact":
            return set18items.artifacts, [], False
        if name == "Radiant":
            return set18items.radiants, [], False
        if name == "Emblem":
            return set18items.emblems, [], False
        if name == "Anima":
            return set18items.animas, [], False
        if name == "Trait":
            return [], extra_buffs, False
        if name == "Augment/Buff":
            return [], utils.convertStrList("set18buffs", aug_buffs), False
        if name == "Wisp":
            return [], utils.convertStrList("set18buffs", wisp_buffs), False
        if name == "Blackthorn":
            # No items or buffs of its own -- the sweep lives in sim_core and
            # keys off the champion already carrying the trait.
            return [], [], True
        return [], [], False

    def run_slice(name):
        slice_items, slice_buffs, run_blackthorn = slice_inputs(name)
        return set18_streamlit_main.doExperimentOneExtra(
            champ,
            enemy,
            utils.convertStrList("set18items", list(slice_items) + set18items.no_item),
            slice_buffs,
            t,
            framerate,
            run_blackthorn=run_blackthorn,
        )

    # The radio widget is created down in tab1, so this reads the value it left
    # in session_state on the previous run -- the whole point being to know
    # which slice to simulate before anything renders. Clicking the radio
    # reruns the script with the new value already in place, so the right slice
    # is computed on that same rerun.
    options = ["Craftable", "Artifact", "Radiant", "Emblem", "Trait", "Augment/Buff", "Wisp"]
    if len([item for item in items if item != "NoItem"]) >= 3:
        options = ["Trait", "Augment/Buff", "Wisp"]
    if any(b[0] == "Blackthorn" for b in buffs):
        options.append("Blackthorn")

    # A stored pick can fall out of `options` when the sidebar changes (a third
    # item added, the Blackthorn trait dropped). Re-seeding session_state here
    # keeps st.radio from being handed a value it can't show.
    radio_value = st.session_state.get(RESULTS_RADIO_KEY)
    if radio_value not in options:
        radio_value = options[0]
        st.session_state[RESULTS_RADIO_KEY] = radio_value

    simLists, source = run_slice(radio_value)

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

    itemSimulator = set18_streamlit_main.Simulator()
    itemSimulator.itemStats(champ_before_sims.items, champ_before_sims)

    class_utilities.write_champion(champ_before_sims)

    # checkboxes

    display_dps = st.checkbox("Display DPS", value=False)

    # `options` and the current pick were both resolved in the sidebar, before
    # the sim ran; this only draws the control.
    radio_value = st.radio(
        "",
        options,
        index=options.index(radio_value),
        key=RESULTS_RADIO_KEY,
        horizontal=True,
    )

    df = set18_streamlit_main.createSelectorDPSTable(simLists)
    df_flt = df


    # simLists now holds this slice alone, plus the NoItem row every slice
    # carries for the Extra DPS ratio, so the per-option .isin() filters that
    # used to live here have nothing left to remove. Blackthorn stays: its
    # "None" row is the baseline to display, so NoItem drops out of the table
    # (it stays in simLists, where the ratio needs it).
    if radio_value == "Blackthorn":
        # One row per sacrifice; the empty hex stands in for the NoItem row.
        df_flt = df_flt[df_flt["Extra"].str.startswith("Blackthorn: ")]
    new_df = df_flt.drop(["Extra class name", "Name", "Level"], axis=1)

    # The sacrifice's Role/Star Level/Cost replace the row name under the
    # Blackthorn radio, and are dead weight under every other one.
    blackthorn_cols = [c for c in ("Role", "Star Level", "Cost") if c in new_df.columns]
    if radio_value == "Blackthorn":
        new_df = new_df.drop(["Extra"], axis=1)
        new_df = new_df[
            blackthorn_cols + [c for c in new_df.columns if c not in blackthorn_cols]
        ]
    elif blackthorn_cols:
        new_df = new_df.drop(blackthorn_cols, axis=1)

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

# Everything above has rendered by now, so this is the "load the rest in the
# background" half: warm the cache for the radio options the visitor didn't
# pick. Streamlit streams output as the script runs, so the table is already on
# screen while this works through the remaining slices, and touching any widget
# abandons this run rather than waiting on it.
if WARM_OTHER_SLICES:
    for slice_name in options:
        if slice_name != radio_value:
            run_slice(slice_name)