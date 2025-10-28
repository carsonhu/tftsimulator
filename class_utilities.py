# This is for commonly used functions in fated/snipers

# import plotly.graph_objects as go
import json
import os
from importlib.resources import files  # Python 3.9+
from pathlib import Path
from typing import List, Optional

import pandas as pd
import plotly.graph_objects as go
import set15buffs
import streamlit as st
import utils
from helpers import buff_display_map, buff_display_names, item_display_map
from set15buffs import *
from set15champs import *
from set15items import *

# Detect stlite/Pyodide (stlite sets this env var)
IS_STLITE = os.environ.get("PYODIDE_BASE_URL") is not None


def select_rows_fallback(df: pd.DataFrame, label="Trials to plot"):
    # Show a read-only table plus a multiselect to choose rows
    labels = {i: f"{i}: {df.loc[i, 'Extra']}" for i in df.index}
    choice = st.multiselect(label, df.index.tolist(), format_func=lambda i: labels[i])
    st.dataframe(df, use_container_width=True)
    return choice


def checkbox_select_fallback(
    df: pd.DataFrame,
    *,
    label: str = "Trials to plot",
    display_df: bool = True,
    key_prefix: str = "plotpick",
    search_cols: Optional[List[str]] = None,
) -> list:
    """
    Render a compact list of checkboxes for the dataframe's index, with
    select/clear and an optional text filter. Returns a list of selected indices.
    """

    # Keep stable keys per row across reruns
    def _row_key(i):
        return f"{key_prefix}_row_{i}"

    # Quick text filter (client-side)
    q = st.text_input("Filter", placeholder="type to filter…", key=f"{key_prefix}_q")
    if q:
        q_lower = q.lower()
        cols = search_cols or [c for c in df.columns if df[c].dtype == "object"]
        mask = pd.Series([False] * len(df), index=df.index)
        for c in cols:
            mask |= df[c].astype(str).str.lower().str.contains(q_lower, na=False)
        df = df[mask]

    # Select / Clear
    c1, c2, c3 = st.columns([1, 1, 6])
    with c1:
        if st.button("Select all", key=f"{key_prefix}_all"):
            for i in df.index:
                st.session_state[_row_key(i)] = True
    with c2:
        if st.button("Clear", key=f"{key_prefix}_none"):
            for i in df.index:
                st.session_state[_row_key(i)] = False

    # Checkboxes (left) + optional table (right)
    left, right = st.columns([1, 3])
    selected: list[int] = []
    with left:
        st.markdown(f"**{label}**")
        for i, row in df.iterrows():
            lab = f"{i}: {row.get('Extra', '')}"
            if st.checkbox(lab, key=_row_key(i)):
                selected.append(i)

    if display_df:
        with right:
            st.dataframe(df, use_container_width=True)

    return selected


def buff_bar(
    buff_list, num_buffs=1, max_buffs=4, starting_buffs=[], default_item="NoBuff"
):
    """Buff Bar: Code for displaying the Buffs input list:
    Each Buff has a name and a level.

    Args:
        buff_list (TYPE): List of buffs to add in
        num_buffs (int, optional): Number of buffs in the buff bar

    Returns:
        tuple: (buff name, buff level, params)
    """

    # display name -> class name
    buff_map = buff_display_map(buff_list)
    starting_buffs = buff_display_names(starting_buffs)
    buff_list = list(buff_map.keys())
    # buff_list = buff_display_names(buff_list)
    st.header("Global Buffs")
    item_cols = st.columns([2, 1, 1])
    num_buffs = st.slider(
        "Number of Buffs",
        min_value=1,
        max_value=max_buffs,
        value=max(num_buffs, len(starting_buffs)),
    )
    buffs = []

    for n in range(num_buffs):
        index = 0
        if default_item in buff_list:
            index = buff_list.index(default_item)
        with item_cols[0]:
            if n < len(starting_buffs):
                if starting_buffs[n] in buff_list:
                    index = buff_list.index(starting_buffs[n])
            buff1 = st.selectbox(
                "Buff {}".format(n + 1), buff_list, key="Buff {}".format(n), index=index
            )
            buff1 = buff_map[buff1]
        with item_cols[1]:
            buff1level = st.selectbox(
                "Level",
                utils.class_for_name("set15buffs", buff1).levels,
                key="Buff lvl {}".format(n),
            )
        with item_cols[2]:
            extraParams = utils.class_for_name("set15buffs", buff1).extraParameters()
            if extraParams != 0:
                buff1Extra = st.number_input(
                    extraParams["Title"],
                    min_value=extraParams["Min"],
                    max_value=extraParams["Max"],
                    value=extraParams["Default"],
                    key=extraParams["Title"] + str(n),
                )
            else:
                buff1Extra = st.number_input(
                    "(ignore)",
                    min_value=0,
                    max_value=0,
                    value=0,
                    key="extra buff" + buff1 + str(n),
                )
        buffs.append((buff1, buff1level, buff1Extra))
    return buffs


def _load_powerups():
    # assumes champ_powerups.json sits next to app.py (or current working dir)
    text = Path("champ_powerups.json").read_text(encoding="utf-8")
    return json.loads(text)


def get_valid_powerups(champ, powerups):
    data = _load_powerups()
    if champ.name in data:
        valid_powerups = data[champ.name] + set15buffs.no_buff
        return [item for item in powerups if item in valid_powerups]
    return []


def powerup_bar(powerup_list, default_item="NoBuff"):
    st.header("Power Up")
    # item_cols = st.columns([2, 1])
    index = 0
    if default_item in powerup_list:
        index = powerup_list.index(default_item)

    powerup = st.selectbox(
        "Powerup {}".format(1), powerup_list, key="Powerup {}".format(1), index=index
    )
    return powerup


def stage_selector():
    stage = st.selectbox("Current stage", ("2-1", "3-1", "4-1", "5-1", "6-1"), index=2)
    return int(stage.split("-")[0])


def level_selector():
    level = st.slider("Tactician Level", 3, 10, value=4)
    return level


def write_champion(champ):
    st.subheader("Base stats")
    cols = st.columns(4)
    ad_text = (
        f"AD: :blue[{round(champ.atk.stat * champ.bonus_ad.stat, 2)}] = {champ.atk.base} * :green[{round(champ.bonus_ad.stat, 4)} AD]"
        if champ.bonus_ad.addMultiplier == 1
        else f"AD: :blue[{round(champ.atk.stat * champ.bonus_ad.stat, 2)}] = {champ.atk.base} * ({1} + :red[{champ.bonus_ad.addMultiplier}] * :green[{round(champ.bonus_ad.add/100, 4)} AD])"
    )
    ap_text = (
        f"AP: :blue[{round(champ.ap.stat, 2)}] = {champ.ap.base} + :green[{round(champ.ap.add, 2)} AP]"
        if champ.ap.addMultiplier == 1
        else f"AP: :blue[{round(champ.ap.stat, 2)}] = {champ.ap.base} + :red[{champ.ap.addMultiplier}] * :green[{round(champ.ap.add, 2)} AP]"
    )
    dmgamp_text = f"DmgAmp: :blue[{round(champ.dmgMultiplier.stat, 2)}] = {champ.dmgMultiplier.base} + :green[{round(champ.dmgMultiplier.add, 4)} DmgAmp]"
    mana_text = f"Mana: :blue[{round(champ.curMana, 2)}] / :blue[{round(champ.fullMana.stat, 2)}]"
    mana_gen_text = f"Mana Regen: :blue[{round(champ.manaRegen.stat, 2)}] = {champ.manaRegen.base} + :green[{round(champ.manaRegen.add, 2)} Mana]"
    cast_text = f"Cast Time: :blue[{champ.castTime} seconds]"

    as_text = f"AS: :blue[{round(champ.aspd.stat, 3)}] = {champ.aspd.base} * (1 + :green[{round(champ.aspd.add, 4)} AS])"
    crit_chance_text = f"Crit Chance: :blue[{round(champ.crit.stat, 3)}] = {champ.crit.base} + :green[{round(champ.crit.add, 4)} Crit]"
    crit_dmg_text = f"Crit Dmg: :blue[{round(champ.critDmg.stat, 2)}] = {champ.critDmg.base} + :green[{round(champ.critDmg.add, 4)} CritDmg]"
    mana_per_attack_text = f"ManaPerAttack: :blue[{round(champ.manaPerAttack.stat, 2)}] = {champ.manaPerAttack.base} + :green[{round(champ.manaPerAttack.add, 2)} Mana]"
    role_text = f"Role: :blue[{champ.role.value}]"
    can_spellcrit_text = f"Can SpellCrit: :blue[{champ.canSpellCrit}]"
    with cols[0]:
        st.write(
            f"""
          {ad_text}
          <br>
          {ap_text}
          <br>
          {dmgamp_text}
          <br>
          {mana_text}
          <br>
          {mana_gen_text}
          <br>
          {cast_text}
          """,
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.write(
            f"""
          {as_text}
          <br>
          {crit_chance_text}
          <br>
          {crit_dmg_text}
          <br>
          {mana_per_attack_text}
          <br>
          {role_text}
          <br>
          {can_spellcrit_text}
          """,
            unsafe_allow_html=True,
        )
    if champ.notes:
        st.write("Notes: " + champ.notes)


def plot_df(df, simLists):
    # --- selection UI ---
    if not IS_STLITE:
        df["To Plot"] = False
        df_edit = st.data_editor(
            df,
            column_config={
                "To Plot": st.column_config.CheckboxColumn(
                    "To Plot", help="Which trials to plot", default=False
                )
            },
            hide_index=False,
        )
        indices_to_plot = df_edit.index[df_edit["To Plot"]].tolist()
    else:
        indices_to_plot = checkbox_select_fallback(df, label="Trials to plot")

    # --- build series dict ---
    dmg_dict = {}
    for idx in indices_to_plot:
        dmg = pd.DataFrame(
            [
                [
                    inst[0],
                    inst[1][0],
                    inst[1][1],
                    inst[2],
                    f"{inst[3]:.1f} / {inst[4]}" if inst[4] > 0 else f"{inst[3]:.1f}",
                ]
                for inst in simLists[idx]["Results"]
            ],
            columns=["Time", "Dmg", "Type", "AS", "Mana"],
        )
        dmg["Total Dmg"] = dmg["Dmg"].cumsum()
        dmg = dmg[["Time", "Dmg", "Total Dmg", "Type", "AS", "Mana"]]
        dmg_dict[idx] = {
            "Dmg": dmg,
            "Name": simLists[idx]["Champ"].name,
            "Level": simLists[idx]["Champ"].level,
            "Item": simLists[idx]["Extra"].name,
        }

    if not dmg_dict:
        st.info("Tick one or more rows to plot.")
        return

    col1, col2 = st.columns([3, 1])
    plot_labels = {k: f"{k}: {v['Item']}" for k, v in dmg_dict.items()}

    # ---------------------- PLOT (left) ----------------------
    with col1:
        # theme-aware basics
        is_dark = (
            (st.get_option("theme.base") == "dark")
            if st.get_option("theme.base")
            else False
        )
        COLORS_LIGHT = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]
        COLORS_DARK = [
            "#4cc9f0",
            "#f72585",
            "#ffd166",
            "#80ed99",
            "#f8961e",
            "#56cfe1",
            "#b8f2e6",
            "#ffcad4",
            "#c77dff",
            "#72efdd",
        ]
        COLORS = COLORS_DARK if is_dark else COLORS_LIGHT

        font_color = "#EAEAEA" if is_dark else "#111111"
        grid_color = "rgba(255,255,255,0.12)" if is_dark else "rgba(0,0,0,0.12)"
        legend_bg = "rgba(20,20,20,0.85)" if is_dark else "rgba(250,250,250,0.95)"
        legend_font = "#FFFFFF" if is_dark else "#111111"

        fig = go.Figure()

        # ---- add each series: visual line + invisible hover helper ----
        for i, (key, val) in enumerate(dmg_dict.items()):
            d = val["Dmg"]
            t = d["Time"].to_numpy()
            y = d["Total Dmg"].to_numpy()

            # 1) Visual line (linear), excluded from hover
            fig.add_trace(
                go.Scatter(
                    x=t,
                    y=y,
                    mode="lines",
                    line=dict(width=3, color=COLORS[i % len(COLORS)]),
                    line_shape="linear",
                    name=plot_labels[key],
                    hoverinfo="skip",
                    showlegend=True,
                )
            )

            # 2) Hover helper: midpoint markers that report LEFT endpoint values
            if len(t) >= 2:
                mids = (t[:-1] + t[1:]) / 2.0
                prev_vals = y[:-1]
                prev_times = t[:-1]

                fig.add_trace(
                    go.Scatter(
                        x=mids,
                        y=prev_vals,
                        customdata=prev_times,
                        mode="markers",
                        marker=dict(size=0.1, opacity=0),  # invisible, but hoverable
                        name=plot_labels[key],
                        showlegend=False,
                        # Put series name in the content & remove the "extra" box.
                        hovertemplate=(
                            "<b>%{fullData.name}</b><br>"
                            "t=%{customdata:.1f}s<br>"
                            "Total Dmg=%{y:,.0f}"
                            "<extra></extra>"
                        ),
                    )
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=t,
                        y=y,
                        customdata=t,
                        mode="markers",
                        marker=dict(size=0.1, opacity=0),
                        name=plot_labels[key],
                        showlegend=False,
                        hovertemplate=(
                            "<b>%{fullData.name}</b><br>"
                            "t=%{customdata:.1f}s<br>"
                            "Total Dmg=%{y:,.0f}"
                            "<extra></extra>"
                        ),
                    )
                )

        first_key = next(iter(dmg_dict))
        fig.update_layout(
            template=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title=f"{dmg_dict[first_key]['Name']} {dmg_dict[first_key]['Level']} Damage Chart",
            title_x=0.5,
            title_font=dict(size=26, color=font_color),
            font=dict(size=14, color=font_color),
            xaxis=dict(
                title="Time (s)",
                showgrid=True,
                gridcolor=grid_color,
                zeroline=False,
                tickfont=dict(color=font_color),
                title_font=dict(color=font_color),
            ),
            yaxis=dict(
                title="Damage",
                showgrid=True,
                gridcolor=grid_color,
                zeroline=False,
                tickformat=",",
                tickfont=dict(color=font_color),
                title_font=dict(color=font_color),
            ),
            legend=dict(
                x=0.02,
                y=0.98,
                xanchor="left",
                yanchor="top",
                bgcolor=legend_bg,
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1,
                font=dict(size=16, color=legend_font),
            ),
            # ----- KEY CHANGES: unified hover at top, no overlaying panel -----
            hovermode="x unified",  # one tooltip at the top
            hoverlabel=dict(
                namelength=-1,
                align="left",
                bgcolor="rgba(20,20,20,0.6)",  # purely cosmetic now
                bordercolor="rgba(255,255,255,0.12)",
            ),
            hoverdistance=20,  # cursor → nearest point tolerance
            spikedistance=-1,  # spike follows cursor, not nearest point
            margin=dict(l=60, r=20, t=70, b=60),
        )

        # vertical cursor line
        fig.update_xaxes(
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikethickness=1,
            spikecolor="#bbbbbb",
            spikedash="dot",
        )

        st.plotly_chart(
            fig, use_container_width=True, config={"displaylogo": False}, theme=None
        )

    # ---------------------- TABLE (right) ----------------------
    with col2:
        options = list(dmg_dict.keys())
        sel = st.selectbox("Index Log", options, format_func=lambda x: plot_labels[x])
        if sel is not None:
            st.dataframe(
                dmg_dict[sel]["Dmg"].round(2),
                hide_index=True,
                column_config={"Total Dmg": None},
                use_container_width=True,
            )


def frameRate(key):
    fps = st.radio(
        "Frame Rate (60 = double the runtime): Leave at 30 fps",
        [30, 60],
        key=key,
        index=0,
        horizontal=True,
    )
    return fps


def items_list(items, default_item="NoItem", num_items=3):
    """
    Items list: Display select boxes for choosing items by display name,
    but return the corresponding class names.
    """
    # Mapping: {DisplayName: ClassName}
    display_map = item_display_map(items)

    # Get the lists separately for clarity
    display_names = list(display_map.keys())

    # --- default handling ---
    def reset_items():
        for i in range(1, num_items + 1):
            st.session_state[f"Items{i}"] = default_item

    for i in range(1, num_items + 1):
        key = f"Items{i}"
        if key not in st.session_state:
            st.session_state[key] = default_item

    # --- UI rendering ---
    item_buttons = []
    for n in range(1, num_items + 1):
        # Find the current selected display name
        current_class = st.session_state[f"Items{n}"]
        current_display = next(
            (disp for disp, cls in display_map.items() if cls == current_class),
            list(display_map.keys())[0],  # fallback to first
        )

        selected_display = st.selectbox(
            f"Item {n}",
            display_names,
            index=(
                display_names.index(current_display)
                if current_display in display_names
                else 0
            ),
            key=f"Items{n}_display",
        )

        # Convert back to class name
        selected_class = display_map[selected_display]
        st.session_state[f"Items{n}"] = selected_class
        item_buttons.append(selected_class)

    st.button("Reset items", on_click=reset_items)
    return item_buttons


def enemy_list(key):
    """Enemy list: Configure the base stats of the enemy: HP, Armor, and MR

    Args:
        key (string): unique key for streamlit

    Returns:
        Champion: a champion with the requested hp, armor, and mr
    """
    st.header("Enemy")

    col1, col2, col3 = st.columns(3)
    with col1:
        hp = st.number_input(
            "Enemy HP", min_value=1, max_value=99999, value=1800, key=key + "1"
        )
    with col2:
        armor = st.number_input(
            "Enemy Armor", min_value=0, max_value=99999, value=100, key=key + "2"
        )
    with col3:
        mr = st.number_input(
            "Enemy MR", min_value=0, max_value=99999, value=100, key=key + "3"
        )
    enemy = DummyTank(1)
    enemy.hp.base = hp
    enemy.armor.base = armor
    enemy.mr.base = mr
    return enemy


def first_takedown(key, champ):
    # st.subheader("First takedown")
    first_takedown = st.number_input(
        "Time of first takedown", min_value=1, max_value=30, value=5, key=key
    )
    champ.first_takedown = first_takedown


def total_takedowns(key, champ):
    takedowns = st.number_input(
        "Total takedowns", min_value=0, max_value=100, value=0, key=key
    )
    champ.takedowns = takedowns


def bonus_stats(key, champ):
    """Enemy list: Configure the base stats of the enemy: HP, Armor, and MR

    Args:
        key (string): unique key for streamlit

    Returns:
        Champion: a champion with the requested hp, armor, and mr
    """

    # st.subheader("First takedown")
    cols = st.columns(3)
    with cols[0]:
        ad_bonus = st.number_input(
            "Bonus AD", min_value=0, max_value=2000, value=0, key=key + "ad"
        )
        dmgamp_bonus = st.number_input(
            "DmgAmp", min_value=0, max_value=1000, value=0, key=key + "dmgamp"
        )
        manaregen_bonus = st.number_input(
            "ManaRegen", min_value=0, max_value=10, value=0, key=key + "manaregen"
        )
    with cols[1]:
        ap_bonus = st.number_input(
            "Bonus AP", min_value=0, max_value=2000, value=0, key=key + "ap"
        )
        crit_bonus = st.number_input(
            "Bonus Crit", min_value=0, max_value=200, value=0, key=key + "crit"
        )
        mpa_bonus = st.number_input(
            "ManaPerAuto", min_value=0, max_value=15, value=0, key=key + "mpa"
        )
    with cols[2]:
        as_bonus = st.number_input(
            "Bonus AS", min_value=0, max_value=200, value=0, key=key + "AS"
        )
        crit_dmg_bonus = st.number_input(
            "CritDmg", min_value=0, max_value=200, value=0, key=key + "critdmg"
        )

    # with col2:
    #   crit_bonus = st.number_input('Bonus Crit',
    #                                    min_value=0, max_value=200,
    #                                    value=0, key=key + "crit")
    #   crit_dmg_bonus = st.number_input('Bonus Crit Dmg',
    #                                    min_value=0, max_value=200,
    #                                    value=0, key=key + "critdmg")
    champ.bonus_ad.addStat(ad_bonus)
    champ.ap.addStat(ap_bonus)
    champ.aspd.addStat(as_bonus)
    champ.manaRegen.addStat(manaregen_bonus)
    champ.manaPerAttack.addStat(mpa_bonus)
    champ.dmgMultiplier.addStat(dmgamp_bonus / 100)
    champ.crit.addStat(crit_bonus / 100)
    champ.critDmg.addStat(crit_dmg_bonus / 100)


def num_traits(key, champ):
    """num traits

    Args:
        key (string): unique key for streamlit

    Returns:
        Champion: a champion with the requested hp, armor, and mr
    """

    # st.subheader("Number of traits")
    traits = st.number_input(
        "Number of active traits", min_value=0, max_value=12, value=6, key=key
    )
    champ.num_traits = traits


def add_buffs(champ, buffs, add_noitem=False):
    for (
        buff,
        level,
        extraParams,
    ) in buffs:
        if buff != "NoBuff" or add_noitem:
            champ.items.append(
                utils.class_for_name("set15buffs", buff)(level, extraParams)
            )


def add_powerup(champ, powerup):
    champ.items.append(utils.class_for_name("set15powerups", powerup)(1, []))


def mentor_selector(champion):
    st.header("Mentor Buffs")
    item_cols = st.columns(3)

    mentors = {"Udyr": False, "Yasuo": False, "Ryze": False}

    for index, name in enumerate(list(mentors.keys())):
        with item_cols[index]:
            champ_mentors = champion.name == name
            mentors[name] = st.checkbox(name, value=champ_mentors)
    champion.mentors = mentors


def starguardian_selector(champion):
    """Select which Star Guardians will be enabled

    Args:
        champion (Champion): Champion selected
          Their Star guardian will be set to true.
    """
    st.header("Star Guardian Buffs")
    item_cols = st.columns(3)

    star_guardians = {
        "Syndra": False,
        "Xayah": False,
        "Ahri": False,
        "Poppy": False,
        "Neeko": False,
        "Rell": False,
        "Jinx": False,
        "Seraphine": False,
        "Emblem": False,
        "Emblem 2": False,
    }

    for index, name in enumerate(list(star_guardians.keys())):
        with item_cols[index % 3]:
            champ_stargs = champion.name == name
            star_guardians[name] = st.checkbox(name, value=champ_stargs)
    champion.star_guardians = star_guardians


def champ_selector(champ_list):
    """champ list: select da champion

    Args:
        key (string): unique key for streamlit

    Returns:
        Champion: a champion with the requested hp, armor, and mr
    """
    st.header("Champion")
    item_cols = st.columns([3, 1])

    with item_cols[0]:
        # index 1 cuz we're not starting on akali
        champ = st.selectbox("Champion", champ_list, index=1)
    with item_cols[1]:
        levels = [1, 2, 3]
        if utils.class_for_name("set15champs", champ).canFourStar:
            levels.append(4)
        champlevel = st.selectbox("Level", levels, index=1)

    new_champ = utils.class_for_name("set15champs", champ)(champlevel)
    return new_champ
    return new_champ
