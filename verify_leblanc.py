import sys
import os

# Add the current directory to sys.path so we can import local modules
sys.path.append(os.getcwd())

from set17champs import Leblanc
from champion import Champion
from stats import Attack
from role import Role
import set17buffs as buffs

def verify_leblanc():
    print("Verifying LeBlanc (Set 17)...")
    
    # Initialize LeBlanc level 2
    leblanc = Leblanc(2)
    print(f"Initial Stats: AS={leblanc.aspd.stat}, Mana={leblanc.curMana}/{leblanc.fullMana.stat}, AP={leblanc.ap.stat}")
    
    assert leblanc.aspd.stat == 0.8, f"Expected AS 0.8, got {leblanc.aspd.stat}"
    assert leblanc.fullMana.stat == 40, f"Expected Mana 40, got {leblanc.fullMana.stat}"
    
    # Dummy opponents
    dummy = Champion("Dummy", 10000, 0, 0, 100, 0.5, 0, 0, 1, Role.TANK)
    leblanc.opponents = [dummy]
    
    time = 1.0
    
    # 1. Test Passive Magic Damage
    print("Testing Passive Magic Damage...")
    attack = Attack()
    attack.opponents = [dummy]
    
    # Find the LeblancUlt buff
    lb_buff = next(i for i in leblanc.items if isinstance(i, buffs.LeblancUlt))
    
    # Call preAttack to set up attack parameters
    lb_buff.performAbility("preAttack", time, leblanc, attack)
    
    assert attack.attackType == "magical", f"Expected magical attack, got {attack.attackType}"
    
    # Level 2 Passive scaling is 96.
    expected_dmg = 96 * leblanc.ap.stat
    actual_dmg = attack.scaling(2, 0, 1.0, leblanc.ap.stat)
    print(f"Passive Damage: Expected {expected_dmg}, Actual {actual_dmg}")
    assert abs(actual_dmg - expected_dmg) < 0.01
    
    # 2. Test Ability Cast
    print("Testing Ability Cast...")
    leblanc.curMana = 40
    # Use update to trigger the full cast logic (mana reset, manalock, etc)
    leblanc.update([dummy], [], time)
    
    assert leblanc.curMana == 0, f"Expected mana 0 after cast, got {leblanc.curMana}"
    assert leblanc.active == True, "LeBlanc should be in active state after cast"
    assert leblanc.activeAttacksLeft == 5, f"Expected 5 active attacks left, got {leblanc.activeAttacksLeft}"
    assert leblanc.manalockTime > time, "LeBlanc should be manalocked"

    # 3. Test Active Attacks and Clones
    print("Testing Active Attacks...")
    
    for i in range(1, 6):
        print(f"Attack {i}...")
        
        # Check manalock
        leblanc.addMana(10, time)
        assert leblanc.curMana == 0, f"LeBlanc should be manalocked during active (Attack {i})"
        
        initial_dmg_dealt = leblanc.dmgDealt
        attack = Attack()
        attack.opponents = [dummy]
        
        lb_buff.performAbility("preAttack", time, leblanc, attack)
        
        if i < 5:
            expected_clone_dmg = 25 * leblanc.ap.stat * 5
        else:
            expected_bolt_dmg = 105 * leblanc.ap.stat * 5
            
        dmg_delta = leblanc.dmgDealt - initial_dmg_dealt
        print(f"Clone Damage Dealt on Attack {i}: {dmg_delta}")
        
        if i < 5:
            assert abs(dmg_delta - (25 * 5)) < 0.1
        else:
            assert abs(dmg_delta - (105 * 5)) < 0.1
            
        assert leblanc.activeAttacksLeft == (5 - i)

    assert leblanc.active == False, "Active should be False after 5 attacks"
    
    # Check manualock end
    leblanc.addMana(10, time + 1.0)
    assert leblanc.curMana == 10, f"LeBlanc should gain mana after active ends. Got {leblanc.curMana}"
    
    print("Verification Passed!")

if __name__ == "__main__":
    verify_leblanc()
