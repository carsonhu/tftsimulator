# streamlit_page_name: "Darth Noob's TFT Simulator"
# streamlit_page_icon: "👋"


import streamlit as st

st.set_page_config(
    page_title="Darth Noob's TFT Simulator",
    page_icon="👋",
)


st.title("Darth Noob's TFT Simulator")

st.markdown(
    """
    This is Darth Noob (Nub)'s Teamfight Tactics Damage Simulator.
    Click on the 'Champion Selector' page and to calculate a unit's DPS.

    This tool is invaluable if you want to have a good idea of what different powerups / items / augments do to empower your champion.

    Do not trust this simulator as gospel: If the stats or intuition conflict
    with the simulator, you should likely trust the stats or your intuition.

    In particular, the main areas where the simulator will suffer:

    * **Mana regen**: Manalock time isn't perfectly calculated, so it will be slightly off compared to live.
    * **Cast times**: Some champs (like Gangplank) have cast times that scale with AS. Others have flat
    cast times. While I have manually recorded every champ's cast time, I don't know exactly which ones scale with AS.
    * **Assumptions**: Certain assumptions have to be made to simulate some buffs.
    For instance, edgelord is calculated as a flat +20% AS.
    
    * **Human error**: sometimes I may have just coded something incorrectly, or missed a patch note. oops.

    Nonetheless, I use this tool every day and consider to be invaluable to getting better as a TFT player.

    \- Darth Noob
"""
)
