import set17champs as champs
import set17buffs as buffs
from stats import Stat

def test_viktor_stats():
    print("Testing Viktor Stats...")
    v = champs.Viktor(level=1)
    assert v.hp.base == 650
    assert v.atk.stat == 30
    assert v.curMana == 20
    assert v.fullMana.stat == 80
    assert v.aspd.stat == 0.80
    assert v.armor.stat == 25
    assert v.mr.stat == 25
    print("Viktor Stats Passed!")

def test_viktor_ability():
    print("Testing Viktor Ability...")
    v = champs.Viktor(level=1)
    # Give full mana
    v.curMana = v.fullMana.stat
    
    enemy1 = champs.DummyTank(level=1) # 100 Armor, 100 MR
    enemy2 = champs.DummyTank(level=1)
    opponents = [enemy1, enemy2]
    
    # Start cast at t=0
    v.update(opponents, [], 0)
    
    # Check timings
    assert abs(v.manalockTime - 4.0) < 0.001, f"Expected manalockTime 4.0, got {v.manalockTime}"
    assert abs(v.nextAttackTime - 4.5) < 0.001, f"Expected nextAttackTime 4.5, got {v.nextAttackTime}"
    
    # Check ticks
    # Tick 1 at t=1.0
    v.update(opponents, [], 1.0)
    assert len(v.dmgVector) == 2, f"Expected 2 hits at t=1.0, got {len(v.dmgVector)}"
    
    # Damage calculation:
    # Scale Level 1: 240 magical
    # enemy1 (primary): 240 * (100/(100+100)) = 120
    # enemy2 (secondary): 240 * 0.6 * (100/(100+100)) = 72
    # Total hit 1: 192
    
    hit1_dmg = sum(hit[1][0] for hit in v.dmgVector)
    assert abs(hit1_dmg - 192) < 0.001, f"Expected 192 dmg at t=1.0, got {hit1_dmg}"
    
    # Tick 2 at t=2.0
    v.update(opponents, [], 2.0)
    assert len(v.dmgVector) == 4, f"Expected 4 total hits at t=2.0, got {len(v.dmgVector)}"
    
    # Tick 3 at t=3.0
    v.update(opponents, [], 3.0)
    assert len(v.dmgVector) == 6, f"Expected 6 total hits at t=3.0, got {len(v.dmgVector)}"
    
    # Tick 4 at t=4.0
    v.update(opponents, [], 4.0)
    assert len(v.dmgVector) == 8, f"Expected 8 total hits at t=4.0, got {len(v.dmgVector)}"
    
    # Test manalock release at t=4.0
    # Apply Conduit level 0 (Innate 1.2x)
    buffs.Conduit(0, 1).performAbility("preCombat", 0, v)
    v.manaRegen.base = 10 # 5 mana per 0.5s tick
    v.nextMana = 4.0
    v.curMana = 0
    v.update(opponents, [], 4.05)
    assert abs(v.curMana - 6.0) < 0.001, f"Expected 6.0 mana after manalock, got {v.curMana}"
    
    # Verify no more ticks from the storm after 4.0
    # Between 4.5 and 5.0, Viktor should have performed at least one auto attack.
    v.update(opponents, [], 5.0)
    # 8 hits from storm + at least 1 from auto attack
    current_hits = len(v.dmgVector)
    assert current_hits > 8, f"Expected more than 8 hits after t=5.0 (storm + autos), got {current_hits}"
    
    # Verify attack lockout ends at 4.5
    v2 = champs.Viktor(level=1)
    v2.curMana = v2.fullMana.stat
    v2.update(opponents, [], 0)
    
    initial_atk_count = v2.numAttacks
    v2.update(opponents, [], 4.4)
    assert v2.numAttacks == initial_atk_count, f"Viktor attacked early at 4.4s, numAttacks={v2.numAttacks}"
    v2.update(opponents, [], 4.6)
    assert v2.numAttacks > initial_atk_count, "Viktor did not attack at 4.6s after castTime ended"
    
    print("Viktor Ability Passed!")
    
def test_viktor_reapplication():
    print("Testing Viktor Reapplication...")
    v = champs.Viktor(level=1)
    enemy1 = champs.DummyTank(level=1)
    enemy2 = champs.DummyTank(level=1)
    opponents = [enemy1, enemy2]
    
    # First cast at t=0
    v.curMana = v.fullMana.stat
    v.performAbility(opponents, [], 0)
    
    # Tick at 1.0, 2.0, 3.0, 4.0
    for t in [1.0, 2.0, 3.0, 4.0]:
        v.update(opponents, [], t)
    
    hits_after_first = len(v.dmgVector)
    assert hits_after_first == 8, f"Expected 8 hits after first storm, got {hits_after_first}"
    
    # Second cast at t=10.0
    v.curMana = v.fullMana.stat
    v.update(opponents, [], 10.0)
    
    # Tick at 11.0, 12.0, 13.0, 14.0
    for t in [11.0, 12.0, 13.0, 14.0]:
        v.update(opponents, [], t)
        
    hits_after_second = len(v.dmgVector)
    
    # We expect 17 hits: 8 magical (1st storm) + 1 physical (mandatory auto between casts) + 8 magical (2nd storm)
    magical_hits = [h for h in v.dmgVector if h[1][1] == "magical"]
    physical_hits = [h for h in v.dmgVector if h[1][1] == "physical"]
    
    assert len(magical_hits) == 16, f"Expected 16 magical hits, got {len(magical_hits)}"
    assert len(physical_hits) == 1, f"Expected 1 physical hit between casts, got {len(physical_hits)}"
    assert hits_after_second == 17, f"Expected 17 total hits, got {hits_after_second}"
    
    print("Viktor Reapplication Passed!")

if __name__ == "__main__":
    test_viktor_stats()
    test_viktor_ability()
    test_viktor_reapplication()
    print("\nAll Viktor tests passed!")
