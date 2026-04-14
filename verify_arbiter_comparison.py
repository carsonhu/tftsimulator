import sys
import os

# Add parent directory to path to import local modules
sys.path.append(os.getcwd())

import sim_core
from set17champs import Leblanc
from champion import Champion
from role import Role
import set17buffs

def verify_comparison():
    print("Verifying Arbiter Comparison Generation...")
    
    # 1. Setup Champion with Arbiter level 2
    leblanc = Leblanc(2)
    # Arbiter trait must be in items to trigger the logic
    # In the app, arbiter_selector and add_buffs handle this.
    arbiter_trait = set17buffs.Arbiter(2, 4)
    leblanc.items.append(arbiter_trait)
    
    dummy = Champion("Dummy", 1000, 0, 0, 100, 0.5, 0, 0, 1, Role.TANK)
    
    # 2. Run experiment with NoItem and empty buff list
    # duration 1.0, frame_rate 30
    import set17items
    no_item = set17items.NoItem()
    sim_results = sim_core.do_experiment_one_extra(leblanc, dummy, [no_item], [], 1.0, 30)

    
    # Baseline: Leblanc starts with one item (Arbiter trait)
    # do_experiment_one_extra returns sim_list
    
    arbiter_extras = [res["Extra"].name for res in sim_results if " | " in res["Extra"].name or res["Extra"].name == "Other"]
    
    print(f"Total Arbiter Combinations: {len(arbiter_extras)}")
    for name in arbiter_extras:
        print(f" - {name}")
    
    # 3. Validation
    
    # Check "Other" count
    others = [n for n in arbiter_extras if n == "Other"]
    assert len(others) == 1, f"Expected 1 'Other', got {len(others)}"
    
    # Check "Gain Mana" non-functional cases (Interest, Reroll, Deal Damage)
    # These should be skipped
    mana_interest = [n for n in arbiter_extras if "Gain interest | Gain mana" in n]
    mana_reroll = [n for n in arbiter_extras if "Reroll | Gain mana" in n]
    mana_damage = [n for n in arbiter_extras if "Deal Damage 10 times | Gain mana" in n]
    
    assert len(mana_interest) == 0, "Gain interest | Gain mana should be skipped"
    assert len(mana_reroll) == 0, "Reroll | Gain mana should be skipped"
    assert len(mana_damage) == 0, "Deal Damage 10 times | Gain mana should be skipped"
    
    # Total expected: 
    # 1 (Other)
    # 7 (AS)
    # 7 (AP)
    # 4 (Mana: Attack3, Periodic, 50Mana, StarLevel)
    # = 19
    assert len(arbiter_extras) == 19, f"Expected 19 combinations, got {len(arbiter_extras)}"
    
    # Check baseline (NoItem)
    baselines = [res["Extra"].name for res in sim_results if res["Extra"].name == "NoItem"]
    assert len(baselines) == 1, "Should have one NoItem baseline"

    print("\nArbiter Comparison Verification Passed!")

if __name__ == "__main__":
    verify_comparison()
