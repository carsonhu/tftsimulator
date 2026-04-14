import sys
import os

# Add parent directory to path to import local modules
sys.path.append(os.getcwd())

import sim_core
from set17champs import Leblanc
from champion import Champion
from role import Role
import set17buffs
import set17items


def test_scaling():
    print("Testing Arbiter Level Scaling in do_experiment_one_extra...")
    
    # 1. Setup Champion with Arbiter level 2
    leblanc = Leblanc(2)
    leblanc.cause = "Combat Start: For each Arbiter star level"
    leblanc.effect = "Gain AP"
    
    # Add level 2 trait
    arbiter_trait = set17buffs.Arbiter(2, 6) # 6 star levels
    leblanc.items.append(arbiter_trait)
    
    # Add GuinsoosRageblade and Archangels (to match screenshot)
    leblanc.items.append(set17items.GuinsoosRageblade())
    leblanc.items.append(set17items.Archangels())

    
    dummy = Champion("Dummy", 10000, 0, 0, 100, 0.5, 0, 0, 1, Role.TANK)
    
    # 2. Run experiment with NoItem and other Arbiter levels in buff_list
    # duration 25.0, frame_rate 30
    no_item = set17items.NoItem()
    
    # Simulate what ChampionSelector.py does: add other levels to extra_buffs
    extra_levels = [0, 3]
    extra_buffs = [set17buffs.Arbiter(lvl, 6) for lvl in extra_levels]
    
    sim_results = sim_core.do_experiment_one_extra(leblanc, dummy, [no_item], extra_buffs, 25.0, 30)


    
    # 3. Analyze results
    for res in sim_results:
        extra_name = res["Extra"].name
        champ = res["Champ"]
        
        # Results are in champ.dmgVector
        total_dmg = sum(d[1][0] for d in champ.dmgVector)
        
        # Check AP at the end
        print(f"Combination: {extra_name}")
        print(f" - Final AP Add: {champ.ap.add}")
        print(f" - Total Damage: {total_dmg:.2f}")

    # Expected AP Add:
    # Baseline (Arbiter 2): 10 (Guinsoo) + 20 (Archangel) + (3 * 6 = 18) = 48
    # NoItem row should represent Arbiter 2.
    
    # Arbiter 3 row:
    # Extra should be Arbiter(3, 6)
    # AP Add: 10 + 20 + (5 * 6 = 30) = 60
    
    # Arbiter 0 row:
    # AP Add: 10 + 20 + 0 = 30

if __name__ == "__main__":
    test_scaling()
