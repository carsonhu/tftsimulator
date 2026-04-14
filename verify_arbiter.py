import sys
import os

# Add the current directory to sys.path so we can import local modules
sys.path.append(os.getcwd())

from set17champs import Leblanc
from champion import Champion
import set17buffs as buffs
from role import Role

def verify_arbiter():
    print("Verifying Arbiter Logic (Attack Cause)...")
    
    time = 1.0
    
    # 1. Test Gain AS
    print("\nTesting Gain AS...")
    leblanc = Leblanc(2) # Level 2 champion
    leblanc.cause = "When an Arbiter attacks 3 times"
    leblanc.effect = "Gain AS"
    
    # Dummy opponents
    dummy = Champion("Dummy", 10000, 0, 0, 100, 0.5, 0, 0, 1, Role.TANK)
    leblanc.opponents = [dummy]
    
    # Add Arbiter trait (Level 2)
    arbiter_trait = buffs.Arbiter(2, 4)
    leblanc.items.append(arbiter_trait)
    
    # Trigger preCombat to add ArbiterAttack buff
    arbiter_trait.performAbility("preCombat", time, leblanc)
    
    # Verify ArbiterAttack is added
    assert any(isinstance(i, buffs.ArbiterAttack) for i in leblanc.items), "ArbiterAttack buff not found"
    
    initial_as = leblanc.aspd.add
    print(f"Initial Bonus AS: {initial_as}")
    
    # Mock some attacks
    for i in range(1, 4):
        leblanc.startAttack(leblanc.opponents, leblanc.items, time + i)
        print(f"Attack {i}, Bonus AS: {leblanc.aspd.add}")
    
    # Level 2 AS gain is 3
    assert leblanc.aspd.add == initial_as + 3, f"Expected {initial_as + 3} AS, got {leblanc.aspd.add}"
    
    # 2. Test Gain AP (Level 3 Trait)
    print("\nTesting Gain AP (Level 3)...")
    leblanc = Leblanc(2)
    leblanc.cause = "When an Arbiter attacks 3 times"
    leblanc.effect = "Gain AP"
    leblanc.opponents = [dummy]
    arbiter_trait = buffs.Arbiter(3, 4)
    leblanc.items.append(arbiter_trait)
    arbiter_trait.performAbility("preCombat", time, leblanc)
    
    initial_ap = leblanc.ap.add
    for i in range(1, 4):
        leblanc.startAttack(leblanc.opponents, leblanc.items, time + i)
    
    # Level 3 AP gain is 9
    assert leblanc.ap.add == initial_ap + 9, f"Expected {initial_ap + 9} AP, got {leblanc.ap.add}"

    # 3. Test Gain Mana (Manalock Bypass)
    print("\nTesting Gain Mana (Manalock Bypass)...")
    leblanc = Leblanc(2)
    leblanc.cause = "When an Arbiter attacks 3 times"
    leblanc.effect = "Gain mana"
    leblanc.opponents = [dummy]
    arbiter_trait = buffs.Arbiter(2, 4)
    leblanc.items.append(arbiter_trait)
    arbiter_trait.performAbility("preCombat", time, leblanc)
    
    # Put Leblanc in manalock
    leblanc.manalockTime = time + 10.0
    leblanc.curMana = 0
    
    print(f"Attempting to add mana while manalocked (Lock until {leblanc.manalockTime})")
    for i in range(1, 4):
        leblanc.startAttack(leblanc.opponents, leblanc.items, time + i)
        print(f"Attack {i}, Mana: {leblanc.curMana}")
    
    # Level 2 Mana gain is 7. Since it bypasses lock, it should be 7.
    assert leblanc.curMana == 7, f"Expected 7 mana despite manalock, got {leblanc.curMana}"

    # 4. Test Periodic Gain AS
    print("\nTesting Every 4 seconds (Gain AS)...")
    leblanc = Leblanc(2)
    leblanc.cause = "Every 4 seconds"
    leblanc.effect = "Gain AS"
    leblanc.opponents = [dummy]
    arbiter_trait = buffs.Arbiter(2, 4)
    leblanc.items.append(arbiter_trait)
    arbiter_trait.performAbility("preCombat", 0, leblanc)
    
    initial_as = leblanc.aspd.add
    # Simulate updates
    leblanc.update([dummy], leblanc.items, 3.9)
    assert leblanc.aspd.add == initial_as
    
    leblanc.update([dummy], leblanc.items, 4.0)
    print(f"Time 4.0, Bonus AS: {leblanc.aspd.add}")
    assert leblanc.aspd.add == initial_as + 11
    
    leblanc.update([dummy], leblanc.items, 7.9)
    assert leblanc.aspd.add == initial_as + 11
    
    leblanc.update([dummy], leblanc.items, 8.0)
    print(f"Time 8.0, Bonus AS: {leblanc.aspd.add}")
    assert leblanc.aspd.add == initial_as + 22

    # 5. Test Interest Gain AP
    print("\nTesting Combat Start: Interest (Gain AP)...")
    leblanc = Leblanc(2)
    leblanc.cause = "Combat Start: For each interest you would gain"
    leblanc.effect = "Gain AP"
    leblanc.opponents = [dummy]
    arbiter_trait = buffs.Arbiter(2, 4)
    leblanc.items.append(arbiter_trait)
    
    initial_ap = leblanc.ap.add
    # preCombat on trait adds the buff
    arbiter_trait.performAbility("preCombat", 0, leblanc)
    # preCombat on the added buff applies the stats
    interest_buff = next(i for i in leblanc.items if isinstance(i, buffs.ArbiterInterest))
    interest_buff.performAbility("preCombat", 0, leblanc)
    
    print(f"AP after interest proc: {leblanc.ap.add}")
    assert leblanc.ap.add == initial_ap + 40

    # 6. Test Reroll Gain AS
    print("\nTesting Combat start: Reroll (Gain AS)...")
    leblanc = Leblanc(2)
    leblanc.cause = "Combat start: If you rerolled"
    leblanc.effect = "Gain AS"
    leblanc.opponents = [dummy]
    arbiter_trait = buffs.Arbiter(2, 4)
    leblanc.items.append(arbiter_trait)
    
    initial_as = leblanc.aspd.add
    # preCombat on trait adds the buff
    arbiter_trait.performAbility("preCombat", 0, leblanc)
    # preCombat on the added buff applies the stats
    reroll_buff = next(i for i in leblanc.items if isinstance(i, buffs.ArbiterReroll))
    reroll_buff.performAbility("preCombat", 0, leblanc)
    
    print(f"AS after reroll proc: {leblanc.aspd.add}")
    assert leblanc.aspd.add == initial_as + 30

    # 7. Test Mana Spent Gain AP
    print("\nTesting When an Arbiter spends 50 mana (Gain AP)...")
    leblanc = Leblanc(2)
    leblanc.fullMana.base = 100 # Set base to 100 to ensure 2 procs (50*2)
    leblanc.cause = "When an Arbiter spends 50 mana"
    leblanc.effect = "Gain AP"
    leblanc.opponents = [dummy]
    arbiter_trait = buffs.Arbiter(2, 4)
    leblanc.items.append(arbiter_trait)
    
    initial_ap = leblanc.ap.add
    # preCombat on trait adds the buff
    arbiter_trait.performAbility("preCombat", 0, leblanc)
    mana_spent_buff = next(i for i in leblanc.items if isinstance(i, buffs.ArbiterManaSpent))
    
    # Simulate a cast (100 mana spent)
    mana_spent_buff.performAbility("postAbility", 1.0, leblanc)
    
    # 100 mana spent = 2 procs of 16 AP = 32
    print(f"AP after spending 100 mana (2 procs): {leblanc.ap.add}")
    assert leblanc.ap.add == initial_ap + 32

    # 8. Test Star Level Gain AP
    print("\nTesting Combat Start: Star Level (Gain AP)...")
    leblanc = Leblanc(2)
    leblanc.cause = "Combat Start: For each Arbiter star level"
    leblanc.effect = "Gain AP"
    leblanc.opponents = [dummy]
    # Trait level 3, Star levels parameter = 4
    arbiter_trait = buffs.Arbiter(3, 4)
    leblanc.items.append(arbiter_trait)
    
    initial_ap = leblanc.ap.add
    # preCombat on trait adds the buff
    arbiter_trait.performAbility("preCombat", 0, leblanc)
    # preCombat on the added buff applies the stats
    star_level_buff = next(i for i in leblanc.items if isinstance(i, buffs.ArbiterStarLevel))
    star_level_buff.performAbility("preCombat", 0, leblanc)
    
    # Logic: Level 3 AP = 5 per star level. 5 * 4 = 20.
    print(f"AP after star level proc (5 * 4): {leblanc.ap.add}")
    assert leblanc.ap.add == initial_ap + 20

    # 9. Test Deal Damage Gain AP
    print("\nTesting When an Arbiter deals damage 10 times (Gain AP)...")
    leblanc = Leblanc(2)
    leblanc.cause = "When an Arbiter deals damage 10 times"
    leblanc.effect = "Gain AP"
    leblanc.opponents = [dummy]
    arbiter_trait = buffs.Arbiter(2, 4)
    leblanc.items.append(arbiter_trait)
    
    initial_ap = leblanc.ap.add
    # preCombat on trait adds the buff
    arbiter_trait.performAbility("preCombat", 0, leblanc)
    deal_dmg_buff = next(i for i in leblanc.items if isinstance(i, buffs.ArbiterDealDamage))
    
    # Simulate 10 instances of damage
    for i in range(1, 11):
        deal_dmg_buff.performAbility("PostOnDealDamage", 1.0, leblanc)
    
    # 10 instances = 1 proc of 4 AP (for Level 2)
    print(f"AP after 10 damage instances: {leblanc.ap.add}")
    assert leblanc.ap.add == initial_ap + 4

    print("\nArbiter Logic Verification Passed!")

if __name__ == "__main__":
    verify_arbiter()
