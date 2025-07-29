import sys
sys.path.append("..")
import set15_streamlit_main
import streamlit as st
import set15items
import set15buffs
from role import Role
import set15champs
import class_utilities
import pandas as pd
import numpy as np
import copy
import itertools
import utils
import inspect

st.set_page_config(layout="wide")

t = 30
simLists = []
simDict = {}

mana_items = set15items.mana_items + set15items.no_item

with st.sidebar:
    st.header("Held item")
    items = class_utilities.items_list(mana_items, num_items = 2)

    # Role
    role = st.selectbox(
            'Role',
             [Role.CASTER.value, Role.MARKSMAN.value], key="rolez", index=0)
    
    castTime = st.number_input("Cast Time", min_value=0.0, max_value=3.0, value=0.5, key="casts")

    col1, col2, = st.columns(2)

    with col1:
        totalMana = st.number_input("Total Mana", min_value=10, max_value=140, value=50, key="totalmana")
        baseAS = st.number_input("Base AS", min_value = 0.5, max_value = 1.0, value=0.7, key="baseAS")
        baseAD = st.number_input("Base AD", min_value = 0, max_value = 1000, value=0, key="baseAD")
        manaRegen = st.number_input("Mana Regen", min_value = 0, max_value = 20, value=0, key="manaRegen")
    with col2:
        startingMana = st.number_input("Start Mana", min_value=0, max_value=totalMana, value=0, key="startmana")
        bonusAS = st.number_input("Bonus AS", min_value = 0, max_value = 1000, value=0, key="bonusAS")
        spellDmg = st.number_input("Spell Damage", min_value = 0, max_value = 1000, value=100, key="Spell Damage")

    new_champ = set15champs.BaseChamp(1)
    new_champ.role = Role(role)
    new_champ.castTime = castTime
    new_champ.fullMana.base = totalMana
    new_champ.curMana = startingMana
    new_champ.manaRegen.add += manaRegen
    
    new_champ.aspd.base = baseAS
    new_champ.aspd.add = bonusAS

    new_champ.atk.base = baseAD
    new_champ.ap_scale = spellDmg

    # Add items to Champion
    for item in items:
        if item != 'NoItem':
            new_champ.items.append(utils.class_for_name('set15items', item)())
            new_champ.item_count += 1

    enemy = set15champs.ZeroResistance(1)
    champ_before_sims = copy.deepcopy(new_champ)
    set15_streamlit_main.doExperimentOneExtraWrapped.clear()
simLists = set15_streamlit_main.doExperimentOneExtra(new_champ, enemy,
        utils.convertStrList('set15items', mana_items),
        [], t)

# print(simLists[0])

itemSimulator = set15_streamlit_main.Simulator()
itemSimulator.itemStats(champ_before_sims.items, champ_before_sims)

class_utilities.write_champion(champ_before_sims)

# checkboxes

display_dps = st.checkbox("Display DPS", value=False)

# options = ["Craftable"]
# if len([item for item in items if item != 'NoItem']) >= 3:
#     options = ["Trait", "Augment/Buff"]

# radio_value = st.radio("",
#                         options, index=0, horizontal=True)

df = set15_streamlit_main.createSelectorDPSTable(simLists)
df_flt = df


# if radio_value == "Craftable":
#     df_flt = df_flt[df_flt['Extra class name'].isin(craftables + ['NoItem'])]
# if radio_value == "Artifact":
#     df_flt = df_flt[df_flt['Extra class name'].isin(set15items.artifacts+['NoItem'])]
# if radio_value == "Radiant":
#     df_flt = df_flt[df_flt['Extra class name'].isin(set15items.radiants+['NoItem'])]
# if radio_value == "Trait":
#     df_flt = df_flt[df_flt['Extra class name'].isin([x[0] for x in buffs]+['NoItem'])]
# if radio_value == "Augment/Buff":
#     df_flt = df_flt[df_flt['Extra class name'].isin(set15buffs.augments+ ['NoItem'])]

new_df = df_flt.drop(['Extra class name', 'Name', 'Level'], axis=1)

if not display_dps:
    new_df = new_df.drop(['Extra DPS ({}s)'.format(i) for i in [5, 10, 15, 20]], axis=1)
else:
    new_df = new_df.drop(['DPS at {}'.format(i) for i in [5, 10, 15, 20, 25]], axis=1)

class_utilities.plot_df(new_df, simLists)