import sys
import os

# Add parent directory to path to import set17 modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from set17.set17champs import Kaisa
from set17.champion import Champion
from set17.role import Role
import set17.set17buffs as buffs

def verify_kaisa():
    print("Verifying Kai'Sa...")
    
    # Initialize Kai'Sa Level 2
    kaisa = Kaisa(2)
    print(f"Initial Stats: AD={kaisa.atk.stat}, AS={kaisa.aspd.stat}, Mana={kaisa.curMana}/{kaisa.fullMana.stat}")
    
    # 2-star AD should be 67.5 (45 * 1.5)
    assert kaisa.atk.stat == 67.5, f"Expected AD 67.5, got {kaisa.atk.stat}"
    assert kaisa.aspd.stat == 0.8, f"Expected AS 0.8, got {kaisa.aspd.stat}"
    
    # 1. Verify Ability Damage (No items/buffs)
    # Give full mana to force cast
    kaisa.curMana = 50
    # Dummy opponent with 0 resistance
    dummy = Champion("Dummy", 10000, 0, 0, 100, 0.5, 0, 0, 1, Role.TANK)
    kaisa.opponents = [dummy]
    
    time = 1.0
    initial_dmg = kaisa.dmgDealt
    print("Casting Bullet Cluster...")
    kaisa.performAbility(kaisa.opponents, kaisa.items, time)
    
    dmg_dealt = kaisa.dmgDealt - initial_dmg
    print(f"Total Ability Damage (2-star): {dmg_dealt}")
    # Expected: 16 missiles * 60 damage each = 960
    # 68 * 0.8 = 54.4 -> 54 AD part. 100 * 0.06 = 6. Total 60.
    # 16 * 60 = 960.
    assert 959 < dmg_dealt < 961, f"Expected ~960 damage, got {dmg_dealt}"

    # 2. Verify Rogue Trait
    print("Testing Rogue 2 (15% AD/AP)...")
    rogue2 = buffs.Rogue(2, 0)
    # Rogue applies at preCombat
    rogue2.performAbility("preCombat", 0, kaisa)
    
    # 68 (base) * 1.15 = 78.2
    # Wait, Stat.stat increases base by addMultiplier?
    # AD.mult starts at 1. addStat(15) adds 15/100=0.15 to mult.
    # So mult becomes 1.15. atk.stat returns base (68).
    # Wait, Champion uses atk.stat in scaling and doDamage.
    # Let's check AD.stat property in stats.py.
    # line 53 in stats.py: "return self.base". 
    # WAIT! AD.stat ONLY returns self.base?
    # Ah, let's look at stats.py line 53 again.
    # 52:     @property
    # 53:     def stat(self):
    # 54:         return self.base
    # THIS IS WRONG? If I add stats, it doesn't change `stat`?
    # Let's look at how AD is used.
    # In `Champion.doAttack`: `scaling(self.level, self.atk.stat, self.bonus_ad.stat, self.ap.stat)`
    # So `atk.stat` (base AD) is passed to scaling.
    # And `bonus_ad.stat` (multiplier) is passed to scaling.
    # So `bonus_ad` handles the percentage increase.
    # My Rogue implementation added to `bonus_ad`.
    # kaisa.bonus_ad.stat should be 1.15 now.
    
    print(f"Bonus AD Mult: {kaisa.bonus_ad.stat}, AP Stat: {kaisa.ap.stat}")
    assert round(kaisa.bonus_ad.stat, 2) == 1.15, f"Expected 1.15 bonus AD, got {kaisa.bonus_ad.stat}"
    assert round(kaisa.ap.stat, 2) == 1.15, f"Expected 1.15 AP, got {kaisa.ap.stat}"

    # 3. Verify Dark Star Trait
    print("Testing Dark Star 4 (33% AD/AP)...")
    # Reset stats for clean test
    kaisa = Kaisa(2)
    ds4 = buffs.DarkStar(4, 0)
    ds4.performAbility("preCombat", 0, kaisa)
    print(f"Bonus AD Mult: {kaisa.bonus_ad.stat}")
    assert round(kaisa.bonus_ad.stat, 2) == 1.33, f"Expected 1.33 bonus AD, got {kaisa.bonus_ad.stat}"
    
    print("Testing Dark Star 6 + Supermassive (66% AD/AP)...")
    kaisa = Kaisa(2)
    ds6 = buffs.DarkStar(6, 1) # Supermassive = 1
    ds6.performAbility("preCombat", 0, kaisa)
    print(f"Bonus AD Mult: {kaisa.bonus_ad.stat}")
    assert round(kaisa.bonus_ad.stat, 2) == 1.66, f"Expected 1.66 bonus AD, got {kaisa.bonus_ad.stat}"

    print("Verification Passed!")

if __name__ == "__main__":
    verify_kaisa()
